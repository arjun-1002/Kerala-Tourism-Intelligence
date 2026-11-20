import os
import sys
from pathlib import Path
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect

# Ensure 12_Frontend is in path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from data_loader import load_all_datasets, get_destination_names, get_destination_record
from analysis import (
    TREND_PILLARS,
    build_google_trends_overview,
    canonical_master_destination,
    get_destination_trends_detail,
    normalize_trends_lookup,
)
from profitability import calculate_profitability, generate_cash_flow_projection, format_inr, BUSINESS_PRESETS
from recommendations import (
    VALID_VENTURE_PRESETS,
    build_cluster_means_lookup,
    build_enriched_recommendation,
    get_destination_recommendation,
    get_opportunity_tag,
)
from assistant import KeralaTourismAssistant
from marketplace import (
    get_all_ventures,
    get_venture_by_id,
    create_venture,
    record_pledge,
    calculate_commission,
    get_marketplace_kpis,
)

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Load datasets into memory on startup
data = load_all_datasets()
master_df = data["master_df"]

CATEGORY_CLEAN_MAP = {
    "High Gap + Positive Growth": "High Potential & Growing Demand",
    "High Gap + Negative Growth": "Undersupplied & Developing",
    "Low Gap + Positive Growth": "Established Market & Growing",
    "Low Gap + Negative Growth": "Mature & Well-Established",
}
if "Opportunity_Category" in master_df.columns:
    master_df["Opportunity_Category"] = master_df["Opportunity_Category"].map(lambda c: CATEGORY_CLEAN_MAP.get(c, c))

trends_df = data["trends_df"]
trends_overview = build_google_trends_overview(
    trends_df=trends_df,
    cat_summary_df=data.get("trends_cat_df", pd.DataFrame()),
    norm_cov_df=data.get("trends_norm_df", pd.DataFrame()),
    unresolved_df=data.get("trends_unresolved_df", pd.DataFrame()),
    master_df=master_df,
    raw_record_count=data.get("trends_raw_count", 0),
)

cluster_means_map = build_cluster_means_lookup(master_df)
_trends_avg_by_dest = {
    row["Destination"]: {
        "Destination Interest": row["Dest_Score"],
        "Accommodation": row["Accom_Score"],
        "Tourism Activities": row["Activity_Score"],
        "Food & Dining": row["Food_Score"],
    }
    for row in trends_overview.get("destination_matrix", [])
}

recommendations_map = {
    row["Destination"]: build_enriched_recommendation(
        row,
        cluster_means=cluster_means_map.get(row.get("Cluster_Name", ""), {}),
        trends_avg=_trends_avg_by_dest.get(row["Destination"]),
    )
    for row in master_df.to_dict(orient="records")
}

master_df["Primary_Concept"] = master_df["Destination"].map(lambda d: recommendations_map[d]["primary_concept"])
master_df["Primary_Sector"] = master_df["Destination"].map(lambda d: recommendations_map[d]["primary_sector"])
master_df["Secondary_Opportunity"] = master_df["Destination"].map(lambda d: recommendations_map[d]["secondary_label"])
master_df["Secondary_Sector"] = master_df["Destination"].map(lambda d: recommendations_map[d]["secondary_sector"])
master_df["Success_Rate"] = master_df["Destination"].map(lambda d: recommendations_map[d]["rank_1"]["success_rate"])
master_df["Rec_Urgency"] = master_df["Destination"].map(lambda d: recommendations_map[d]["urgency"])

# Initialize conversational AI assistant
ai_assistant = KeralaTourismAssistant(master_df, recommendations_map, trends_overview)


def get_clean_trend_series(dest_name: str, period: str = "3y") -> dict:
    """
    Aggregates monthly Google Trends scores cleanly per date for a destination,
    filtering to destination-level queries to avoid jagged multi-term overlapping spikes.
    """
    if trends_df.empty:
        return {
            "destination": dest_name,
            "dates": ["Jan '22", "Jun '22", "Jan '23", "Jun '23", "Jan '24", "Jun '24", "Dec '24"],
            "scores": [48, 62, 75, 68, 85, 78, 92],
        }

    lookup = normalize_trends_lookup(dest_name)
    sub = trends_df[trends_df["Destination"].astype(str).str.strip().str.lower() == lookup]

    if sub.empty:
        # Fallback: compute platform-wide monthly average so chart is never empty
        sub = trends_df

    if "Category" in sub.columns:
        dest_cat = sub[sub["Category"].astype(str).str.contains("destination", case=False, na=False)]
        if not dest_cat.empty:
            sub = dest_cat

    agg = (
        sub.groupby("Date", as_index=False)["Google_Trends_Score"]
        .max()
        .sort_values("Date")
    )

    if period == "1y":
        agg = agg.tail(12)
    elif period == "all":
        agg = agg.iloc[::4]
    else:
        # Default "3y": last 36 months sampled every 3 months for a smooth ~12-point trend curve
        agg = agg.tail(36).iloc[::3]

    try:
        dates = pd.to_datetime(agg["Date"]).dt.strftime("%b '%y").tolist()
    except Exception:
        dates = [str(d)[:7] for d in agg["Date"].tolist()]

    scores = [round(float(s), 1) for s in agg["Google_Trends_Score"].tolist()]

    return {
        "destination": dest_name,
        "dates": dates,
        "scores": scores,
    }

@app.context_processor
def inject_global_data():
    """Injects common destinations list across all Jinja2 templates."""
    return {
        "all_destinations": get_destination_names(master_df)
    }

# ==============================================================================
# ROUTE 1: HOME DASHBOARD (INSPIRED BY ATTACHED SCREENSHOT)
# ==============================================================================
@app.route("/")
def index():
    # High-level Platform KPIs
    total_destinations = len(master_df)
    total_footfall_2024 = int(master_df["Total_Visitors_2024"].sum())
    total_footfall_2022 = int(master_df["Total_Visitors_2022"].sum())
    overall_growth = ((total_footfall_2024 - total_footfall_2022) / total_footfall_2022) * 100 if total_footfall_2022 else 0

    total_hotels = int(master_df["Hotels"].sum())
    total_resorts = int(master_df["Resorts"].sum())
    total_homestays = int(master_df["Homestays_Vacation_Rentals"].sum())
    total_restaurants = int(master_df["Restaurants"].sum())
    commercial_supply = total_hotels + total_resorts + total_homestays + total_restaurants

    kpis = {
        "total_destinations": total_destinations,
        "total_footfall_2024": total_footfall_2024,
        "total_footfall_2022": total_footfall_2022,
        "overall_growth": overall_growth,
        "commercial_supply": commercial_supply,
        "total_hotels": total_hotels,
        "total_resorts": total_resorts,
        "total_homestays": total_homestays,
        "total_restaurants": total_restaurants
    }

    # Destination roster records
    dest_records = master_df[[
        "Destination", "District", "Landscape_Category", "Cluster", "Cluster_Name",
        "Latitude", "Longitude",
        "Total_Visitors_2024", "Growth_2022_2024", "Photo_URL", "Tagline",
        "Recommended_Business", "Primary_Concept", "Primary_Sector", "Opportunity_Score"
    ]].to_dict(orient="records")

    # Default spotlight destination is Munnar
    default_dest = master_df[master_df["Destination"] == "Munnar"].iloc[0].to_dict()

    # Initial trends for Munnar
    initial_trends = get_clean_trend_series("Munnar", "3y")

    # Top 5 destinations by footfall
    top_5 = master_df.sort_values("Total_Visitors_2024", ascending=False).head(5).to_dict(orient="records")

    # 4 Featured destinations
    featured = master_df[master_df["Destination"].isin(["Munnar", "Wayanad", "Alappuzha", "Varkala"])].to_dict(orient="records")

    return render_template(
        "index.html",
        kpis=kpis,
        destinations=dest_records,
        default_dest=default_dest,
        initial_trends=initial_trends,
        top_destinations=top_5,
        featured_destinations=featured
    )

# ==============================================================================
# ROUTE 2: EXPLORE DESTINATIONS
# ==============================================================================
@app.route("/destinations")
def destinations():
    search = request.args.get("search", "").strip()
    district = request.args.get("district", "All").strip()
    cluster = request.args.get("cluster", "All").strip()
    landscape = request.args.get("landscape", "All").strip()
    highlight = request.args.get("highlight", "").strip()

    filtered = master_df.copy()
    if search:
        filtered = filtered[filtered["Destination"].str.lower().str.contains(search.lower())]
    if district != "All":
        filtered = filtered[filtered["District"] == district]
    if cluster != "All":
        filtered = filtered[filtered["Cluster_Name"] == cluster]
    if landscape != "All":
        filtered = filtered[filtered["Landscape_Category"] == landscape]

    highlight_dest = None
    highlight_rec = None
    if highlight and highlight in master_df["Destination"].values:
        highlight_dest = master_df[master_df["Destination"] == highlight].iloc[0].to_dict()
        highlight_rec = recommendations_map.get(highlight)

    districts = sorted(master_df["District"].unique().tolist())

    all_destinations_ribbon = master_df.sort_values("Total_Visitors_2024", ascending=False)[[
        "Destination", "District", "Landscape_Category", "Photo_URL", "Total_Visitors_2024", "Growth_2022_2024"
    ]].to_dict(orient="records")

    return render_template(
        "destinations.html",
        destinations=filtered.to_dict(orient="records"),
        all_destinations_ribbon=all_destinations_ribbon,
        districts=districts,
        search_query=search,
        selected_district=district,
        selected_cluster=cluster,
        selected_landscape=landscape,
        highlight_dest=highlight_dest,
        highlight_rec=highlight_rec
    )

# ==============================================================================
# ROUTE 3: UNIFIED TOURISM & VISITOR ANALYSIS
# ==============================================================================
@app.route("/tourism-analysis")
def tourism_analysis():
    # Overall Footfall statistics (2022–2024)
    tot_2022 = int(master_df["Total_Visitors_2022"].sum())
    tot_2023 = int(master_df["Total_Visitors_2023"].sum())
    tot_2024 = int(master_df["Total_Visitors_2024"].sum())
    pct_change = ((tot_2024 - tot_2022) / tot_2022) * 100 if tot_2022 else 0

    # 3-Year growth ranking for all destinations
    ranked_growth = master_df.sort_values("Growth_2022_2024", ascending=True)
    growth_labels = ranked_growth["Destination"].tolist()
    growth_values = [round(float(v), 1) for v in ranked_growth["Growth_2022_2024"].tolist()]
    growth_colors = ["#154734" if v >= 0 else "#9f1239" for v in growth_values]

    # Domestic vs foreign split for top 8 international gateways
    top_intl = master_df.sort_values("Foreign_Visitors_2024", ascending=False).head(8)
    dom_for_labels = top_intl["Destination"].tolist()
    dom_values = [int(v) for v in top_intl["Domestic_Visitors_2024"].tolist()]
    for_values = [int(v) for v in top_intl["Foreign_Visitors_2024"].tolist()]

    # Aggregate commercial hospitality supply by district for top 7 districts
    dist_supply = master_df.groupby("District")[["Hotels", "Resorts", "Homestays_Vacation_Rentals", "Restaurants"]].sum()
    dist_supply["Total"] = dist_supply.sum(axis=1)
    dist_top = dist_supply.sort_values("Total", ascending=False).head(7).reset_index()

    district_data = {
        "labels": dist_top["District"].tolist(),
        "hotels": dist_top["Hotels"].tolist(),
        "resorts": dist_top["Resorts"].tolist(),
        "homestays": dist_top["Homestays_Vacation_Rentals"].tolist(),
        "restaurants": dist_top["Restaurants"].tolist()
    }

    # Hospitality rating averages across lodging & dining
    rating_cols = ["Hotels_Average_Rating", "Resorts_Average_Rating", "Homestays_Average_Rating", "Restaurants_Average_Rating"]
    avg_ratings = [round(float(master_df[c].mean()), 2) for c in rating_cols]

    # Commercial hospitality supply totals
    total_hotels = int(master_df["Hotels"].sum())
    total_resorts = int(master_df["Resorts"].sum())
    total_homestays = int(master_df["Homestays_Vacation_Rentals"].sum())
    total_restaurants = int(master_df["Restaurants"].sum())
    total_venues = total_hotels + total_resorts + total_homestays + total_restaurants

    # Fastest growing destination
    top_grower = master_df.sort_values("Growth_2022_2024", ascending=False).iloc[0].to_dict()

    districts = sorted(master_df["District"].unique().tolist())

    return render_template(
        "tourism_analysis.html",
        tot_2022=tot_2022,
        tot_2023=tot_2023,
        tot_2024=tot_2024,
        pct_change=pct_change,
        destinations=master_df.to_dict(orient="records"),
        growth_labels=growth_labels,
        growth_values=growth_values,
        growth_colors=growth_colors,
        dom_for_labels=dom_for_labels,
        dom_values=dom_values,
        for_values=for_values,
        district_data=district_data,
        avg_ratings=avg_ratings,
        total_hotels=total_hotels,
        total_resorts=total_resorts,
        total_homestays=total_homestays,
        total_restaurants=total_restaurants,
        total_venues=total_venues,
        top_grower=top_grower,
        districts=districts
    )

# ==============================================================================
# ROUTE 4: DESTINATION REGIONAL PROFILES
# ==============================================================================
@app.route("/clustering")
def clustering():
    return render_template(
        "clustering.html",
        destinations=master_df.to_dict(orient="records")
    )

# ==============================================================================
# ROUTE 5: BUSINESS OPPORTUNITY ANALYSIS
# ==============================================================================
@app.route("/opportunities")
def opportunities():
    ranked = master_df.sort_values("Overall_Gap_Score", ascending=False)
    top_10 = ranked.head(10)

    top_gap_labels = top_10["Destination"].tolist()
    top_gap_values = [round(float(v), 1) for v in top_10["Overall_Gap_Score"].tolist()]

    ranked_records = ranked.to_dict(orient="records")
    default_brief_dest = request.args.get("destination", "").strip()
    if default_brief_dest not in recommendations_map:
        default_brief_dest = ranked_records[0]["Destination"] if ranked_records else "Kozhikode City"

    return render_template(
        "opportunities.html",
        ranking=ranked_records,
        top_gap_labels=top_gap_labels,
        top_gap_values=top_gap_values,
        recommendations_map=recommendations_map,
        default_brief_dest=default_brief_dest,
        default_rec=recommendations_map.get(default_brief_dest),
    )

# ==============================================================================
# ROUTE 6: PROFITABILITY CALCULATOR
# ==============================================================================
@app.route("/calculator")
def calculator():
    dest_param = request.args.get("destination", "Kumarakom").strip()
    if dest_param not in master_df["Destination"].values:
        dest_param = "Kumarakom"

    dest_row = master_df[master_df["Destination"] == dest_param].iloc[0].to_dict()
    default_rec = recommendations_map.get(dest_param, {})

    venture_param = request.args.get("venture", "").strip()
    if venture_param not in VALID_VENTURE_PRESETS:
        venture_param = default_rec.get("primary_sector", "Homestay")
        if venture_param not in VALID_VENTURE_PRESETS:
            venture_param = "Homestay"

    return render_template(
        "calculator.html",
        destinations=master_df.to_dict(orient="records"),
        default_dest_name=dest_param,
        default_dest=dest_row,
        default_rec=default_rec,
        default_venture=venture_param,
    )

# ==============================================================================
# ROUTE 7: DESTINATION COMPARISON
# ==============================================================================
@app.route("/comparison")
def comparison():
    dest1_name = request.args.get("dest1", "Munnar").strip()
    dest2_name = request.args.get("dest2", "Wayanad").strip()

    if dest1_name not in master_df["Destination"].values:
        dest1_name = "Munnar"
    if dest2_name not in master_df["Destination"].values or dest2_name == dest1_name:
        dest2_name = "Wayanad" if dest1_name != "Wayanad" else "Vagamon"

    d1 = master_df[master_df["Destination"] == dest1_name].iloc[0].to_dict()
    d2 = master_df[master_df["Destination"] == dest2_name].iloc[0].to_dict()
    rec1 = recommendations_map.get(dest1_name)
    rec2 = recommendations_map.get(dest2_name)

    return render_template(
        "comparison.html",
        destinations=master_df.to_dict(orient="records"),
        dest1=d1,
        dest2=d2,
        rec1=rec1,
        rec2=rec2
    )

# ==============================================================================
# ROUTE 8: VISITOR GROWTH (UNIFIED UNDER TOURISM ANALYSIS)
# ==============================================================================
@app.route("/visitor-growth")
def visitor_growth():
    return redirect("/tourism-analysis")

# ==============================================================================
# ROUTE 9: KERALA CULTURE GUIDE
# ==============================================================================
@app.route("/culture-guide")
def culture_guide():
    return render_template("culture_guide.html")

# ==============================================================================
# ROUTE 10: GOOGLE TRENDS ANALYSIS
# ==============================================================================
@app.route("/google-trends")
def google_trends():
    selected_dest = request.args.get("destination", "Munnar").strip()
    canonical = canonical_master_destination(selected_dest)
    valid_dests = get_destination_names(master_df)
    if canonical not in valid_dests:
        canonical = "Munnar" if "Munnar" in valid_dests else (valid_dests[0] if valid_dests else "Munnar")

    initial_detail = get_destination_trends_detail(trends_df, canonical, pillar="All", period="3y")

    return render_template(
        "google_trends.html",
        overview=trends_overview,
        initial_detail=initial_detail,
        selected_dest=canonical,
        pillars=TREND_PILLARS,
    )

# ==============================================================================
# ROUTE 11: VENTURE MARKETPLACE & INVESTOR CONNECT
# ==============================================================================
@app.route("/invest")
def invest():
    selected_dest = request.args.get("destination", "All").strip()
    selected_cat = request.args.get("category", "All").strip()

    ventures = get_all_ventures(destination=selected_dest, category=selected_cat)
    kpis = get_marketplace_kpis()
    destinations = ["All"] + sorted(master_df["Destination"].unique().tolist())
    categories = [
        "All",
        "Boutique Homestay",
        "Eco-Resort & Wellness",
        "Houseboat Cruise",
        "Experiential Cafe & Wellness",
        "Adventure Tourism"
    ]

    return render_template(
        "invest.html",
        ventures=ventures,
        kpis=kpis,
        destinations=destinations,
        categories=categories,
        selected_dest=selected_dest,
        selected_cat=selected_cat,
        active_page="invest"
    )

# ==============================================================================
# ROUTE 12: ABOUT PROJECT
# ==============================================================================
@app.route("/about")
def about():
    return render_template("about.html")

# ==============================================================================
# REST API ENDPOINTS FOR CLIENT-SIDE JAVASCRIPT
# ==============================================================================
def _sanitize_json_value(value):
    if isinstance(value, (list, tuple)):
        return [_sanitize_json_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _sanitize_json_value(v) for k, v in value.items()}
    if hasattr(value, "item"):
        value = value.item()
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


@app.route("/api/destination/<name>")
def api_destination(name):
    """Returns single destination record with metadata and enriched recommendations."""
    record = get_destination_record(master_df, name)
    if not record:
        return jsonify({"error": "Destination not found"}), 404
    record["Recommendation"] = recommendations_map.get(record["Destination"], {})
    return jsonify(_sanitize_json_value(record))

@app.route("/api/trends/<path:name>")
def api_trends(name):
    """Returns monthly Google Trends time series for Chart.js line graph."""
    period = request.args.get("period", "3y")
    return jsonify(get_clean_trend_series(name, period=period))

@app.route("/api/google-trends/<path:name>")
def api_google_trends_detail(name):
    """Returns multi-pillar monthly time series and keyword breakdown for Google Trends Explorer."""
    pillar = request.args.get("pillar", "All").strip()
    period = request.args.get("period", "3y").strip()
    detail = get_destination_trends_detail(trends_df, name, pillar=pillar, period=period)
    return jsonify(_sanitize_json_value(detail))

@app.route("/api/calculate-profitability", methods=["POST"])
def api_calculate():
    """Calculates profitability metrics and 5-year cash flow projections."""
    req = request.get_json() or {}
    inv = float(req.get("investment", 2500000))
    rev = float(req.get("monthly_revenue", 160000))
    exp = float(req.get("monthly_expenses", 75000))

    res = calculate_profitability(inv, rev, exp)
    cf_df = generate_cash_flow_projection(inv, res["monthly_profit"], years=5)
    res["cash_flows"] = cf_df.to_dict(orient="records")

    return jsonify(res)

# ==============================================================================
# ROUTE 12: CONVERSATIONAL AI ASSISTANT API
# ==============================================================================
@app.route("/api/assistant/suggestions", methods=["GET"])
def api_assistant_suggestions():
    """Returns curated starter prompts for the AI travel & business concierge."""
    return jsonify({"suggestions": ai_assistant.get_suggestions()})

@app.route("/api/assistant/chat", methods=["POST"])
def api_assistant_chat():
    """Processes conversational questions and returns grounded intelligence responses."""
    payload = request.get_json() or {}
    message = payload.get("message", "").strip()
    history = payload.get("history", [])

    if not message:
        return jsonify({
            "reply": "Please ask a question about destinations, business ventures, or travel in Kerala.",
            "suggestions": ai_assistant.get_suggestions()[:4]
        })

    response = ai_assistant.answer_query(message, conversation_history=history)
    return jsonify(response)

# ==============================================================================
# ROUTE 13: VENTURE MARKETPLACE REST APIS
# ==============================================================================
@app.route("/api/ventures/calculate-commission", methods=["GET"])
def api_venture_calculate_commission():
    """Calculates live platform fee breakdown and net deployed capital."""
    try:
        amount = float(request.args.get("amount", 500000))
    except (ValueError, TypeError):
        amount = 500000.0
    return jsonify(calculate_commission(amount))

@app.route("/api/ventures/pledge", methods=["POST"])
def api_venture_pledge():
    """Records investor pledge with automatic platform commission split."""
    payload = request.get_json() or {}
    v_id = payload.get("venture_id")
    name = payload.get("investor_name")
    email = payload.get("investor_email")
    notes = payload.get("notes", "")
    is_nri = bool(payload.get("is_nri", False))

    try:
        amt = float(payload.get("amount", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid investment amount"}), 400

    if not v_id or not name or not email or amt <= 0:
        return jsonify({"error": "Please provide your name, email, and a valid pledge amount."}), 400

    try:
        result = record_pledge(v_id, name, email, amt, is_nri=is_nri, notes=notes)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/api/ventures/submit", methods=["POST"])
def api_venture_submit():
    """Receives new venture proposals from entrepreneurs and hosts."""
    payload = request.get_json() or {}
    if not payload.get("title") or not payload.get("destination"):
        return jsonify({"error": "Venture title and destination are required"}), 400

    try:
        new_v = create_venture(payload, master_df=master_df)
        return jsonify({"success": True, "venture": new_v})
    except Exception as e:
        return jsonify({"error": f"Submission failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
