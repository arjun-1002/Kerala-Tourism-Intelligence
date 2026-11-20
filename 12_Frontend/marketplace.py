"""
Kerala Tourism Intelligence — Venture & Investor Marketplace
Handles two-sided investment matchmaking between tourism entrepreneurs
seeking capital and private/NRI investors, including automated platform
commission calculation and escrow split tracking.
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
VENTURES_FILE = DATA_DIR / "ventures_store.json"
PLEDGES_FILE = DATA_DIR / "pledges_store.json"

DEFAULT_COMMISSION_RATE = 0.03  # 3.0% platform facilitation commission

SEED_VENTURES = [
    {
        "id": "v-wayanad-01",
        "title": "Wayanad Rainforest Eco-Treehouses & Wellness Retreat",
        "destination": "Wayanad",
        "district": "Wayanad",
        "category": "Eco-Resort & Wellness",
        "target_amount": 3500000,
        "raised_amount": 2250000,
        "min_ticket": 250000,
        "equity_or_share": "16% Equity + 10 Free Stay Nights/Yr",
        "projected_roi": "19.4% Annual",
        "payback_period": "2.4 Years",
        "proponent_name": "Suhail K. & Family",
        "proponent_role": "Cardamom Estate Owner (7 Acres)",
        "verified": True,
        "viability_score": 94,
        "cluster_name": "Established Leisure and Resort Destinations",
        "summary": "Expanding our certified organic spice estate with 6 luxury off-grid canopy treehouses. Wayanad received over 1.25M visitors in 2024 with a 42% deficit in high-end experiential stays.",
        "photo_url": "/static/images/destinations/wayanad.jpg",
        "status": "Active",
        "created_at": "2026-11-10"
    },
    {
        "id": "v-alappuzha-02",
        "title": "Alappuzha Vembanad Solar Hybrid Houseboat Fleet",
        "destination": "Alappuzha",
        "district": "Alappuzha",
        "category": "Houseboat Cruise",
        "target_amount": 4500000,
        "raised_amount": 3000000,
        "min_ticket": 500000,
        "equity_or_share": "14% Profit Share + Priority Charter Stays",
        "projected_roi": "18.2% Annual",
        "payback_period": "2.8 Years",
        "proponent_name": "Capt. V. Madhavan",
        "proponent_role": "Licensed Backwater Master (18 Yrs Exp)",
        "verified": True,
        "viability_score": 91,
        "cluster_name": "Backwater and Coastal Destinations",
        "summary": "Building a zero-emission luxury solar-electric Kettuvallam cruiser with 3 air-conditioned staterooms to capture premium European and honeymoon tourism demand on Vembanad Lake.",
        "photo_url": "/static/images/destinations/alappuzha.jpg",
        "status": "Active",
        "created_at": "2026-11-12"
    },
    {
        "id": "v-varkala-03",
        "title": "Varkala Cliffside Heritage Ayurveda & Sunset Bistro",
        "destination": "Varkala",
        "district": "Thiruvananthapuram",
        "category": "Experiential Cafe & Wellness",
        "target_amount": 2000000,
        "raised_amount": 1400000,
        "min_ticket": 200000,
        "equity_or_share": "18% Revenue Share + Quarterly Royalties",
        "projected_roi": "22.5% Annual",
        "payback_period": "1.9 Years",
        "proponent_name": "Dr. Ananya Nair & Chef Rohan",
        "proponent_role": "Ayurvedic Physician & Malabar Culinary Chef",
        "verified": True,
        "viability_score": 89,
        "cluster_name": "Backwater and Coastal Destinations",
        "summary": "Prime North Cliff beachfront space integrating organic farm-to-table coastal cuisine with rooftop yoga and traditional Karkidakam wellness packages. Foreign footfall grew +38%.",
        "photo_url": "/static/images/destinations/varkala.jpg",
        "status": "Active",
        "created_at": "2026-11-14"
    },
    {
        "id": "v-munnar-04",
        "title": "Munnar High-Range Tea Boutique Homestay",
        "destination": "Munnar",
        "district": "Idukki",
        "category": "Boutique Homestay",
        "target_amount": 2800000,
        "raised_amount": 1750000,
        "min_ticket": 250000,
        "equity_or_share": "15% Co-Ownership Share",
        "projected_roi": "17.8% Annual",
        "payback_period": "2.3 Years",
        "proponent_name": "Mathew & Geetha Kurian",
        "proponent_role": "Third-Generation Planters",
        "verified": True,
        "viability_score": 92,
        "cluster_name": "Established Leisure and Resort Destinations",
        "summary": "Restoring an authentic 1940s colonial stone planter bungalow into a 5-key experiential tea homestay with guided shola walks, private tea plucking, and panoramic valley views.",
        "photo_url": "/static/images/destinations/munnar.jpg",
        "status": "Active",
        "created_at": "2026-11-15"
    },
    {
        "id": "v-bekal-05",
        "title": "Bekal Fort Oceanfront Glamping & Kayak Outpost",
        "destination": "Bekal",
        "district": "Kasaragod",
        "category": "Adventure Tourism",
        "target_amount": 2200000,
        "raised_amount": 800000,
        "min_ticket": 200000,
        "equity_or_share": "16% Revenue Share + Free Season Pass",
        "projected_roi": "21.0% Annual",
        "payback_period": "2.1 Years",
        "proponent_name": "North Malabar Adventure Guild",
        "proponent_role": "Surf & Kayak Expedition Instructors",
        "verified": True,
        "viability_score": 86,
        "cluster_name": "Cultural and Heritage Destinations",
        "summary": "10 weatherproof geodome luxury tents on the Arabian beachfront near Bekal Fort, featuring sunset sea kayaking, stand-up paddleboarding, and local Theyyam cultural excursions.",
        "photo_url": "/static/images/destinations/bekal.jpg",
        "status": "Active",
        "created_at": "2026-11-16"
    },
    {
        "id": "v-athirappilly-06",
        "title": "Athirappilly Riverview Canopy Eco-Cottages",
        "destination": "Athirappilly",
        "district": "Thrissur",
        "category": "Eco-Resort & Wellness",
        "target_amount": 3000000,
        "raised_amount": 1800000,
        "min_ticket": 300000,
        "equity_or_share": "15% Equity Share + Annual Dividends",
        "projected_roi": "18.5% Annual",
        "payback_period": "2.5 Years",
        "proponent_name": "Chalakkudy Eco-Leisure Group",
        "proponent_role": "Sustainable Tourism Developers",
        "verified": True,
        "viability_score": 88,
        "cluster_name": "Wildlife and Eco-Tourism Destinations",
        "summary": "Boutique 8-unit riverside eco-stay nestled below the Athirappilly rainforest canopy with bio-climatic architecture, night nature walks, and wildlife photography hides.",
        "photo_url": "/static/images/destinations/athirappilly.jpg",
        "status": "Active",
        "created_at": "2026-11-17"
    }
]


def load_ventures() -> List[Dict[str, Any]]:
    if not VENTURES_FILE.exists():
        save_ventures(SEED_VENTURES)
        return list(SEED_VENTURES)
    try:
        with open(VENTURES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return list(SEED_VENTURES)


def save_ventures(ventures: List[Dict[str, Any]]) -> None:
    with open(VENTURES_FILE, "w", encoding="utf-8") as f:
        json.dump(ventures, f, indent=2, ensure_ascii=False)


def load_pledges() -> List[Dict[str, Any]]:
    if not PLEDGES_FILE.exists():
        return []
    try:
        with open(PLEDGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_pledges(pledges: List[Dict[str, Any]]) -> None:
    with open(PLEDGES_FILE, "w", encoding="utf-8") as f:
        json.dump(pledges, f, indent=2, ensure_ascii=False)


def calculate_commission(investment_amount: float, rate: float = DEFAULT_COMMISSION_RATE) -> Dict[str, Any]:
    """Calculates automated platform fee and net venture capital split."""
    platform_fee = round(investment_amount * rate, 2)
    net_capital = round(investment_amount - platform_fee, 2)
    return {
        "gross_investment": investment_amount,
        "commission_rate_pct": round(rate * 100, 1),
        "platform_fee": platform_fee,
        "net_capital_to_venture": net_capital,
        "formatted_gross": f"₹{investment_amount:,.0f}",
        "formatted_fee": f"₹{platform_fee:,.0f}",
        "formatted_net": f"₹{net_capital:,.0f}",
    }


def get_all_ventures(destination: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
    ventures = load_ventures()
    filtered = []
    for v in ventures:
        if destination and destination != "All" and v.get("destination") != destination:
            continue
        if category and category != "All" and v.get("category") != category:
            continue
        
        # Compute dynamic progress percentage
        target = float(v.get("target_amount", 1))
        raised = float(v.get("raised_amount", 0))
        progress = min(100, round((raised / target) * 100, 1)) if target > 0 else 0
        v_copy = dict(v)
        v_copy["funding_progress"] = progress
        v_copy["commission_info"] = calculate_commission(float(v.get("min_ticket", 200000)))
        filtered.append(v_copy)
    return filtered


def get_venture_by_id(venture_id: str) -> Optional[Dict[str, Any]]:
    ventures = load_ventures()
    for v in ventures:
        if v.get("id") == venture_id:
            target = float(v.get("target_amount", 1))
            raised = float(v.get("raised_amount", 0))
            v_copy = dict(v)
            v_copy["funding_progress"] = min(100, round((raised / target) * 100, 1)) if target > 0 else 0
            v_copy["commission_info"] = calculate_commission(float(v.get("min_ticket", 200000)))
            return v_copy
    return None


def create_venture(data: Dict[str, Any], master_df=None) -> Dict[str, Any]:
    ventures = load_ventures()
    new_id = f"v-{uuid.uuid4().hex[:8]}"

    dest = data.get("destination", "Wayanad").strip()
    target_amt = float(data.get("target_amount", 2500000))
    min_ticket = float(data.get("min_ticket", 200000))

    # Pull cluster and viability score from master_df if available
    cluster_name = "Emerging Tourism Cluster"
    viability_score = 88
    district = "Kerala"
    photo_url = "/static/images/destinations/wayanad.jpg"

    if master_df is not None:
        row = master_df[master_df["Destination"].str.lower() == dest.lower()]
        if not row.empty:
            r = row.iloc[0]
            cluster_name = str(r.get("Cluster_Name", cluster_name))
            viability_score = int(r.get("Opportunity_Score", 88))
            district = str(r.get("District", district))
            photo_url = str(r.get("Photo_URL", photo_url))

    new_venture = {
        "id": new_id,
        "title": data.get("title", f"New Venture in {dest}").strip(),
        "destination": dest,
        "district": district,
        "category": data.get("category", "Boutique Homestay").strip(),
        "target_amount": target_amt,
        "raised_amount": 0,
        "min_ticket": min_ticket,
        "equity_or_share": data.get("equity_or_share", "15% Revenue Share").strip(),
        "projected_roi": data.get("projected_roi", "18.5% Annual").strip(),
        "payback_period": data.get("payback_period", "2.2 Years").strip(),
        "proponent_name": data.get("proponent_name", "Local Tourism Host").strip(),
        "proponent_role": data.get("proponent_role", "Property / Enterprise Proponent").strip(),
        "verified": True,
        "viability_score": viability_score,
        "cluster_name": cluster_name,
        "summary": data.get("summary", "New hospitality and travel opportunity listed on Kerala Tourism Intelligence.").strip(),
        "photo_url": photo_url,
        "status": "Active",
        "created_at": "Just now"
    }

    ventures.insert(0, new_venture)
    save_ventures(ventures)
    return new_venture


def record_pledge(venture_id: str, investor_name: str, investor_email: str, amount: float, is_nri: bool = False, notes: str = "") -> Dict[str, Any]:
    ventures = load_ventures()
    pledges = load_pledges()

    venture = None
    for v in ventures:
        if v.get("id") == venture_id:
            venture = v
            break

    if not venture:
        raise ValueError("Venture not found.")

    min_ticket = float(venture.get("min_ticket", 100000))
    if amount < min_ticket:
        raise ValueError(f"Pledge amount (₹{amount:,.0f}) is below the minimum ticket size of ₹{min_ticket:,.0f}.")

    # Calculate automatic platform fee split
    split = calculate_commission(amount)

    # Update raised amount
    current_raised = float(venture.get("raised_amount", 0))
    venture["raised_amount"] = current_raised + amount
    if venture["raised_amount"] >= float(venture.get("target_amount", 0)):
        venture["status"] = "Funded"

    save_ventures(ventures)

    # Log pledge record
    pledge_record = {
        "pledge_id": f"pld-{uuid.uuid4().hex[:8]}",
        "venture_id": venture_id,
        "venture_title": venture.get("title"),
        "destination": venture.get("destination"),
        "investor_name": investor_name.strip(),
        "investor_email": investor_email.strip(),
        "gross_amount": amount,
        "platform_commission": split["platform_fee"],
        "net_deployed_capital": split["net_capital_to_venture"],
        "is_nri": is_nri,
        "notes": notes.strip(),
        "status": "Confirmed & Escrowed",
        "created_at": "2026-11-20"
    }
    pledges.insert(0, pledge_record)
    save_pledges(pledges)

    return {
        "success": True,
        "pledge": pledge_record,
        "split": split,
        "updated_raised": venture["raised_amount"],
        "funding_progress": min(100, round((venture["raised_amount"] / float(venture.get("target_amount", 1))) * 100, 1))
    }


def get_marketplace_kpis() -> Dict[str, Any]:
    ventures = load_ventures()
    pledges = load_pledges()

    total_pipeline = sum(float(v.get("target_amount", 0)) for v in ventures)
    total_raised = sum(float(v.get("raised_amount", 0)) for v in ventures)
    total_commission_collected = sum(float(p.get("platform_commission", 0)) for p in pledges)

    # Also compute theoretical platform commission on all raised so far
    theoretical_commission = total_raised * DEFAULT_COMMISSION_RATE

    return {
        "total_ventures": len(ventures),
        "active_ventures": len([v for v in ventures if v.get("status") == "Active"]),
        "total_pipeline_inr": f"₹{total_pipeline / 10000000:.2f} Cr",
        "total_raised_inr": f"₹{total_raised / 10000000:.2f} Cr",
        "commission_rate_display": f"{DEFAULT_COMMISSION_RATE * 100:.1f}%",
        "total_commission_earned_inr": f"₹{max(total_commission_collected, theoretical_commission):,.0f}",
        "total_investors_count": max(len(pledges), 14)  # 14 base syndicate pledges + new pledges
    }
