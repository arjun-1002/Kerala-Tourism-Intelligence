from typing import Any, Dict, List, Optional
import pandas as pd


OPPORTUNITY_METADATA = {
    "High Potential & Growing Demand": {
        "label": "High Potential & Growing Demand",
        "badge_class": "badge-emerald",
        "color": "#154734",
        "description": "Rapidly rising traveler demand combined with limited local stays and dining. Outstanding potential to launch quality new hospitality ventures.",
        "urgency": "Top Growth Opportunity",
    },
    "Undersupplied & Developing": {
        "label": "Undersupplied & Developing",
        "badge_class": "badge-amber",
        "color": "#b8922a",
        "description": "Underserved local market with steady or developing footfall. Ideal for boutique, low-overhead stays or unique dining concepts that build loyal repeat visitors.",
        "urgency": "Boutique / Selective Entry",
    },
    "Established Market & Growing": {
        "label": "Established Market & Growing",
        "badge_class": "badge-blue",
        "color": "#2b6cb0",
        "description": "A popular, fast-growing destination with an established hospitality presence. Best suited for standout culinary spots, specialty cafes, or differentiated luxury stays.",
        "urgency": "Premium & Niche Concepts",
    },
    "Mature & Well-Established": {
        "label": "Mature & Well-Established",
        "badge_class": "badge-rose",
        "color": "#9f1239",
        "description": "A mature, well-known destination with ample existing rooms. Rather than adding standard inventory, the focus is on upgrading guest experiences, eco-wellness, and heritage revitalization.",
        "urgency": "Reposition & Experience Upgrade",
    },
    # Raw keys mapping for backwards compatibility
    "High Gap + Positive Growth": {
        "label": "High Potential & Growing Demand",
        "badge_class": "badge-emerald",
        "color": "#154734",
        "description": "Rapidly rising traveler demand combined with limited local stays and dining. Outstanding potential to launch quality new hospitality ventures.",
        "urgency": "Top Growth Opportunity",
    },
    "High Gap + Negative Growth": {
        "label": "Undersupplied & Developing",
        "badge_class": "badge-amber",
        "color": "#b8922a",
        "description": "Underserved local market with steady or developing footfall. Ideal for boutique, low-overhead stays or unique dining concepts that build loyal repeat visitors.",
        "urgency": "Boutique / Selective Entry",
    },
    "Low Gap + Positive Growth": {
        "label": "Established Market & Growing",
        "badge_class": "badge-blue",
        "color": "#2b6cb0",
        "description": "A popular, fast-growing destination with an established hospitality presence. Best suited for standout culinary spots, specialty cafes, or differentiated luxury stays.",
        "urgency": "Premium & Niche Concepts",
    },
    "Low Gap + Negative Growth": {
        "label": "Mature & Well-Established",
        "badge_class": "badge-rose",
        "color": "#9f1239",
        "description": "A mature, well-known destination with ample existing rooms. Rather than adding standard inventory, the focus is on upgrading guest experiences, eco-wellness, and heritage revitalization.",
        "urgency": "Reposition & Experience Upgrade",
    },
}

SECTOR_SPECS = [
    {
        "key": "Hotel",
        "label": "Hotels",
        "count_col": "Hotels",
        "gap_col": "Hotels_Gap",
        "rating_col": "Hotels_Average_Rating",
    },
    {
        "key": "Resort",
        "label": "Resorts",
        "count_col": "Resorts",
        "gap_col": "Resorts_Gap",
        "rating_col": "Resorts_Average_Rating",
    },
    {
        "key": "Homestay",
        "label": "Homestays",
        "count_col": "Homestays_Vacation_Rentals",
        "gap_col": "Homestays_Vacation_Rentals_Gap",
        "rating_col": "Homestays_Average_Rating",
    },
    {
        "key": "Restaurant",
        "label": "Restaurants",
        "count_col": "Restaurants",
        "gap_col": "Restaurants_Gap",
        "rating_col": "Restaurants_Average_Rating",
    },
]

VALID_VENTURE_PRESETS = {"Hotel", "Resort", "Homestay", "Restaurant"}

CONCEPT_MAP = {
    ("Homestay", "Hills"): "Boutique Hill Homestay & Eco-Cottages",
    ("Homestay", "Coastal"): "Managed Coastal Homestay & Beach Villas",
    ("Homestay", "Backwaters"): "Responsible Backwater Homestay",
    ("Homestay", "Urban"): "Serviced Urban Boutique Stay",
    ("Restaurant", "Hills"): "Highland View Cafe & Multi-Cuisine Dining",
    ("Restaurant", "Coastal"): "Specialty Seafood & Cliffside Bistro",
    ("Restaurant", "Backwaters"): "Lakeside Dining & Traditional Culinary Hub",
    ("Restaurant", "Urban"): "Destination Dining & Specialty Cafe",
    ("Resort", "Hills"): "Boutique Eco-Resort & Nature Retreat",
    ("Resort", "Coastal"): "Coastal Wellness & Boutique Beach Resort",
    ("Resort", "Backwaters"): "Waterfront Experiential Retreat",
    ("Resort", "Urban"): "Urban Business & Wellness Resort",
    ("Hotel", "Hills"): "Mid-Scale Highland Transit Hotel",
    ("Hotel", "Coastal"): "Boutique Coastal Leisure Hotel",
    ("Hotel", "Backwaters"): "Backwater Heritage Hotel",
    ("Hotel", "Urban"): "Business & Transit City Hotel",
}


def get_opportunity_tag(category: str) -> Dict[str, Any]:
    """Returns editorial badge styling and urgency classification for an opportunity quadrant."""
    return OPPORTUNITY_METADATA.get(category, {
        "badge_class": "badge-neutral",
        "color": "#5f6c64",
        "description": "Standard market monitoring.",
        "urgency": "Steady Market",
    })


def build_cluster_means_lookup(master_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Computes cluster-level mean counts and ratings across the 25 benchmark destinations."""
    if master_df.empty or "Cluster_Name" not in master_df.columns:
        return {}

    agg_cols = [
        "Hotels", "Resorts", "Homestays_Vacation_Rentals", "Restaurants",
        "Hotels_Average_Rating", "Resorts_Average_Rating",
        "Homestays_Average_Rating", "Restaurants_Average_Rating",
    ]
    present = [c for c in agg_cols if c in master_df.columns]
    grouped = master_df.groupby("Cluster_Name")[present].mean()
    return {
        cluster: {col: round(float(val), 1) for col, val in row.items()}
        for cluster, row in grouped.iterrows()
    }


def _compute_sector_breakdown(
    row: Dict[str, Any],
    cluster_means: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Computes recorded count, cluster peer mean, cluster gap, and rating per sector."""
    breakdown = []
    for spec in SECTOR_SPECS:
        count = int(row.get(spec["count_col"], 0) or 0)
        c_mean = float(cluster_means.get(spec["count_col"], count))
        c_gap = round(c_mean - count, 1)
        s_gap = round(float(row.get(spec["gap_col"], 0.0) or 0.0), 1)
        rating = round(float(row.get(spec["rating_col"], 0.0) or 0.0), 1)
        breakdown.append({
            "key": spec["key"],
            "label": spec["label"],
            "count": count,
            "cluster_mean": round(c_mean, 1),
            "cluster_gap": c_gap,
            "state_gap": s_gap,
            "rating": rating,
            "is_zero": count == 0,
        })
    return breakdown


def _select_primary_and_secondary(
    row: Dict[str, Any],
    sectors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Resolves actionable primary/secondary sectors and tailors concepts using real supply & quality gaps."""
    baseline = str(row.get("Recommended_Business", "Homestay")).strip()
    opp_cat = str(row.get("Opportunity_Category", "Low Gap + Positive Growth"))
    landscape = str(row.get("Landscape_Category", "Hills"))
    growth = float(row.get("Growth_2022_2024", 0.0) or 0.0)
    cafes = int(row.get("Cafes_Tea_Rooms", 0) or 0)

    # Sort sectors by strongest deficit first (tie-breaking on zero recorded supply)
    ranked_sectors = sorted(
        sectors,
        key=lambda s: (s["cluster_gap"] + (15.0 if s["is_zero"] else 0.0)),
        reverse=True,
    )
    lowest_rated_sector = min(sectors, key=lambda s: s["rating"] if s["rating"] > 0 else 5.0)

    if baseline in VALID_VENTURE_PRESETS:
        primary_sector = baseline
        # Refine hubs where zero cafes or zero homestays reveal sharper positioning
        if primary_sector == "Restaurant" and cafes == 0:
            primary_concept = f"Destination Dining & Heritage Cafe ({landscape})"
        elif primary_sector == "Homestay" and any(s["key"] == "Homestay" and s["is_zero"] for s in sectors):
            base_concept = CONCEPT_MAP.get(("Homestay", landscape), "Boutique Homestay")
            primary_concept = f"First-Mover {base_concept}"
        else:
            primary_concept = CONCEPT_MAP.get((primary_sector, landscape), f"{primary_sector} Venture")
    else:
        # Handle hubs with mature room supply constructively (Munnar, Alappuzha, Wayanad)
        primary_sector = lowest_rated_sector["key"] if lowest_rated_sector["rating"] <= 4.0 else "Restaurant"
        if growth > 0:
            primary_concept = "Signature Experiential Dining & Artisan Cafe"
        else:
            primary_concept = f"Premium Experience Repositioning: {lowest_rated_sector['label']}"

    # Determine secondary concrete sector opportunity (excluding the chosen primary sector)
    sec_candidates = [s for s in ranked_sectors if s["key"] != primary_sector]
    sec = sec_candidates[0] if sec_candidates else ranked_sectors[0]

    # Prefer highlighting unserved sectors explicitly when present
    zero_others = [s for s in sec_candidates if s["is_zero"]]
    if zero_others:
        sec = zero_others[0]
        secondary_label = f"Unserved {sec['label']} (0 currently open vs. {sec['cluster_mean']:.0f} avg in similar destinations)"
    elif sec["cluster_gap"] > 0:
        secondary_label = f"{sec['label']} expansion (+{sec['cluster_gap']:.0f} additional needed)"
    else:
        secondary_label = f"Quality upgrade in {sec['label']} (current rating: {sec['rating']:.1f}/5)"

    # Determine tertiary concrete sector opportunity (excluding primary and secondary)
    tert_candidates = [s for s in sec_candidates if s["key"] != sec["key"]]
    tert = tert_candidates[0] if tert_candidates else (sec_candidates[1] if len(sec_candidates) > 1 else ranked_sectors[-1])

    zero_terts = [s for s in tert_candidates if s["is_zero"]]
    if zero_terts:
        tert = zero_terts[0]
        tertiary_label = f"Unserved {tert['label']} (0 currently open)"
    elif tert["cluster_gap"] > 0:
        tertiary_label = f"{tert['label']} expansion (+{tert['cluster_gap']:.0f} additional needed)"
    else:
        tertiary_label = f"Quality upgrade in {tert['label']} ({tert['rating']:.1f}/5)"

    return {
        "primary_sector": primary_sector,
        "primary_concept": primary_concept,
        "secondary_sector": sec["key"],
        "secondary_label": secondary_label,
        "tertiary_sector": tert["key"],
        "tertiary_label": tertiary_label,
        "lowest_rated": lowest_rated_sector,
        "top_cluster_gap_sector": ranked_sectors[0],
        "hold_capacity": baseline not in VALID_VENTURE_PRESETS and growth <= 0,
    }


def _compute_success_rate(rank: int, sector_spec: Dict[str, Any], growth: float, gap_score: float) -> int:
    """Computes a grounded success rate percentage (70%-96%) reflecting footfall growth and sector gaps."""
    if rank == 1:
        score = 90
    elif rank == 2:
        score = 83
    else:
        score = 76

    if growth > 50.0:
        score += 4
    elif growth > 15.0:
        score += 2
    elif growth > 0.0:
        score += 1
    elif growth < -20.0:
        score -= 4
    else:
        score -= 2

    c_gap = float(sector_spec.get("cluster_gap", 0.0) or 0.0)
    if sector_spec.get("is_zero", False):
        score += 4
    elif c_gap > 3.0:
        score += 2
    elif c_gap < -10.0:
        score -= 2

    rating = float(sector_spec.get("rating", 4.0) or 4.0)
    if 0 < rating <= 3.8:
        score += 2
    elif rating >= 4.6:
        score -= 1

    if rank == 1:
        return max(88, min(96, score))
    elif rank == 2:
        return max(80, min(89, score))
    else:
        return max(70, min(81, score))


def build_enriched_recommendation(
    row: Dict[str, Any],
    cluster_means: Optional[Dict[str, float]] = None,
    trends_avg: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Builds a multi-factor investment & concept recommendation from supply benchmarks, traveler ratings, trends, and transit."""
    dest = str(row.get("Destination", ""))
    district = str(row.get("District", ""))
    cluster = str(row.get("Cluster_Name", ""))
    landscape = str(row.get("Landscape_Category", "Nature"))
    gap_score = round(float(row.get("Overall_Gap_Score", 0.0) or 0.0), 1)
    growth = round(float(row.get("Growth_2022_2024", 0.0) or 0.0), 1)
    visitors_2024 = int(row.get("Total_Visitors_2024", 0) or 0)
    opp_cat = str(row.get("Opportunity_Category", "Low Gap + Positive Growth"))
    baseline = str(row.get("Recommended_Business", "Homestay")).strip()
    data_quality = str(row.get("Data_Quality", "Official records"))
    airport_km = round(float(row.get("Nearest_Airport_Distance_km_numeric", 0.0) or 0.0), 0)
    cafes = int(row.get("Cafes_Tea_Rooms", 0) or 0)
    attractions = int(row.get("Attraction_Count", 0) or 0)

    opp_info = get_opportunity_tag(opp_cat)
    c_means = cluster_means or {}
    sectors = _compute_sector_breakdown(row, c_means)
    picks = _select_primary_and_secondary(row, sectors)

    primary_sector = picks["primary_sector"]
    primary_spec = next((s for s in sectors if s["key"] == primary_sector), sectors[0])

    total_stays = int(row.get("Hotels", 0) or 0) + int(row.get("Resorts", 0) or 0) + int(row.get("Homestays_Vacation_Rentals", 0) or 0)
    dining_count = int(row.get("Restaurants", 0) or 0)

    # Build grounded, humanized advisory rationale
    if picks["hold_capacity"]:
        rationale = (
            f"{dest} already has abundant hospitality options ({total_stays} registered stays) compared to similar getaways, while recent "
            f"traveler traffic eased by {abs(growth):.1f}%. Rather than adding standard rooms, smart investors should "
            f"focus on {picks['primary_concept'].lower()}, elevating guest experiences where local ratings currently average {picks['lowest_rated']['rating']:.1f}/5."
        )
    elif baseline not in VALID_VENTURE_PRESETS and growth > 0:
        rationale = (
            f"{dest} already offers an established hospitality base ({total_stays} accommodations and {dining_count} dining spots) "
            f"alongside booming traveler arrivals ({growth:+.1f}% to {visitors_2024:,} visitors). New ventures will thrive "
            f"by introducing distinctive experiential dining, artisanal cafes, and curated activities rather than basic lodging, especially with local {picks['lowest_rated']['label'].lower()} ratings averaging {picks['lowest_rated']['rating']:.1f}/5."
        )
    elif gap_score > 0 and growth > 0:
        rationale = (
            f"{dest} combines strong market room for new venues (+{gap_score:.1f} opportunity index) with {growth:+.1f}% "
            f"visitor growth over the past 3 years. The standout opportunity is {picks['primary_concept']} ({primary_spec['count']} currently open vs. {primary_spec['cluster_mean']:.1f} "
            f"average in similar destinations), complemented by clear headroom in {picks['secondary_label']}."
        )
    elif gap_score > 0 and growth <= 0:
        rationale = (
            f"{dest} has significantly fewer stays and dining options than peer destinations (+{gap_score:.1f} opportunity index). "
            f"With traveler traffic fluctuating ({growth:+.1f}%), operators should start with flexible, low-overhead {picks['primary_concept']} formats that sustainably build repeat visitors."
        )
    else:
        rationale = (
            f"{dest} is a vibrant and competitive destination within {cluster}. With strong traveler demand (+{growth:.1f}% growth), "
            f"high-potential openings exist for standout concepts such as {picks['primary_concept']} and {picks['secondary_label']}."
        )

    # Construct 3 concrete, data-backed human action bullets
    zero_list = [s["label"] for s in sectors if s["is_zero"]]
    if zero_list:
        bullet_format = (
            f"No registered options currently exist in {', '.join(zero_list)}. Launching a thoughtfully designed {picks['primary_concept']} "
            f"gives you uncontested first-mover advantage and immediate local recognition."
        )
    elif cafes == 0:
        bullet_format = (
            f"With {attractions} mapped tourist spots and zero dedicated cafes or tea lounges, pairing artisanal refreshments "
            f"with your {primary_sector.lower()} will easily capture high daytime footfall."
        )
    else:
        bullet_format = (
            f"Establish a memorable {picks['primary_concept']} (currently {primary_spec['count']} local venues, rated {primary_spec['rating']:.1f}/5) "
            f"and complement it with {picks['secondary_label']}."
        )

    bullet_quality = (
        f"Guest satisfaction benchmark: Local {picks['lowest_rated']['label'].lower()} currently average {picks['lowest_rated']['rating']:.1f}/5 "
        f"in traveler reviews, leaving plenty of room for a high-service operator to stand out and command premium rates."
    )

    if trends_avg and trends_avg.get("Food & Dining", 0.0) == 0.0:
        trends_note = "Travelers search for the destination itself before specific dining brands, meaning great on-ground visibility and word-of-mouth will win visitors."
    elif trends_avg:
        top_t_pillar = max(trends_avg, key=lambda k: trends_avg[k])
        trends_note = f"Online traveler interest is strongest for {top_t_pillar.lower()} ({trends_avg[top_t_pillar]:.1f} relative search volume)."
    else:
        trends_note = f"Conveniently accessible ({int(airport_km)} km from nearest airport) along key {district} travel routes."

    if "Contains estimates" in data_quality:
        bullet_risk = f"Planning tip: Historical visitor figures include provisional regional estimates; confirm weekend traffic patterns on-site. {trends_note}"
    elif airport_km >= 90:
        bullet_risk = f"Traveler profile: Located {int(airport_km)} km from the nearest airport — tailor your offering for road-trippers, scenic weekenders, and nature lovers. {trends_note}"
    else:
        bullet_risk = f"Verified traveler traffic ({visitors_2024:,} annual visitors in 2024). {trends_note}"

    # User-friendly quick-scan signal pills
    risk_flags = []
    if "Contains estimates" in data_quality:
        risk_flags.append({"label": "Provisional Visitor Data", "class": "badge-amber"})
    else:
        risk_flags.append({"label": "Verified Tourism Records", "class": "badge-emerald"})

    if zero_list:
        risk_flags.append({"label": f"Unserved: {', '.join(zero_list)}", "class": "badge-blue"})
    if picks["hold_capacity"]:
        risk_flags.append({"label": "Consolidating Footfall", "class": "badge-rose"})
    if picks["lowest_rated"]["rating"] <= 3.8:
        risk_flags.append({"label": f"Quality Headroom: {picks['lowest_rated']['label']} ({picks['lowest_rated']['rating']:.1f}/5.0)", "class": "badge-amber"})
    if airport_km >= 90:
        risk_flags.append({"label": f"{int(airport_km)} km to Airport", "class": "badge-neutral"})

    # Build 3 ranked recommendations with data-calibrated success rates
    ranked_recs = []

    # Rank 1: Primary Recommendation
    r1_rate = _compute_success_rate(1, primary_spec, growth, gap_score)
    r1_demand = f"+{growth:.1f}% Footfall Surge" if growth >= 0 else "Quality Experience Gap"
    r1_summary = (
        f"{dest} traveler footfall ({visitors_2024:,} annual visitors) and local "
        f"{picks['lowest_rated']['label'].lower()} ratings ({picks['lowest_rated']['rating']:.1f}/5.0) create peak market demand for this concept."
    )
    ranked_recs.append({
        "rank": 1,
        "badge": "Rank 1 · Top Pick",
        "badge_class": "badge-emerald",
        "border_color": "var(--forest)",
        "accent_bg": "#eaf5ea",
        "rate_color": "#15803d",
        "title": picks["primary_concept"],
        "sector": primary_sector,
        "success_rate": r1_rate,
        "demand_driver": r1_demand,
        "summary": r1_summary,
        "market_need": f"{primary_spec['count']} venues currently active",
        "calc_link": f"/calculator?destination={dest}&venture={primary_sector}",
    })

    # Rank 2: Secondary Recommendation (Strong Alternative)
    sec_spec = next((s for s in sectors if s["key"] == picks["secondary_sector"]), sectors[1] if len(sectors) > 1 else sectors[0])
    r2_rate = _compute_success_rate(2, sec_spec, growth, gap_score)
    r2_concept = CONCEPT_MAP.get((picks["secondary_sector"], landscape), f"{sec_spec['label']} Venture")
    r2_demand = picks["secondary_label"]
    if sec_spec["is_zero"]:
        r2_summary = f"Zero registered {sec_spec['label'].lower()} currently open in {dest}. Launching here gives uncontested first-mover advantage."
    elif sec_spec["cluster_gap"] > 0:
        r2_summary = f"Strong supply gap with {sec_spec['cluster_gap']:.0f} additional venues needed compared to peer destinations to meet peak demand."
    else:
        r2_summary = f"High traveler traffic makes upgraded, distinctive {sec_spec['label'].lower()} a resilient investment with rapid payback."

    ranked_recs.append({
        "rank": 2,
        "badge": "Rank 2 · Alternative",
        "badge_class": "badge-blue",
        "border_color": "#2563eb",
        "accent_bg": "#eff6ff",
        "rate_color": "#1d4ed8",
        "title": r2_concept,
        "sector": picks["secondary_sector"],
        "success_rate": r2_rate,
        "demand_driver": r2_demand,
        "summary": r2_summary,
        "market_need": f"{sec_spec['count']} venues currently active",
        "calc_link": f"/calculator?destination={dest}&venture={picks['secondary_sector']}",
    })

    # Rank 3: Tertiary Recommendation (Emerging Opportunity)
    tert_spec = next((s for s in sectors if s["key"] == picks["tertiary_sector"]), sectors[2] if len(sectors) > 2 else sectors[-1])
    r3_rate = _compute_success_rate(3, tert_spec, growth, gap_score)
    r3_concept = CONCEPT_MAP.get((picks["tertiary_sector"], landscape), f"{tert_spec['label']} Opportunity")
    r3_demand = picks["tertiary_label"]
    if tert_spec["is_zero"]:
        r3_summary = f"Unserved sector with 0 registered venues in {dest}. Captures untapped visitor segments seeking specialized hospitality."
    elif tert_spec["cluster_gap"] > 0:
        r3_summary = f"Clear room for expansion (+{tert_spec['cluster_gap']:.0f} additional needed) to cater to scenic weekenders and travelers."
    else:
        r3_summary = f"Low-overhead model with flexible operations, catering to budget-conscious and experiential travelers."

    ranked_recs.append({
        "rank": 3,
        "badge": "Rank 3 · Emerging",
        "badge_class": "badge-amber",
        "border_color": "#d97706",
        "accent_bg": "#fefce8",
        "rate_color": "#b45309",
        "title": r3_concept,
        "sector": picks["tertiary_sector"],
        "success_rate": r3_rate,
        "demand_driver": r3_demand,
        "summary": r3_summary,
        "market_need": f"{tert_spec['count']} venues currently active",
        "calc_link": f"/calculator?destination={dest}&venture={picks['tertiary_sector']}",
    })

    return {
        "destination": dest,
        "district": district,
        "cluster": cluster,
        "landscape": landscape,
        "gap_score": gap_score,
        "growth": growth,
        "visitors_2024": visitors_2024,
        "category": opp_info.get("label", opp_cat),
        "badge_class": opp_info["badge_class"],
        "urgency": opp_info["urgency"],
        "color": opp_info["color"],
        "model_baseline": baseline,
        "primary_sector": primary_sector,
        "primary_concept": picks["primary_concept"],
        "success_rate": r1_rate,
        "secondary_sector": picks["secondary_sector"],
        "secondary_label": picks["secondary_label"],
        "tertiary_sector": picks["tertiary_sector"],
        "tertiary_label": picks["tertiary_label"],
        "ranked_recommendations": ranked_recs,
        "rank_1": ranked_recs[0],
        "rank_2": ranked_recs[1],
        "rank_3": ranked_recs[2],
        "lowest_rated_label": picks["lowest_rated"]["label"],
        "lowest_rated_rating": picks["lowest_rated"]["rating"],
        "total_stays": total_stays,
        "dining_count": dining_count,
        "hold_capacity": picks["hold_capacity"],
        "rationale": rationale,
        "action_bullets": [bullet_format, bullet_quality, bullet_risk],
        "risk_flags": risk_flags,
        "sectors": sectors,
        "cafes": cafes,
        "attractions": attractions,
        "airport_km": int(airport_km),
        "data_quality": data_quality,
        "photo_url": str(row.get("Photo_URL", "")),
        "tagline": str(row.get("Tagline", "")),
        "hotels": int(row.get("Hotels", 0) or 0),
        "resorts": int(row.get("Resorts", 0) or 0),
        "homestays": int(row.get("Homestays_Vacation_Rentals", 0) or 0),
        "restaurants": dining_count,
        "airport_name": str(row.get("Nearest_Airport", "Airport")),
        "airport_distance": str(row.get("Airport_Distance", f"{int(airport_km)} km")),
        "railway_name": str(row.get("Nearest_Railway_Station", "")),
        "railway_distance": str(row.get("Railway_Distance", "")),
        "main_road": str(row.get("Main_Road_or_Highway", "")),
        "road_access": str(row.get("Road_Accessibility", "")),
    }


def get_destination_recommendation(
    row: Any,
    cluster_means: Optional[Dict[str, float]] = None,
    trends_avg: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Backwards-compatible wrapper returning enriched recommendation fields for a destination record."""
    row_dict = row.to_dict() if isinstance(row, pd.Series) else dict(row)
    return build_enriched_recommendation(row_dict, cluster_means=cluster_means, trends_avg=trends_avg)
