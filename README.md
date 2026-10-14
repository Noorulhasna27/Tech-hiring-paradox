# The Tech Hiring Paradox
**Uncovering the skill gap and experience barrier behind modern tech unemployment**

An end-to-end data science capstone project analyzing over 2,000 Indian tech job postings collected via the Adzuna API. This project investigates market demand, salary distributions, key skill requirements, and hiring trends across various tech domains and experience tiers in India.
## Problem Statement 
Is tech unemployment driven by a shortage of job openings, or by a structural mismatch between the skills companies demand and the skills job seekers have?

## Approach
1. **Data collection:** Adzuna Jobs API (India), 8 keyword searches (4 specialized, 4 legacy roles), 2,000 raw records
2. **Cleaning:** removed 247 duplicates and 43 incomplete rows, giving 1,710 records; engineered skill-count features from job descriptions
3. **EDA:** salary, skill vocabulary, hiring trend, and salary transparency by tier
4. **Modeling:** Logistic Regression and Decision Tree, both implemented from scratch with NumPy
5. **Dashboard:** 4-page interactive Power BI report with drill-through and row-level security

## Key Findings
| | Specialized | Legacy |
|---|---|---|
| Postings | 909 (53.2%) | 801 (46.8%) |
| Avg. disclosed salary | ₹14.79 L | ₹6.56 L |
| Salary disclosure rate | 15.9% | 50.8% |
| Trend over collection window | +82.3% | −49.7% |

- Job volume is balanced between tiers, so the issue isn't scarcity of openings
- The tiers share **zero overlap** in their top-10 skills; skill *identity*, not skill *count*, separates them
- Specialized roles pay ~2.25x more than legacy roles

## Model Results (341-row test set)
| Model | Accuracy | Precision | Recall |
|---|---|---|---|
| Logistic Regression | 86.5% | 82.6% | 94.5% |
| Decision Tree | 86.8% | 87.4% | 87.8% |

![Confusion matrices](images/model_confusion_matrices.png)
![Feature importance](images/model_feature_importance.png)

## Repo Structure
- `src/`: scraping (`webScraping.py`) and cleaning (`cleaned.py`) scripts
- `notebooks/`: `Eda.ipynb`, `Model.ipynb`
- `data/`: raw, cleaned, and prediction CSVs
- `dashboard/`: `Dashboard.pbix` (open with Power BI Desktop)
- `report/`: full project report (PDF)

## Run It Yourself
```bash
pip install -r requirements.txt
export ADZUNA_APP_ID="your_id"
export ADZUNA_APP_KEY="your_key"
python src/webScraping.py
python src/cleaned.py
```
Get free API keys at developer.adzuna.com.

## Author
A. Noorul Hasna: Data Science & Analytics Professional
