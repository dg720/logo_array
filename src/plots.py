import os
import requests
import pandas as pd
import time
from googlesearch import search
from urllib.parse import urlparse
import random


def get_company_website(company_name):
    """Performs a Google search to find the official website of the company."""
    query = f"{company_name} official site"
    for result in search(query):
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


def download_logo(company_url, company_name, save_path="logos"):
    """Downloads the company logo from Brandfetch."""
    api_key = "1ido2FzbOBCMRcIuMAs"
    logo_url = f"https://cdn.brandfetch.io/{company_url}/w/512/h/94/logo?c={api_key}"

    print(f"Fetching logo from: {logo_url}")

    headers = {
        "User-Agent": random.choice(
            [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            ]
        ),
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://brandfetch.io/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    response = requests.get(
        logo_url, headers=headers, allow_redirects=True, stream=True
    )

    if response.status_code == 200 and "image" in response.headers.get(
        "Content-Type", ""
    ):
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, f"{company_name}.png")

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"Logo saved for {company_name}: {file_path}")
    else:
        print(f"Failed to download logo for {company_name}.")


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
                print(f"Extracted domain: {domain}")
                download_logo(domain, company)
        time.sleep(random.uniform(1, 3))  # Randomized sleep to avoid rate limits


if __name__ == "__main__":
    main("companies.csv")
