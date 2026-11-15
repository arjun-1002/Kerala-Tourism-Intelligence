# Kerala Tourism Intelligence & Business Opportunity Platform

An end-to-end data science pipeline and interactive Flask web application analyzing **25 major tourist destinations across Kerala**. The project combines visitor footfall growth (2022–2024), accommodation & hospitality supply counts, Google Trends India search demand (2021–2026), K-Means destination segmentation, infrastructure gap scoring, and ROI profitability estimation for tourism entrepreneurs.

---

## 🚀 Quick Start (Easiest Way to Run)

Anyone downloading or cloning this repository can run the application with **zero manual environment setup**:

### 🪟 Windows (1-Click Run)
Simply double-click **`run.bat`** (or execute `.\run.bat` in PowerShell / Command Prompt).
> `run.bat` automatically detects Python, creates a fresh virtual environment (`.venv`), installs all dependencies from `requirements.txt`, starts the web server, and opens **`http://127.0.0.1:5000`** in your default browser.

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
# 1. Clone the repository
git clone https://github.com/arjun-1002/Kerala-Tourism-Intelligence.git
cd Kerala-Tourism-Intelligence

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Launch the web platform
python app.py
```
Then open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 📦 GitHub & Upload Guidelines

### ⚠️ Why `.venv` and `.git` Are NOT Uploaded Directly
- **`.venv` (Virtual Environment):** Contains 400MB+ of operating-system-specific compiled binaries and hardcoded local file paths (e.g. `C:\Users\...`). If `.venv` is uploaded to GitHub and downloaded on another computer, Python commands will fail with `No Python at '...'`. The `.gitignore` file intentionally excludes `.venv/`. Instead, each user generates their own local environment instantly using `run.bat` or `python -m venv .venv`.
- **`.git` (Version Control):** The `.git` folder stores Git's internal commit database and should never be manually zipped, copied, or uploaded through GitHub's web interface (which rejects hidden folders). Git communicates directly with GitHub via `git push`. Do not create a duplicate folder named `git/`.

### 📤 How to Push Updates to GitHub

#### Option A: Using Git Command Line (Recommended)
```bash
# 1. Check modified files
git status

# 2. Stage all project files (ignoring .venv automatically)
git add .

# 3. Commit your changes
git commit -m "Add root runner, requirements, and update documentation"

# 4. Push to GitHub
git push origin main
```

#### Option B: Using GitHub Desktop
1. Open **GitHub Desktop**.
2. Click **File** -> **Add Local Repository** -> Select this folder (`Kerala-Tourism-Intelligence Updates`).
3. You will see all modified code and newly added files (`app.py`, `run.bat`, `run.sh`, `requirements.txt`). `.venv` is automatically ignored.
4. Type a summary in the bottom-left box and click **Commit to main**.
5. Click **Push origin** in the top bar.

---

## Project Architecture

```text
TOURISM INTELLIGENCE/
├── 01_Data_Collection/       # Raw reference PDFs, scraped stays data & audit screenshots
├── 02_Raw_Data/              # Raw CSVs (business counts, ratings, coordinates, transport, Google Trends)
├── 03_Cleaned_Data/          # Master 25-destination dataset & cleaned Google Trends CSV
├── 04_Notebooks/             # Exploratory Jupyter notebooks (01 through 04, kept as archive)
├── 05_Source_Code/           # Modular, production-ready Python pipeline separated by stage
├── 06_EDA_Analysis/          # Visitor growth tables & Google Trends category/coverage summaries
├── 07_Machine_Learning/      # StandardScaler & RobustScaler K-Means cluster assignments
├── 08_Results/               # Cluster profiles, model comparisons, gap rankings & recommendations
├── 09_Visualizations/        # Generated charts (optional --save output from pipeline)
├── 10_Documentation/         # Supporting documentation folder
├── 11_Presentation/          # Presentation materials folder
├── 12_Frontend/              # Interactive Flask web application & REST JSON endpoints
├── .gitignore                # Comprehensive git exclusions (.venv, __pycache__, etc.)
├── app.py                    # Root entry point to launch the web platform
├── requirements.txt          # Universal Python dependencies
├── run.bat                   # 1-Click Windows launcher (auto-installs & launches)
├── run.ps1                   # 1-Click PowerShell launcher
├── run.sh                    # 1-Click macOS/Linux launcher
└── README.md                 # Project documentation (this file)
```

---

## Modular Python Pipeline (`05_Source_Code/`)

The code from `04_Notebooks/` has been refactored into single-responsibility Python modules inside `05_Source_Code/`. Every script defaults to **dry-run mode** so existing datasets are never overwritten unless `--save` is passed.

| Script | Responsibility | Source Notebook & Cells |
| :--- | :--- | :--- |
| `05_Source_Code/data_loading.py` | Project path resolution (`PROJECT_ROOT`), master dataset loading, shape/missing/duplicate inspection. | `01_data_loading.ipynb` (Cells 0–8) |
| `05_Source_Code/preprocessing.py` | Zero-to-NaN supply cleaning (`Hotels`, `Resorts`, `Homestays_Vacation_Rentals`), median `SimpleImputer`, `StandardScaler`, and `RobustScaler` over 8 ML features. | `02_data_cleaning.ipynb` (Cells 0–23, 56) |
| `05_Source_Code/clustering.py` | Elbow WCSS (`k=1..10`), Silhouette sweep (`k=2..8`), `KMeans(k=3)` across `StandardScaler`, `RobustScaler`, and `RobustScaler + PCA(2)`, plus cluster profiles. | `02_data_cleaning.ipynb` (Cells 24–35, 56–80) |
| `05_Source_Code/visitor_growth_analysis.py` | Computes `Growth_2022_2024`, audits `Visitor_Estimation_Note_{year}` into `Data_Quality`, and plots horizontal growth bars. | `02_data_cleaning.ipynb` (Cells 41–45) |
| `05_Source_Code/google_trends_analysis.py` | Standardizes `Category`/`Destination`, isolates 5 unresolved duplicate-key search terms (`610` rows -> `29,585` cleaned rows), and summarizes categories & normalization groups. | `03_google_trends_analysis.ipynb` (Cells 0–51) |
| `05_Source_Code/business_opportunities.py` | Computes cluster-relative infrastructure deficits (`Overall_Gap_Score`), 2x2 opportunity quadrants (`classify_opportunity`), and statewide gap recommendations (`get_best_recommendation`). | `02_data_cleaning.ipynb` & `04_profitability_estimator.ipynb` |
| `05_Source_Code/profitability_estimator.py` | `calculate_profitability`, `get_destination_details`, `tourism_business_estimator`, and 2-destination comparison table & chart. | `04_profitability_estimator.ipynb` (Cells 14–24, 29–34) |
| `05_Source_Code/run_pipeline.py` | Runs all 7 pipeline stages sequentially in one command (`--save` optional). | Full `01`–`04` workflow |

```powershell
# Full end-to-end dry-run (verifies all 7 stages without overwriting CSVs/plots)
python 05_Source_Code\run_pipeline.py

# Or run any individual stage
python 05_Source_Code\data_loading.py
python 05_Source_Code\preprocessing.py
python 05_Source_Code\clustering.py
python 05_Source_Code\visitor_growth_analysis.py
python 05_Source_Code\google_trends_analysis.py
python 05_Source_Code\business_opportunities.py
python 05_Source_Code\profitability_estimator.py --destination Kumarakom --compare-with Munnar
```

---

## Key Methodology & Analytical Results

### 1. Feature Engineering & K-Means Segmentation
Clustering operates on 8 numerical infrastructure, rating, and accessibility features across all **25 destinations**:
- `Attraction_Count`, `Hotels`, `Resorts`, `Homestays_Vacation_Rentals`, `Restaurants`
- `Hotels_Average_Rating`, `Resorts_Average_Rating`, `Nearest_Airport_Distance_km_numeric`

Three `KMeans(n_clusters=3, random_state=42, n_init=10)` configurations are evaluated:

| Model Configuration | Evaluation Space | Silhouette Score | Role |
| :--- | :--- | :---: | :--- |
| **StandardScaler + K-Means** | Original 8 features | **0.3899** | Primary business segmentation model |
| **RobustScaler + K-Means** | Original 8 features | **0.5804** | Outlier-resistant comparison |
| **RobustScaler + PCA + K-Means** | 2 PCA components | **0.6799** | Dimensionality reduction & 2D projection |

Primary `StandardScaler` clusters:
- **Cluster 0 (3 destinations):** *Urban Tourism and Commercial Hubs*
- **Cluster 1 (14 destinations):** *Developing and Nature-Based Destinations*
- **Cluster 2 (8 destinations):** *Established Leisure and Resort Destinations*

### 2. Visitor Growth & Estimation Audit (2022–2024)
- **Top Growth Destination:** Munnar (**+109.21%**)
- **Data Quality Breakdown:** `16` destinations contain at least one yearly estimation note (`"Contains estimates"`), while `9` destinations have no estimation notes (`"No estimation notes"`).

### 3. Google Trends India Analysis
- **Raw Master Records:** `30,195` rows across 4 normalization groups (`accommodation`, `food`, `activities`, `destination_interest`).
- **Duplicate Resolution:** `5` ambiguous duplicate-key search terms (`hotels in athirappilly`, `malampuzha garden`, `malampuzha ropeway`, `hotels in malampuzha`, `konni elephant training centre` — `610` rows) were isolated into `02_Raw_Data/google_trends_unresolved_records.csv`.
- **Cleaned Working Dataset:** `29,585` conflict-free monthly records (`03_Cleaned_Data/google_trends_clean.csv`).

### 4. Business Opportunity Scoring
Opportunities are evaluated through two complementary lenses:
- **Cluster-Relative Deficit (`Overall_Gap_Score`):** Compares each destination's supply against its own peer cluster mean (Top cluster-relative gaps: **Kozhikode City** `130.08`, **Kumarakom** `94.12`, **Vagamon** `67.38`).
- **2×2 Opportunity Quadrants:** Combines gap sign and `Growth_2022_2024` (`High Gap + Positive Growth` = `14`, `Low Gap + Positive Growth` = `8`, `Low Gap + Negative Growth` = `2`, `High Gap + Negative Growth` = `1`).
- **Statewide Gap Highlights:** Identifies underserved Homestay/Restaurant segments in emerging corridors (e.g., Thalassery, Palaruvi, Silent Valley with `212.48` Homestay gap below statewide mean).

---

## Interactive Flask Web Application (`12_Frontend/`)

The user-facing web dashboard is built with **Flask**, **Jinja2**, **Chart.js / Plotly**, custom SVG branding (`static/images/logo.svg`), and tailored destination imagery.

### Available Web Pages & API Endpoints

| Route | Purpose |
| :--- | :--- |
| `/` | Home dashboard with Kerala KPIs, cluster spotlight, and interactive Google Trends demand curve |
| `/destinations` | Explorer cards & detail modals across all 25 destinations with tailored recommendations |
| `/tourism-analysis` | Deep-dive infrastructure & visitor footfall growth metrics across destinations |
| `/clustering` | Cluster breakdown and Silhouette Score comparison across the 3 scaling/PCA modes |
| `/opportunities` | Business opportunity quadrant ranking and rich destination business concepts |
| `/google-trends` | Detailed India Google Trends analysis across 4 demand pillars (`All`, `1y`, `3y`, `All-time`) |
| `/comparison` | Side-by-side infrastructure, rating, growth, and gap comparison between two destinations |
| `/calculator` | Interactive Tourism Business ROI & 5-year cash-flow simulator with destination presets |
| `/culture-guide` | Kerala cultural & seasonal travel context guide |
| `/about` | Project background, data sources, and methodology summary |
| `/api/destination/<name>` | JSON profile and enriched business recommendation for a destination |
| `/api/trends/<name>` | JSON destination interest series (`?period=1y\|3y\|all`) |
| `/api/google-trends/<name>` | JSON multi-pillar series & keyword breakdown (`?pillar=...&period=...`) |
| `/api/calculate-profitability` | `POST` endpoint returning monthly/annual profit, payback months, ROI %, and 5-year cash flow |

---

## Limitations & Data Notes
- **Visitor Data Estimates:** 16 of 25 destinations include official/derived estimation notes for one or more years (`2022`–`2024`), flagged explicitly via `Data_Quality`.
- **Zero-Supply Handling:** Unrecorded counts (`0`) in raw Hotel, Resort, and Homestay columns are median-imputed prior to ML clustering, while statewide raw averages retain true table means.
- **Financial Projections:** Profitability calculator figures (`ROI %`, payback months, 5-year cash flow) depend on user-supplied or preset revenue/expense assumptions and should be paired with local feasibility due diligence.
