import os
import requests
import pandas as pd
import re
import time
from googlesearch import search
from urllib.parse import urlparse


def get_company_website(company_name):
    """Performs a Google search to find the official website of the company."""
    query = f"{company_name} official site"
    for result in search(query, num_results=5):
        if "wikipedia" not in result and "linkedin" not in result:
            return result
    return None


def extract_domain(url):
    """Extracts the domain from a given URL."""
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace("www.", "")
    except:
        return None


def download_logo(domain, company_name, save_path="logos"):
    """Uses Clearbit's Logo API to fetch and download the logo with a higher resolution."""
    logo_url = f"https://logo.clearbit.com/{domain}?size=500"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(logo_url, headers=headers, stream=True)

    if response.status_code == 200:
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, f"{company_name}.png")
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Logo saved for {company_name}: {file_path}")
    else:
        print(f"Logo not found for {company_name} ({domain})")


def main(csv_path):
    """Main function to process the CSV and download logos."""
    df = pd.read_csv(csv_path)
    if "Company" not in df.columns:
        print("CSV must contain a 'Company' column.")
        return

    for company in df["Company"].dropna():
        print(f"Processing: {company}")
        website = get_company_website(company)
        if website:
            domain = extract_domain(website)
            if domain:
                download_logo(domain, company)
        time.sleep(1)  # Avoid rate limiting


if __name__ == "__main__":
    main("companies.csv")

# WORKING
