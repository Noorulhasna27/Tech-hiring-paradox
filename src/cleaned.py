

import re
import pandas as pd

INPUT_FILE = "adzuna_raw_jobs.csv"
OUTPUT_FILE = "cleaned_jobs.csv"



SPECIALIZED_KEYWORDS = [
    "python", "machine learning", "deep learning", "tensorflow", "pytorch",
    "nlp", "natural language processing", "computer vision", "aws", "azure",
    "gcp", "google cloud", "cloud", "kubernetes", "docker", "airflow",
    "spark", "hadoop", "data science", "data scientist", "sql", "nosql",
    "mongodb", "generative ai", "llm", "genai", "mlops", "big data",
    "scikit-learn", "keras", "tableau", "power bi", "data engineering",
    "data analytics", "data analysis", "statistics", "statistical",
    "predictive model", "predictive analytics", "ai", "artificial intelligence",
    "neural network", "model deployment", "etl", "data pipeline",
    "data warehouse", "snowflake", "databricks", "devops", "ci/cd",
    "terraform", "microservices", "api", "r programming", "pandas", "numpy",
]

LEGACY_KEYWORDS = [
    "php", "java", "javascript", "html", "css", "wordpress", "jquery",
    ".net", "c#", "vb.net", "helpdesk", "help desk", "troubleshooting",
    "windows server", "active directory", "networking", "hardware",
    "excel", "ms office", "customer support", "technical support",
    "desktop support", "software developer", "software development",
    "web development", "front end", "frontend", "back end", "backend",
    "full stack", "mysql", "linux", "bootstrap", "react", "angular",
    "node.js", "software engineer", "maintenance", "installation",
    "system administration", "it support",
]

SKILL_KEYWORDS = SPECIALIZED_KEYWORDS + LEGACY_KEYWORDS


def load_data(filename):
    df = pd.read_csv(filename)
    print(f"Loaded {len(df)} raw rows")
    return df


def drop_duplicates(df):
    before = len(df)
    df = df.drop_duplicates(subset=["job_title", "company", "location"], keep="first")
    print(f"Removed {before - len(df)} duplicate rows -> {len(df)} remaining")
    return df


def clean_text_fields(df):
    text_cols = ["job_title", "company", "location", "category", "contract_type"]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    
    df["contract_type"] = df["contract_type"].replace("", "Not specified")
    return df


def standardize_location(df):
    
    df["location_clean"] = df["location"].apply(
        lambda x: "Not specified / Remote" if x.strip().lower() == "india" or x.strip() == "" else x
    )
    return df


def handle_missing_salary(df):
    df["salary_disclosed"] = df["salary_min"].notna() & (df["salary_min"] != "")
    df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
    df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")
    df["salary_avg"] = df[["salary_min", "salary_max"]].mean(axis=1)
    print(f"Salary disclosed: {df['salary_disclosed'].sum()} / {len(df)} "
          f"({df['salary_disclosed'].mean() * 100:.1f}%)")
    return df


def parse_dates(df):
    df["posted_date"] = pd.to_datetime(df["created"], errors="coerce")
    return df


def extract_skills(df):
    def find_skills(description, keyword_list):
        if not isinstance(description, str):
            return []
        desc_lower = description.lower()
        return [kw for kw in keyword_list if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower)]

    df["specialized_skills_found"] = df["description"].apply(lambda d: find_skills(d, SPECIALIZED_KEYWORDS))
    df["legacy_skills_found"] = df["description"].apply(lambda d: find_skills(d, LEGACY_KEYWORDS))

    df["extracted_skills"] = df.apply(
        lambda r: "; ".join(r["specialized_skills_found"] + r["legacy_skills_found"]), axis=1
    )
    df["specialized_skill_count"] = df["specialized_skills_found"].apply(len)
    df["legacy_skill_count"] = df["legacy_skills_found"].apply(len)
    df["skill_count"] = df["specialized_skill_count"] + df["legacy_skill_count"]

    print(f"Average skills extracted per posting: {df['skill_count'].mean():.2f}")
    print(f"Average specialized-skill count: {df['specialized_skill_count'].mean():.2f}")
    print(f"Average legacy-skill count: {df['legacy_skill_count'].mean():.2f}")
    return df


def add_text_and_encoded_features(df):
    
    df["description_length"] = df["description"].astype(str).apply(lambda x: len(x.split()))

   
    df["search_keyword_encoded"] = pd.factorize(df["search_keyword"])[0]
    return df


def drop_unusable_rows(df):
    before = len(df)
    
    df = df[(df["job_title"] != "") & (df["company"] != "")]
    print(f"Dropped {before - len(df)} rows missing title/company -> {len(df)} remaining")
    return df


def finalize_columns(df):
    
    keep_cols = [
        "search_keyword", "search_keyword_encoded", "tier_label", "job_title",
        "company", "location_clean", "salary_min", "salary_max", "salary_avg",
        "salary_disclosed", "category", "contract_type",
        "posted_date", "extracted_skills", "skill_count", "specialized_skill_count",
        "legacy_skill_count", "description_length", "job_url",
    ]
    return df[keep_cols].rename(columns={"location_clean": "location"})


def clean():
    df = load_data(INPUT_FILE)
    df = clean_text_fields(df)
    df = drop_duplicates(df)
    df = drop_unusable_rows(df)
    df = standardize_location(df)
    df = handle_missing_salary(df)
    df = parse_dates(df)
    df = extract_skills(df)
    df = add_text_and_encoded_features(df)
    df = finalize_columns(df)

  
    df = df.sort_values(
        by=["tier_label", "search_keyword", "salary_disclosed", "salary_avg"],
        ascending=[True, True, False, False],
    )

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved {len(df)} cleaned rows to {OUTPUT_FILE}")
    print("\nColumn overview:")
    print(df.dtypes)


if __name__ == "__main__":
    clean()
