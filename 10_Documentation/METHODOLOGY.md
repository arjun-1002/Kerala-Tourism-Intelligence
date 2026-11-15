# Analytical Methodology & Statistical Formulation

This document outlines the end-to-end data science and financial modeling methodology implemented in the Kerala Tourism Intelligence platform.

---

## 1. Feature Preprocessing & Imputation

1. **Zero-Count Imputation**: In raw data, true zero supply is distinguished from missing reporting. Unrecorded counts in `Hotels`, `Resorts`, and `Homestays` are median-imputed across peer landscape categories prior to distance-metric computation.
2. **Feature Normalization**: Eight continuous features are evaluated across two scaling regimes:
   * **StandardScaler**: Centers around mean with unit variance ($\mu = 0, \sigma = 1$).
   * **RobustScaler**: Uses median and Interquartile Range ($IQR = Q3 - Q1$) to resist skewness from high-volume commercial centers (e.g. Kochi City, Kozhikode City).

Features selected for unsupervised segmentation:
* `Attraction_Count`
* `Hotels`
* `Resorts`
* `Homestays_Vacation_Rentals`
* `Restaurants`
* `Hotels_Average_Rating`
* `Resorts_Average_Rating`
* `Nearest_Airport_Distance_km_numeric`

---

## 2. K-Means Clustering & Model Validation

Cluster evaluation is conducted across $k \in [2, 8]$ using three complementary metrics:
* **Silhouette Score**: Measures intra-cluster cohesion vs nearest-cluster separation (optimal: higher).
* **Davies-Bouldin Index**: Measures similarity between clusters (optimal: lower).
* **Calinski-Harabasz Index**: Ratio of between-cluster to within-cluster dispersion (optimal: higher).

### Benchmarking Results:

| Model Configuration | Feature Space | Silhouette Score | Davies-Bouldin | Calinski-Harabasz |
| :--- | :--- | :---: | :---: | :---: |
| **StandardScaler + K-Means ($k=3$)** | 8 Features | **0.3899** | 0.9875 | 15.35 |
| **RobustScaler + K-Means ($k=3$)** | 8 Features | **0.5804** | 0.6431 | 28.21 |
| **RobustScaler + PCA(2) + K-Means ($k=3$)** | 2 PCA Comps | **0.6799** | 0.5692 | 45.81 |

The 3 identified cluster archetypes:
* **Cluster 0:** *Urban Tourism and Commercial Hubs* (Kochi City, Kozhikode City, Thiruvananthapuram City).
* **Cluster 1:** *Developing and Nature-Based Destinations* (14 emerging eco-corridors such as Vagamon, Ponmudi, Konni, Ranipuram).
* **Cluster 2:** *Established Leisure and Resort Destinations* (8 major holiday destinations including Munnar, Wayanad, Kovalam, Varkala, Kumarakom).

---

## 3. Infrastructure Gap Scoring & Opportunity Quadrants

### Cluster-Relative Deficit ($G_i$):
To avoid penalizing peaceful nature destinations by comparing them directly to metropolitan centers, infrastructure supply is evaluated relative to each destination's specific peer cluster mean $\mu_C$:

$$Gap_{i, f} = \max(0, \, \mu_{C, f} - X_{i, f})$$

$$Overall\_Gap\_Score_i = \sum_{f} w_f \cdot \frac{Gap_{i, f}}{\sigma_{C, f}}$$

### 2×2 Strategic Opportunity Matrix:
Destinations are categorized into quadrants combining Infrastructure Deficit and 3-Year Visitor Growth:
1. **High Potential & Growing Demand:** High Deficit + Positive Growth ($Gap > 0 \land Growth > 0$) ➔ *Highest priority for new capital investment.*
2. **Undersupplied & Developing:** High Deficit + Negative Growth ($Gap > 0 \land Growth \le 0$) ➔ *Opportunity for targeted niche hospitality revival.*
3. **Established Market & Growing:** Low Deficit + Positive Growth ($Gap \le 0 \land Growth > 0$) ➔ *Mature market with room for premium/differentiated offerings.*
4. **Mature & Well-Established:** Low Deficit + Negative Growth ($Gap \le 0 \land Growth \le 0$) ➔ *Saturated market, quality upgrading recommended.*

---

## 4. Financial ROI & Payback Estimation

For any prospective hospitality or culinary enterprise:
* **Monthly Net Profit**:
  $$\text{Net Profit}_{\text{monthly}} = \text{Monthly Revenue} - \text{Monthly Expenses}$$
* **Annualized Net Profit**:
  $$\text{Net Profit}_{\text{annual}} = \text{Net Profit}_{\text{monthly}} \times 12$$
* **Simple Payback Period (Months)**:
  $$\text{Payback Months} = \frac{\text{Initial Capital Investment}}{\text{Net Profit}_{\text{monthly}}}$$
* **Annual Return on Investment (ROI %)**:
  $$\text{ROI} (\%) = \left(\frac{\text{Net Profit}_{\text{annual}}}{\text{Initial Capital Investment}}\right) \times 100$$
