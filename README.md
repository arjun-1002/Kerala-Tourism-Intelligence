# Kerala Tourism Intelligence & Business Opportunity Platform

An end-to-end data science pipeline and interactive Flask web application analyzing **25 major tourist destinations across Kerala**. The project combines visitor footfall growth (2022–2024), accommodation & hospitality supply counts, Google Trends India search demand (2021–2026), K-Means destination segmentation, infrastructure gap scoring, and ROI profitability estimation for tourism entrepreneurs.

Main Repo Link: https://github.com/arjun-1002/Kerala-Tourism-Intelligence
WEBSITE LINK: https://kerala-tourism-business-intelligence-1.onrender.com/
---

## 🚀 Quick Start (Easiest Way to Run)

Anyone downloading or cloning this repository can launch the full application with **zero manual environment setup**:

### 🪟 Windows (1-Click Run)
Simply double-click **`run.bat`** (or execute `.\run.bat` in PowerShell / Command Prompt).
> `run.bat` automatically detects Python (or Anaconda), verifies dependencies, creates an isolated virtual environment (`.venv`) if needed, starts the web server, and automatically opens **`http://127.0.0.1:5000`** in your browser.

### 🍎 macOS & 🐧 Linux (1-Click Run)
Open your terminal in the project folder and run:
```bash
chmod +x run.sh
./run.sh
```

---

## 💻 Manual Setup & Execution (Any Platform)

If you prefer to configure and run the project manually:

```bash
# 1. Clone or download repository
git clone https://github.com/arjun-1002/Kerala-Tourism-Intelligence.git
cd Kerala-Tourism-Intelligence

# 2. Create and activate a virtual environment
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the web platform
python app.py
```
Then open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 📁 Clean & Structured Repository Architecture

The repository is organized into a clean, numbered 12-stage pipeline with **zero duplicate files**:

```text
Kerala-Tourism-Intelligence/
├── 01_Data_Collection/       # Raw reference PDFs, official government reports & audit screenshots
├── 02_Raw_Data/              # Unprocessed raw CSVs (hospitality supply, ratings, Google Trends raw long format)
├── 03_Cleaned_Data/          # Master 25-destination dataset & cleaned conflict-free Google Trends CSV
├── 04_Notebooks/             # Exploratory Jupyter notebooks (01 through 04 research archive)
├── 05_Source_Code/           # Modular production Python pipeline separated by stage
├── 06_EDA_Analysis/          # Visitor growth tables & Google Trends category/coverage summaries
├── 07_Machine_Learning/      # StandardScaler & RobustScaler K-Means cluster assignments
├── 08_Results/               # Cluster profiles, model comparisons, gap rankings & opportunity recommendations
├── 09_Visualizations/        # High-resolution generated charts (elbow curve, clusters, visitor growth)
├── 10_Documentation/         # Comprehensive Data Dictionary & Analytical Methodology guides
├── 11_Presentation/          # Executive 10-slide PowerPoint deck (.pptx) & presentation generator scripts
├── 12_Frontend/              # Full Flask web dashboard (Jinja2 templates, custom CSS, JS, destination photos)
├── .gitignore                # Comprehensive exclusions (.venv, __pycache__, temp files)
├── app.py                    # Root entrypoint to launch web platform
├── requirements.txt          # Universal Python dependencies
├── run.bat                   # 1-Click Windows launcher
├── run.ps1                   # 1-Click PowerShell launcher
├── run.sh                    # 1-Click macOS/Linux launcher
└── README.md                 # Complete project documentation (this file)
```

---

## 🔬 Modular Python Pipeline (`05_Source_Code/`)

The analytics codebase is refactored into single-responsibility Python modules inside `05_Source_Code/`. Every script defaults to **dry-run mode** so existing datasets are never modified unless `--save` is passed:

| Script | Responsibility | Output Directory |
| :--- | :--- | :--- |
| `05_Source_Code/data_loading.py` | Project root path resolution, master dataset loading, and missing/duplicate inspection. | `03_Cleaned_Data/` |
| `05_Source_Code/preprocessing.py` | Zero-to-NaN supply cleaning, median imputation, StandardScaler & RobustScaler over 8 features. | `07_Machine_Learning/` |
| `05_Source_Code/clustering.py` | Elbow WCSS (`k=1..10`), Silhouette sweep (`k=2..8`), `KMeans(k=3)` across 3 scaling regimes. | `07_Machine_Learning/`, `08_Results/`, `09_Visualizations/` |
| `05_Source_Code/visitor_growth_analysis.py` | Computes 3-year growth (`2022–2024`), audits estimation notes into `Data_Quality`, plots growth rankings. | `06_EDA_Analysis/`, `09_Visualizations/` |
| `05_Source_Code/google_trends_analysis.py` | Standardizes search pillars, isolates 5 ambiguous duplicate-key terms (`610` rows -> `29,585` clean rows). | `03_Cleaned_Data/`, `06_EDA_Analysis/` |
| `05_Source_Code/business_opportunities.py` | Computes cluster-relative infrastructure deficits (`Overall_Gap_Score`) and 2x2 opportunity quadrants. | `08_Results/` |
| `05_Source_Code/profitability_estimator.py` | Simulates monthly profit, annual ROI (%), payback period, and 5-year cumulative cash flows. | `08_Results/` |
| `05_Source_Code/run_pipeline.py` | Orchestrates all 7 pipeline stages sequentially in one command (`--save` optional). | End-to-end |

```powershell
# Run full pipeline with --save to refresh models, metrics, and plots:
python 05_Source_Code\run_pipeline.py --save
```

---

## 📊 Analytical Methodology & Model Benchmarking

### 1. Feature Engineering & K-Means Segmentation
Clustering operates on 8 numerical infrastructure, rating, and accessibility features across all **25 destinations**:
* `Attraction_Count`, `Hotels`, `Resorts`, `Homestays_Vacation_Rentals`, `Restaurants`
* `Hotels_Average_Rating`, `Resorts_Average_Rating`, `Nearest_Airport_Distance_km_numeric`

Three `KMeans(n_clusters=3, random_state=42)` configurations are evaluated:

| Model Configuration | Feature Space | Silhouette Score | Davies-Bouldin | Calinski-Harabasz | Role |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **StandardScaler + K-Means** | Original 8 features | **0.3899** | 0.9875 | 15.35 | Primary business segmentation model |
| **RobustScaler + K-Means** | Original 8 features | **0.5804** | 0.6431 | 28.21 | Outlier-resistant comparison |
| **RobustScaler + PCA + K-Means** | 2 PCA components | **0.6799** | 0.5692 | 45.81 | Dimensionality reduction & 2D projection |

### 2. Destination Clusters
* **Cluster 0: Urban Tourism & Commercial Hubs (3 destinations):** Kochi City, Kozhikode City, Thiruvananthapuram City.
* **Cluster 1: Developing & Nature-Based Destinations (14 destinations):** Vagamon, Ponmudi, Thenmala, Konni, Ranipuram, etc.
* **Cluster 2: Established Leisure & Resort Destinations (8 destinations):** Munnar, Wayanad, Kovalam, Varkala, Kumarakom, Alappuzha, Thekkady, Bekal.

### 3. Business Opportunity Quadrants
Destinations are categorized into a 2×2 matrix combining cluster-relative Infrastructure Gap Scores and 3-Year Visitor Growth:
* **High Potential & Growing Demand (14 destinations):** Highest capital investment priority (Top: Kozhikode City `130.08`, Kumarakom `94.12`, Vagamon `67.38`).
* **Undersupplied & Developing (1 destination):** Low footfall but acute infrastructure gaps.
* **Established Market & Growing (8 destinations):** Steady growth; ideal for premium differentiation.
* **Mature & Well-Established (2 destinations):** Saturated markets where quality renovation is favored.

---

## 🌐 Interactive Web Application (`12_Frontend/`)

The dashboard is built with **Flask**, **Jinja2**, **Chart.js / Plotly**, and tailored destination imagery across 11 dedicated pages:

| Route | Purpose |
| :--- | :--- |
| `/` | Executive dashboard with Kerala KPIs, cluster spotlight, and interactive Google Trends demand curve |
| `/destinations` | Directory cards & detail modals across all 25 destinations with tailored sector concepts |
| `/tourism-analysis` | Deep-dive infrastructure supply, rating benchmarks, and visitor footfall analytics |
| `/clustering` | Machine learning cluster profiles and Silhouette Score comparison across scaling modes |
| `/opportunities` | 4-Quadrant strategic matrix and top-ranked commercial venture recommendations |
| `/google-trends` | Multi-pillar Google Trends search interest analysis across `1y`, `3y`, and `All-time` periods |
| `/comparison` | Side-by-side head-to-head comparison between any two destinations |
| `/calculator` | Interactive hospitality ROI simulator with 5-year cumulative cash-flow projections |
| `/culture-guide` | Kerala cultural heritage guide (arts, festivals, boat races, Malabar cuisine, Ayurveda) |
| `/about` | Project background, data sources, and methodology summary |
| `/api/*` | REST endpoints for destination details, trend series, and financial calculations |

---

## 📚 Supporting Documentation
* **[Data Dictionary](10_Documentation/DATA_DICTIONARY.md)** — Complete feature specifications and column descriptions.
* **[Analytical Methodology](10_Documentation/METHODOLOGY.md)** — Mathematical formulations, clustering validation, and ROI calculation equations.

---

## 📤 Pushing Changes to GitHub

To push the latest structured code to your GitHub repository:
```powershell
git add .
git commit -m "Organize folder architecture, remove duplicate files, and add documentation"
git push origin main
```
*Or open **GitHub Desktop** and click **Push origin**.*
