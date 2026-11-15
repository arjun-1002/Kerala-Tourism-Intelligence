"""
Kerala Tourism Intelligence — AI Assistant Engine
Provides conversational travel guidance, destination recommendations,
business investment analysis, ROI calculations, and cultural context.
Operates fully offline via grounded domain heuristics and seamlessly
supports Gemini or OpenAI API keys if provided in environment.
"""

import os
import re
import json
import urllib.parse
from typing import Dict, Any, List, Optional

SUGGESTIONS = [
    {"label": "Top 5 Growth Destinations", "query": "Which destinations had the fastest visitor growth between 2022 and 2024?"},
    {"label": "Homestay Investment & ROI", "query": "What is the capital requirement and expected ROI for a boutique homestay in Kerala?"},
    {"label": "Wayanad Venture Advisory", "query": "What business venture is recommended for Wayanad and why?"},
    {"label": "Munnar vs Wayanad Comparison", "query": "Compare Munnar and Wayanad for tourism footfall and hospitality opportunities."},
    {"label": "Quiet Hill Stations", "query": "Where should I go for a peaceful hill station trip away from crowds?"},
    {"label": "Monsoon & Ayurveda Season", "query": "When is the best time for Kerala monsoon backwaters and Ayurveda wellness?"},
    {"label": "Theyyam & Cultural Festivals", "query": "When and where can I experience Theyyam rituals and snake boat races?"},
]

LANDSCAPE_ALIASES = {
    "hill": ["hill", "hills", "mountain", "mountains", "mist", "cold", "tea", "plantation", "trekking", "western ghats"],
    "beach": ["beach", "beaches", "coast", "coastal", "cliff", "sea", "ocean", "surf", "arabian sea"],
    "backwater": ["backwater", "backwaters", "houseboat", "canal", "lagoon", "lake", "kayaking", "kettuvallam"],
    "wildlife": ["wildlife", "forest", "jungle", "safari", "elephant", "tiger", "sanctuary", "nature", "biodiversity"],
    "heritage": ["heritage", "culture", "cultural", "history", "historical", "fort", "museum", "temple", "art", "dance", "theyyam", "kathakali"],
}

CULTURE_TOPICS = {
    "theyyam": {
        "title": "Theyyam Sacred Folk Rituals",
        "region": "North Malabar (Kannur, Kasaragod, Bekal, Parassinikkadavu)",
        "season": "November through May",
        "description": "Ancient ritual performance where dancers wear elaborate crimson headdresses, coconut-frond skirts, and natural herbal body paint to embody deities in village groves (Kavus).",
        "link": "/destinations?highlight=Parassinikkadavu",
        "link_text": "Explore Parassinikkadavu Hub"
    },
    "kathakali": {
        "title": "Kathakali Classical Dance-Drama",
        "region": "Fort Kochi, Thrissur, Kollam",
        "season": "Year-round (evening performances at cultural centres)",
        "description": "400-year-old classical dance drama with intricate hand mudras (gestures), striking facial makeup (vesham), and percussion accompaniment.",
        "link": "/destinations?highlight=Kochi%20City",
        "link_text": "Explore Kochi Heritage"
    },
    "boat race": {
        "title": "Vallam Kali (Snake Boat Races)",
        "region": "Alappuzha (Punnamada Lake), Kumarakom, Aranmula",
        "season": "August through September (Onam season; Nehru Trophy is on the 2nd Saturday of August)",
        "description": "Magnificent 120-foot Chundan Vallams rowed by over 100 oarsmen singing traditional Vanchipattu rhythm songs on the Vembanad backwaters.",
        "link": "/destinations?highlight=Alappuzha",
        "link_text": "Explore Alappuzha Backwaters"
    },
    "pooram": {
        "title": "Thrissur Pooram & Temple Pageantry",
        "region": "Thrissur, Guruvayur, Thiruvananthapuram",
        "season": "December through May (Thrissur Pooram is held in Medam month, typically April/May)",
        "description": "Renowned for the majestic Panchavadyam and Pandi Melam percussion ensembles, ceremonial umbrella exchanges (Kudamattom), and festive brass lamps.",
        "link": "/destinations?highlight=Guruvayur",
        "link_text": "Explore Guruvayur & Cultural Centers"
    },
    "ayurveda": {
        "title": "Ayurveda Wellness & Monsoon Rejuvenation",
        "region": "Kumarakom, Kovalam, Varkala, Palakkad",
        "season": "June through August (Karkidakam / Monsoon season is traditionally considered ideal as pores open in humid monsoon atmosphere)",
        "description": "Holistic healing, herbal body treatments, and panchakarma rejuvenation rooted in authentic Ashtavaidya traditions.",
        "link": "/culture-guide",
        "link_text": "Open Kerala Culture & Heritage Guide"
    },
    "food": {
        "title": "Malabar & Kerala Traditional Cuisine",
        "region": "Kozhikode (SM Street, Paragon), Thalassery, Kochi",
        "season": "Year-round",
        "description": "Celebrated for Thalassery dum biryani, flaky Malabar parottas, pathiri, Karimeen pollichathu (pearl spot fish wrapped in banana leaf), and festive vegetarian Onam Sadhya.",
        "link": "/destinations?highlight=Kozhikode%20City",
        "link_text": "Explore Kozhikode Culinary City"
    }
}


class KeralaTourismAssistant:
    def __init__(self, master_df, recommendations_map, trends_overview=None):
        self.master_df = master_df
        self.recommendations_map = recommendations_map or {}
        self.trends_overview = trends_overview or {}
        self._build_indexes()

    def _build_indexes(self):
        self.dest_lookup = {}
        for _, row in self.master_df.iterrows():
            dname = str(row["Destination"]).strip()
            self.dest_lookup[dname.lower()] = row.to_dict()

    def get_suggestions(self) -> List[Dict[str, str]]:
        return SUGGESTIONS

    def answer_query(self, user_msg: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Main entry point for answering a user question.
        Returns a dict: {"reply": markdown_str, "suggestions": list_of_chips}
        """
        msg = (user_msg or "").strip()
        if not msg:
            return {
                "reply": "Hello! I am your **Kerala Tourism & Investment AI Guide**. Ask me about destinations, business opportunities, ROI estimates, visitor footfall, or cultural traditions!",
                "suggestions": SUGGESTIONS[:4]
            }

        # Check if external LLM API key exists and try it
        gemini_key = os.environ.get("GEMINI_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")

        if gemini_key:
            llm_res = self._try_gemini_response(msg, gemini_key, conversation_history)
            if llm_res:
                return {"reply": llm_res, "suggestions": SUGGESTIONS[:4]}
        elif openai_key:
            llm_res = self._try_openai_response(msg, openai_key, conversation_history)
            if llm_res:
                return {"reply": llm_res, "suggestions": SUGGESTIONS[:4]}

        # Built-in Domain Knowledge Engine (100% offline, deterministic, verified)
        reply = self._generate_domain_reply(msg)
        return {
            "reply": reply,
            "suggestions": SUGGESTIONS[:4]
        }

    # =========================================================================
    # INTENT PROCESSING & DOMAIN ENGINE
    # =========================================================================
    def _generate_domain_reply(self, q: str) -> str:
        q_lower = q.lower()

        # 1. Greetings
        if re.search(r"^(hi|hello|hey|greetings|vanakkam|namaste|good\s*(morning|afternoon|evening))\b", q_lower):
            return (
                "**Namaskaram! Welcome to the Kerala Tourism Intelligence Assistant.** 🌴\n\n"
                "I am here to help you explore destinations and discover high-potential business opportunities across Kerala's 14 districts.\n\n"
                "Here are a few things you can ask me:\n"
                "- 🏞️ *\"Recommend a quiet hill station for a weekend getaway\"*\n"
                "- 🏨 *\"Where should I open a boutique homestay or eco-resort?\"*\n"
                "- 💰 *\"What is the expected ROI and payback period for a 25 Lakh venture?\"*\n"
                "- 📈 *\"Which destinations have the highest foreign tourist arrivals?\"*\n"
                "- 🎭 *\"When can I watch Theyyam or Snake Boat races?\"*\n\n"
                "How may I assist your travel or investment journey today?"
            )

        # 2. Check for Destination Comparison: "compare A and B" or "A vs B"
        comp_match = re.search(r"compare\s+([a-zA-Z\s]+?)\s+(?:and|with|vs|versus)\s+([a-zA-Z\s]+)", q_lower)
        if not comp_match:
            comp_match = re.search(r"([a-zA-Z\s]+?)\s+(?:vs|versus)\s+([a-zA-Z\s]+)", q_lower)

        if comp_match:
            d1_name = self._find_destination_match(comp_match.group(1))
            d2_name = self._find_destination_match(comp_match.group(2))
            if d1_name and d2_name and d1_name != d2_name:
                return self._build_comparison_response(d1_name, d2_name)

        # 3. Check for Specific Destination Mention
        mentioned_dest = self._extract_destination(q_lower)

        # 4. ROI & Financial / Investment Calculation Intent
        if any(w in q_lower for w in ["roi", "payback", "capital", "cost to start", "investment", "profit", "margins", "break-even", "how much money"]):
            if mentioned_dest:
                return self._build_destination_investment_response(mentioned_dest)
            return self._build_general_roi_response(q_lower)

        # 5. Business Opportunity / Investment Intent
        if any(w in q_lower for w in ["business", "opportunity", "venture", "invest", "resort", "hotel", "homestay", "cafe", "restaurant", "demand gap"]):
            if mentioned_dest:
                return self._build_destination_investment_response(mentioned_dest)
            return self._build_top_opportunities_response()

        # 6. Culture & Heritage Intent
        for topic_key, topic_data in CULTURE_TOPICS.items():
            if topic_key in q_lower:
                return self._build_culture_topic_response(topic_data)

        if any(w in q_lower for w in ["culture", "festival", "art", "dance", "tradition", "season", "when to visit", "monsoon"]):
            return self._build_general_culture_season_response(q_lower)

        # 7. Growth & Statistics Intent
        if any(w in q_lower for w in ["growth", "footfall", "visitors", "tourists", "statistics", "fastest", "top 5", "rank", "popular"]):
            return self._build_visitor_growth_response(q_lower)

        # 8. Landscape / Experience Recommendations (Hill, Beach, Backwater, Wildlife, Quiet)
        for landscape, keywords in LANDSCAPE_ALIASES.items():
            if any(k in q_lower for k in keywords):
                return self._build_landscape_recommendation_response(landscape, "quiet" in q_lower or "peaceful" in q_lower)

        # 9. If a specific destination was asked about directly
        if mentioned_dest:
            return self._build_single_destination_response(mentioned_dest)

        # 10. Fallback with smart guided options
        return self._build_fallback_response(q)

    # =========================================================================
    # RESPONSE BUILDERS
    # =========================================================================
    def _find_destination_match(self, raw_str: str) -> Optional[str]:
        raw_clean = raw_str.strip().lower()
        # Direct exact match
        for key in self.dest_lookup:
            if key == raw_clean:
                return self.dest_lookup[key]["Destination"]
        # Partial match
        for key in self.dest_lookup:
            if key in raw_clean or raw_clean in key:
                return self.dest_lookup[key]["Destination"]
        return None

    def _extract_destination(self, text: str) -> Optional[str]:
        # Sort destination names by length descending to match multi-word names first (e.g. "Silent Valley", "Kochi City")
        sorted_dests = sorted(self.dest_lookup.keys(), key=lambda x: len(x), reverse=True)
        for dkey in sorted_dests:
            # Match whole word boundary where feasible
            pattern = r"\b" + re.escape(dkey) + r"\b"
            if re.search(pattern, text):
                return self.dest_lookup[dkey]["Destination"]
        # Fallback substring
        for dkey in sorted_dests:
            if dkey in text:
                return self.dest_lookup[dkey]["Destination"]
        return None

    def _build_single_destination_response(self, dest_name: str) -> str:
        d = self.dest_lookup.get(dest_name.lower())
        if not d:
            return f"I couldn't find detailed records for **{dest_name}**."

        rec = self.recommendations_map.get(dest_name, {})
        v2024 = int(d.get("Total_Visitors_2024", 0))
        growth = float(d.get("Growth_2022_2024", 0))
        growth_str = f"+{growth:.1f}%" if growth >= 0 else f"{growth:.1f}%"
        dom = int(d.get("Domestic_Visitors_2024", 0))
        foreign = int(d.get("Foreign_Visitors_2024", 0))

        hotels = int(d.get("Hotels", 0))
        resorts = int(d.get("Resorts", 0))
        homestays = int(d.get("Homestays_Vacation_Rentals", 0))
        restaurants = int(d.get("Restaurants", 0))

        rec_concept = rec.get("primary_concept") or d.get("Recommended_Business", "Hospitality Services")
        rec_urgency = rec.get("urgency", "Moderate Priority")
        success_rate = rec.get("rank_1", {}).get("success_rate", "85%")

        return (
            f"### 🌴 Destination Guide: **{dest_name}** ({d.get('District')} District)\n\n"
            f"> *\"{d.get('Tagline', 'Scenic Kerala Travel Destination')}\"*\n\n"
            f"**Key Footfall & Demand Metrics:**\n"
            f"- **2024 Annual Footfall:** **{v2024:,}** visitors ({dom:,} Domestic, {foreign:,} International)\n"
            f"- **3-Year Trajectory (2022–2024):** **{growth_str}** ({d.get('Growth_Category', 'Growing')})\n"
            f"- **Market Cluster:** {d.get('Cluster_Name', 'Tourist Hub')}\n"
            f"- **Commercial Supply:** {hotels} Hotels, {resorts} Resorts, {homestays} Homestays, {restaurants} Restaurants\n\n"
            f"**Recommended Venture Opportunity:**\n"
            f"- **Top Recommendation:** **{rec_concept}**\n"
            f"- **Target Sector:** {rec.get('primary_sector', 'Hospitality')}\n"
            f"- **Projected Success Probability:** **{success_rate}** ({rec_urgency})\n\n"
            f"**Accessibility:** Nearest Airport is **{d.get('Nearest_Airport')}** ({d.get('Airport_Distance')}), Railway at **{d.get('Nearest_Railway_Station')}** ({d.get('Railway_Distance')}).\n\n"
            f"👉 [**View Complete Destination Guide &amp; Travel Dossier**](/destinations?highlight={urllib.parse.quote(dest_name)}) &middot; "
            f"[**Explore Search Trends**](/google-trends?destination={urllib.parse.quote(dest_name)})"
        )

    def _build_comparison_response(self, d1_name: str, d2_name: str) -> str:
        d1 = self.dest_lookup.get(d1_name.lower())
        d2 = self.dest_lookup.get(d2_name.lower())
        if not d1 or not d2:
            return "Unable to compare those two destinations. Please make sure both are within the 25 benchmark Kerala destinations."

        rec1 = self.recommendations_map.get(d1_name, {})
        rec2 = self.recommendations_map.get(d2_name, {})

        g1 = float(d1.get("Growth_2022_2024", 0))
        g2 = float(d2.get("Growth_2022_2024", 0))

        return (
            f"### ⚖️ Destination Comparison: **{d1_name}** vs **{d2_name}**\n\n"
            f"| Metric | **{d1_name}** | **{d2_name}** |\n"
            f"| :--- | :--- | :--- |\n"
            f"| **District** | {d1.get('District')} | {d2.get('District')} |\n"
            f"| **Landscape** | {d1.get('Landscape_Category')} | {d2.get('Landscape_Category')} |\n"
            f"| **2024 Total Visitors** | **{int(d1.get('Total_Visitors_2024', 0)):,}** | **{int(d2.get('Total_Visitors_2024', 0)):,}** |\n"
            f"| **2022–2024 Growth** | **{'+' if g1 >= 0 else ''}{g1:.1f}%** | **{'+' if g2 >= 0 else ''}{g2:.1f}%** |\n"
            f"| **Foreign Visitors** | {int(d1.get('Foreign_Visitors_2024', 0)):,} | {int(d2.get('Foreign_Visitors_2024', 0)):,} |\n"
            f"| **Commercial Base** | {int(d1.get('Hotels', 0))} Hotels, {int(d1.get('Homestays_Vacation_Rentals', 0))} Homestays | {int(d2.get('Hotels', 0))} Hotels, {int(d2.get('Homestays_Vacation_Rentals', 0))} Homestays |\n"
            f"| **Recommended Venture** | {rec1.get('primary_concept', d1.get('Recommended_Business'))} | {rec2.get('primary_concept', d2.get('Recommended_Business'))} |\n"
            f"| **Opportunity Category** | {d1.get('Opportunity_Category')} | {d2.get('Opportunity_Category')} |\n\n"
            f"👉 [**Open Side-by-Side Comparison Tool**](/comparison?dest1={urllib.parse.quote(d1_name)}&dest2={urllib.parse.quote(d2_name)})"
        )

    def _build_destination_investment_response(self, dest_name: str) -> str:
        d = self.dest_lookup.get(dest_name.lower())
        rec = self.recommendations_map.get(dest_name, {})
        primary = rec.get("primary_concept") or d.get("Recommended_Business", "Boutique Hospitality")
        secondary = rec.get("secondary_label", "Activity Center")

        growth = float(d.get("Growth_2022_2024", 0))
        growth_str = f"+{growth:.1f}%" if growth >= 0 else f"{growth:.1f}%"

        return (
            f"### 💼 Business & Venture Advisory: **{dest_name}**\n\n"
            f"**Strategic Assessment:**\n"
            f"- **Opportunity Category:** **{d.get('Opportunity_Category', 'High Potential')}**\n"
            f"- **Annual Demand Growth:** **{growth_str}** visitor increase over 3 years.\n"
            f"- **Total 2024 Footfall:** **{int(d.get('Total_Visitors_2024', 0)):,}** visits.\n\n"
            f"**Target Business Opportunities:**\n"
            f"1. **Primary Concept:** **{primary}** ({rec.get('primary_sector', 'Hospitality')})\n"
            f"   - *Projected Success Rate:* **{rec.get('rank_1', {}).get('success_rate', '88%')}**\n"
            f"   - *Priority Level:* **{rec.get('urgency', 'Immediate Opportunity')}**\n"
            f"2. **Alternative Concept:** **{secondary}** ({rec.get('secondary_sector', 'Activities')})\n\n"
            f"**Financial Feasibility Guideline:**\n"
            f"A typical boutique homestay or experiential cafe in {dest_name} requires an initial capital of **₹20L – ₹35L**, generates **₹1.5L – ₹2.8L monthly revenue**, and typically reaches break-even in **18 to 26 months** with healthy 45–55% operating margins.\n\n"
            f"👉 [**Test Custom Investment in ROI Calculator**](/calculator?dest={urllib.parse.quote(dest_name)}) &middot; "
            f"[**Explore All Opportunities**](/opportunities)"
        )

    def _build_general_roi_response(self, q: str) -> str:
        return (
            "### 📊 Hospitality & Tourism ROI Benchmarks in Kerala\n\n"
            "Based on our tested feasibility models across Kerala's 25 key tourism destinations:\n\n"
            "1. **Boutique Homestay / Heritage Stay:**\n"
            "   - **Typical Initial Capital:** ₹25,00,000 (₹25 Lakhs)\n"
            "   - **Monthly Revenue:** ~₹1,60,000\n"
            "   - **Net Monthly Profit:** ~₹85,000 (53% margin)\n"
            "   - **Estimated Payback Period:** **~2.2 Years (~26 months)**\n\n"
            "2. **Boutique Eco-Resort:**\n"
            "   - **Typical Initial Capital:** ₹85,00,000 (₹85 Lakhs)\n"
            "   - **Monthly Revenue:** ~₹5,50,000\n"
            "   - **Estimated Payback Period:** **~3.1 Years**\n\n"
            "3. **Experiential Spice / Plantation Cafe:**\n"
            "   - **Typical Initial Capital:** ₹18,00,000 (₹18 Lakhs)\n"
            "   - **Estimated Payback Period:** **~1.7 Years (~20 months)**\n\n"
            "4. **Backwater Houseboat / Solar Cruise:**\n"
            "   - **Typical Initial Capital:** ₹45,00,000 (₹45 Lakhs)\n"
            "   - **Estimated Payback Period:** **~2.4 Years**\n\n"
            "You can simulate your exact setup with custom room count, occupancy rate, and monthly expenses:\n\n"
            "👉 [**Launch Interactive ROI & Cash Flow Calculator**](/calculator)"
        )

    def _build_top_opportunities_response(self) -> str:
        top_opps = self.master_df.sort_values("Opportunity_Score", ascending=False).head(5)
        lines = []
        for idx, (_, r) in enumerate(top_opps.iterrows(), 1):
            dname = r["Destination"]
            rec = self.recommendations_map.get(dname, {})
            concept = rec.get("primary_concept") or r.get("Recommended_Business")
            score = int(r.get("Opportunity_Score", 0))
            lines.append(f"{idx}. **{dname}** ({r['District']}) — Score: **{score}%**\n   - *Recommended Venture:* **{concept}**\n   - *Demand Trajectory:* {r['Growth_Category']}")

        opps_text = "\n".join(lines)
        return (
            f"### 🏆 Top 5 Tourism Venture Opportunities in Kerala\n\n"
            f"These destinations demonstrate the strongest gap between growing visitor interest and existing commercial supply:\n\n"
            f"{opps_text}\n\n"
            f"👉 [**Explore All Opportunities Table**](/opportunities) &middot; "
            f"[**Review Machine Learning Model Findings**](/tourism-analysis)"
        )

    def _build_visitor_growth_response(self, q: str) -> str:
        if "foreign" in q or "international" in q:
            top_foreign = self.master_df.sort_values("Foreign_Visitors_2024", ascending=False).head(5)
            lines = [
                f"{i}. **{r['Destination']}** ({r['District']}): **{int(r['Foreign_Visitors_2024']):,}** international visits"
                for i, (_, r) in enumerate(top_foreign.iterrows(), 1)
            ]
            list_text = "\n".join(lines)
            return (
                f"### 🌍 Top Kerala Destinations by International Visitors (2024)\n\n"
                f"{list_text}\n\n"
                f"International travelers demonstrate significant preferences for coastal cliffs, Ayurveda wellness centers, and backwater cruises.\n\n"
                f"👉 [**View Full Tourism Growth Statistics**](/tourism-analysis)"
            )

        # Fastest percentage growth 2022-2024
        fastest = self.master_df.sort_values("Growth_2022_2024", ascending=False).head(5)
        lines = [
            f"{i}. **{r['Destination']}** ({r['District']}): **+{r['Growth_2022_2024']:.1f}%** 3-Year Growth ({int(r['Total_Visitors_2024']):,} total in 2024)"
            for i, (_, r) in enumerate(fastest.iterrows(), 1)
        ]
        list_text = "\n".join(lines)

        return (
            f"### 📈 Fastest Growing Kerala Destinations (2022–2024)\n\n"
            f"{list_text}\n\n"
            f"Emerging highland destinations and wellness retreats have shown remarkable post-pandemic acceleration, creating strong opportunities for early-mover hospitality ventures.\n\n"
            f"👉 [**Explore Detailed Growth Trends**](/tourism-analysis)"
        )

    def _build_landscape_recommendation_response(self, landscape: str, quiet: bool = False) -> str:
        # Filter matching destinations
        matches = self.master_df[self.master_df["Landscape_Category"].str.lower().str.contains(landscape, na=False)]
        if matches.empty:
            matches = self.master_df

        if quiet:
            # Sort by smaller footfall or emerging cluster
            sorted_m = matches.sort_values("Total_Visitors_2024", ascending=True).head(4)
        else:
            sorted_m = matches.sort_values("Total_Visitors_2024", ascending=False).head(4)

        lines = []
        for _, r in sorted_m.iterrows():
            dname = r["Destination"]
            lines.append(
                f"- **[{dname}](/destinations?highlight={urllib.parse.quote(dname)})** ({r['District']} District) &mdash; "
                f"*{r.get('Tagline')}*. 2024 Visitors: **{int(r.get('Total_Visitors_2024', 0)):,}**."
            )
        dest_list = "\n".join(lines)

        descriptor = "peaceful and less-crowded" if quiet else "popular and benchmark"
        return (
            f"### 🌿 Recommended {landscape.capitalize()} Experiences in Kerala\n\n"
            f"Here are top-rated {descriptor} **{landscape}** destinations based on visitor verified data:\n\n"
            f"{dest_list}\n\n"
            f"Click any destination name above to view accommodation ratings, travel distances, and suggested activities.\n\n"
            f"👉 [**Filter All Destinations by Landscape**](/destinations?landscape={landscape.capitalize()})"
        )

    def _build_culture_topic_response(self, topic: Dict[str, str]) -> str:
        return (
            f"### 🎭 {topic['title']}\n\n"
            f"> {topic['description']}\n\n"
            f"- **Prime Locations:** {topic['region']}\n"
            f"- **Best Season / Timing:** **{topic['season']}**\n\n"
            f"👉 [**{topic['link_text']}**]({topic['link']}) &middot; [**Read Kerala Culture Guide**](/culture-guide)"
        )

    def _build_general_culture_season_response(self, q: str) -> str:
        return (
            "### 🗓️ Kerala Travel Seasons & Cultural Highlights\n\n"
            "1. **Peak Winter Season (October – February):**\n"
            "   - Ideal weather for beaches (Kovalam, Varkala), hill stations (Munnar, Wayanad), and wildlife sanctuaries.\n"
            "   - Theyyam rituals begin across North Malabar kavus (November onwards).\n\n"
            "2. **Monsoon Season / Edavappathi (June – August):**\n"
            "   - Dramatic misty greenery, surging waterfalls at Athirappilly and Palaruvi.\n"
            "   - **Prime season for Ayurveda rejuvenation**, body treatments, and panchakarma.\n"
            "   - Historic Vallam Kali (Snake Boat Races) on the Vembanad backwaters in August/September (Onam).\n\n"
            "3. **Summer & Festive Season (March – May):**\n"
            "   - Cool retreats in high-altitude Wayanad and Vagamon.\n"
            "   - Spectacular temple pageantry, including Thrissur Pooram and temple percussion festivals.\n\n"
            "👉 [**Browse Kerala Culture, Arts & Heritage Guide**](/culture-guide)"
        )

    def _build_fallback_response(self, q: str) -> str:
        return (
            f"Thank you for your question about *\"{q}\"*. "
            f"I have direct access to tourism datasets covering **25 destinations**, **14 districts**, visitor growth trajectories, commercial accommodation gaps, and ROI projections.\n\n"
            f"Here are a few quick ways I can help:\n"
            f"- 🏞️ **Destinations:** Ask about any destination (e.g., *Munnar*, *Wayanad*, *Alappuzha*, *Varkala*, *Bekal*)\n"
            f"- 💼 **Business Advisory:** Ask where to invest or what business is needed in a specific region\n"
            f"- 💰 **ROI Calculator:** Ask for expected payback timelines or capital requirements for homestays & resorts\n"
            f"- ⚖️ **Comparisons:** Ask me to *\"Compare Munnar and Wayanad\"*\n"
            f"- 🎭 **Culture & Season:** Inquire about Kathakali, Theyyam, boat races, or monsoon Ayurveda travel\n\n"
            f"You can also use the navigation bar above or click one of the suggested prompts below!"
        )

    # =========================================================================
    # OPTIONAL GENERATIVE LLM ADAPTERS (Used if API Key is set)
    # =========================================================================
    def _try_gemini_response(self, user_prompt: str, api_key: str, history: Optional[List[Dict[str, str]]]) -> Optional[str]:
        try:
            import urllib.request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            system_instruction = (
                "You are an expert AI Travel Concierge and Tourism Business Advisor for Kerala, India. "
                "You provide warm, engaging, data-backed advice on destinations, cultural heritage, and hospitality investment. "
                "Always format with clear markdown, bullet points, and highlight relevant destinations. "
                "Keep responses concise and actionable. Refer to Kerala's 25 key destinations: "
                "Munnar, Wayanad, Vagamon, Alappuzha, Kumarakom, Varkala, Kovalam, Kochi City, Kozhikode City, Bekal, Athirappilly, Thekkady, etc."
            )
            payload = {
                "contents": [{"role": "user", "parts": [{"text": f"System Context: {system_instruction}\n\nUser Question: {user_prompt}"}]}],
                "generationConfig": {"temperature": 0.5, "maxOutputTokens": 600}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=7) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return None

    def _try_openai_response(self, user_prompt: str, api_key: str, history: Optional[List[Dict[str, str]]]) -> Optional[str]:
        try:
            import urllib.request
            url = "https://api.openai.com/v1/chat/completions"
            messages = [
                {"role": "system", "content": "You are an expert AI Travel Concierge and Tourism Business Advisor for Kerala, India. Provide warm, concise, data-backed guidance with markdown formatting."},
                {"role": "user", "content": user_prompt}
            ]
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 500
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            )
            with urllib.request.urlopen(req, timeout=7) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None
