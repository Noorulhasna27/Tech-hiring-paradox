
import csv
import time
import requests


APP_ID = "ADZUNA API "
APP_KEY = "ADZUNA KEY"

COUNTRY = "in"   # India
RESULTS_PER_PAGE = 50   
PAGES_PER_KEYWORD = 5   


SEARCHES = {
    "data-scientist":     ("data scientist", "specialized"),
    "ai-engineer":        ("ai engineer", "specialized"),
    "cloud-engineer":     ("cloud engineer", "specialized"),
    "machine-learning":   ("machine learning engineer", "specialized"),
    "software-developer": ("software developer", "legacy"),
    "php-developer":      ("php developer", "legacy"),
    "it-support":         ("it support", "legacy"),
    "web-developer":      ("web developer", "legacy"),
}

OUTPUT_FILE = "adzuna_raw_jobs.csv"
BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
REQUEST_DELAY = 1.5   



def fetch_page(keyword, page):
    url = BASE_URL.format(country=COUNTRY, page=page)
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": keyword,
        "content-type": "application/json",
    }
    resp = requests.get(url, params=params, timeout=15)

    if resp.status_code != 200:
        print(f"  [!] Status {resp.status_code} for '{keyword}' page {page}: {resp.text[:200]}")
        return None

    return resp.json()


def extract_rows(data, keyword_tag, tier):
    rows = []
    for job in data.get("results", []):
        rows.append({
            "search_keyword": keyword_tag,
            "tier_label": tier,
            "job_title": job.get("title", ""),
            "company": job.get("company", {}).get("display_name", ""),
            "location": job.get("location", {}).get("display_name", ""),
            "salary_min": job.get("salary_min", ""),
            "salary_max": job.get("salary_max", ""),
            "category": job.get("category", {}).get("label", ""),
            "contract_type": job.get("contract_type", ""),
            "created": job.get("created", ""),
            "description": job.get("description", ""),
            "job_url": job.get("redirect_url", ""),
        })
    return rows


def scrape():
    all_rows = []

    for keyword_tag, (query, tier) in SEARCHES.items():
        print(f"\n=== Scraping keyword: {keyword_tag} ({tier}) ===")

        for page in range(1, PAGES_PER_KEYWORD + 1):
            print(f"  Fetching page {page} for '{query}'...")
            data = fetch_page(query, page)

            if data is None:
                break

            rows = extract_rows(data, keyword_tag, tier)
            print(f"    -> {len(rows)} jobs found")

            if not rows:
                print("    No more results, moving to next keyword.")
                break

            all_rows.extend(rows)
            time.sleep(REQUEST_DELAY)

    return all_rows


def save_csv(rows, filename):
    if not rows:
        print("No rows scraped — nothing to save.")
        return

    fieldnames = list(rows[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} raw records to {filename}")


if __name__ == "__main__":
    if APP_ID.startswith("PASTE") or APP_KEY.startswith("PASTE"):
        print("ERROR: Please paste your Adzuna APP_ID and APP_KEY at the top of this file first.")
    else:
        scraped_rows = scrape()
        save_csv(scraped_rows, OUTPUT_FILE)