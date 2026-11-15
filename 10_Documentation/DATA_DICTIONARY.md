# Kerala Tourism Intelligence Platform — Data Dictionary

This document describes the structure and column definitions of the master analytical dataset (`03_Cleaned_Data/kerala_tourism_master_dataset_25_destinations.csv`) covering 25 major tourist destinations across Kerala.

---

## 1. Geographical & Identification Features

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `Destination` | string | Standardized name of the Kerala tourist destination (e.g., Munnar, Kumarakom, Varkala). |
| `District` | string | Administrative district in Kerala (e.g., Idukki, Kottayam, Thiruvananthapuram). |
| `Latitude` | float | Geographic latitude coordinate (WGS84). |
| `Longitude` | float | Geographic longitude coordinate (WGS84). |
| `Landscape_Category` | string | Natural landscape classification: `Hills`, `Backwaters`, `Coastal`, or `Urban`. |
| `Attraction_Count` | integer | Number of verified tourist attractions, heritage sites, and natural signposts in destination bounds. |

---

## 2. Commercial Hospitality & Supply Infrastructure

Counts obtained from verified directory scraping, Google Maps business registers, and official municipal audits:

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `Hotels` | integer | Total licensed hotels within the destination corridor. |
| `Resorts` | integer | Total eco-resorts, luxury boutique retreats, and wellness retreats. |
| `Homestays_Vacation_Rentals` | integer | Registered and estimated homestay, bed & breakfast, and serviced villa accommodations. |
| `Restaurants` | integer | Full-service dining venues, traditional eateries, and seafood restaurants. |
| `Cafes` | integer | Coffee shops, bakeries, and casual cafes. |
| `Bakeries` | integer | Independent bakery and pastry outlets. |

---

## 3. Customer Satisfaction & Rating Averages

Derived from customer review aggregations (1.0 to 5.0 scale):

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `Hotels_Average_Rating` | float | Mean customer review score for hotels in the destination. |
| `Resorts_Average_Rating` | float | Mean customer review score for resorts in the destination. |
| `Homestays_Average_Rating` | float | Mean customer review score for homestays in the destination. |
| `Restaurants_Average_Rating` | float | Mean customer review score for restaurants in the destination. |

---

## 4. Visitor Footfall & Influx Growth (2022–2024)

Compiled from Kerala Tourism Statistics (Department of Tourism, Government of Kerala):

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `Domestic_Visitors_2022` | integer | Indian domestic tourist arrivals in 2022. |
| `Foreign_Visitors_2022` | integer | International foreign tourist arrivals in 2022. |
| `Total_Visitors_2022` | integer | Total visitor count in 2022 (`Domestic + Foreign`). |
| `Domestic_Visitors_2023` | integer | Indian domestic tourist arrivals in 2023. |
| `Foreign_Visitors_2023` | integer | International foreign tourist arrivals in 2023. |
| `Total_Visitors_2023` | integer | Total visitor count in 2023 (`Domestic + Foreign`). |
| `Domestic_Visitors_2024` | integer | Indian domestic tourist arrivals in 2024. |
| `Foreign_Visitors_2024` | integer | International foreign tourist arrivals in 2024. |
| `Total_Visitors_2024` | integer | Total visitor count in 2024 (`Domestic + Foreign`). |
| `Growth_2022_2024` | float | Percentage growth in total visitors from 2022 to 2024 (`((Total_2024 - Total_2022) / Total_2022) * 100`). |
| `Data_Quality` | string | Audit flag indicating verified official counts vs derived estimations (`Contains estimates` or `No estimation notes`). |

---

## 5. Machine Learning Segmentation & Infrastructure Gap Metrics

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `Cluster` | integer | K-Means cluster assignment ID (`0`, `1`, or `2`). |
| `Cluster_Name` | string | Descriptive archetype: `Urban Tourism and Commercial Hubs`, `Developing and Nature-Based Destinations`, or `Established Leisure and Resort Destinations`. |
| `Overall_Gap_Score` | float | Statistical infrastructure deficit score relative to peer cluster mean. Higher scores indicate larger supply deficits. |
| `Opportunity_Category` | string | 2x2 matrix classification (`High Potential & Growing Demand`, `Undersupplied & Developing`, `Established Market & Growing`, `Mature & Well-Established`). |
| `Opportunity_Score` | integer | Normalized opportunity index (0 to 100 scale). |
| `Recommended_Business` | string | Primary recommended business sector (`Homestay / Boutique Stays`, `Specialty Restaurant / Cafe`, `Eco-Resort / Retreat`, `Urban Hospitality Hub`). |
