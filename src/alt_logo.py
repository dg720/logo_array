import os
import requests
import pandas as pd
import time
from googlesearch import search
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
import random
import retrying


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


@retrying.retry(stop_max_attempt_number=5, wait_fixed=2000)
def download_logo(company_url, company_name, save_path="logos"):
    """Downloads the company logo from Brandfetch with retries."""
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
        content_type = response.headers["Content-Type"]
        extension = content_type.split("/")[-1]  # Extract the file extension

        if extension == "webp":
            extension = "png"  # Convert WEBP to PNG for better compatibility

        file_path = os.path.join(save_path, f"{company_name}.{extension}")

        # Save the image as raw bytes first
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"Logo saved for {company_name}: {file_path}")
    else:
        print(f"Invalid content type or failed request for {company_name}. Retrying...")
        raise Exception("Failed request")


def main(csv_path):
    """Main function to process the CSV and download logos."""
    df = pd.read_csv(csv_path)
    if "Company" not in df.columns:
        print("CSV must contain a 'Company' column.")
        return

    os.makedirs("logos", exist_ok=True)  # Ensure the logos directory exists

    for company in df["Company"].dropna():
        existing_files = os.listdir("logos")

        if any(company in file for file in existing_files):
            print(f"Skipping {company}, logo already exists.")
            continue

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
