from selenium.webdriver.common.by import By  # Import the By class

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import json
import numpy as np
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

username = "bteardg7tn@privaterelay.appleid.com"

options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=/Users/sam/Documents/uber-price/userProfile")
# add here any tag you want.
#
# options.add_argument("--headless")  # Add this line for headless mode
options.add_argument(
    "--window-size=600,600"
)  # Replace with your desired width and height

options.add_experimental_option(
    "excludeSwitches",
    [
        "ignore-certificate-errors",
        "safebrowsing-disable-download-protection",
        "safebrowsing-disable-auto-update",
        "disable-client-side-phishing-detection",
    ],
)
# LINK TO Chromediver goes here (Need to change)
chromedriver = "C:/Users/Home Admin/Desktop/uber_local_scrape/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(options=options)


def getEmailCode():
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    SERVICE_ACCOUNT_FILE = "/Users/sam/Documents/fitpal-397800-29cc4dd68dd5.json"  # Update this with the actual path

    # Load the service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # Build the Gmail API service
    service = build("gmail", "v1", credentials=credentials)

    # ...

    try:
        # Retrieve a list of messages
        results = service.users().messages().list(userId="me").execute()
        messages = results.get("messages", [])

        # Print message details
        for message in messages:
            msg = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            print(msg["snippet"])
    except HttpError as error:
        print(f"An error occurred: {error.content}")


def generate_uber_url(drop, pickup, vehicle):
    # Uber Selection URL
    base_url = "https://m.uber.com/go/product-selection"

    # Constructing the URL parameters
    drop_param = f"drop[0]={json.dumps(drop)}"
    pickup_param = f"pickup={json.dumps(pickup)}"
    vehicle_param = f"vehicle={vehicle}"

    # Constructing the complete URL
    uber_url = f"{base_url}?{drop_param}&{pickup_param}&{vehicle_param}"

    return uber_url


# Example data (replace with your own random data)
drop_location = {
    "addressLine1": "80 Bison Dr",
    "addressLine2": "Winnipeg, Manitoba R3T 4Z7",
    "id": "3aafb376-6f73-d4f7-1139-4d7fcd87d3ba",
    "source": "SEARCH",
    "latitude": 49.8011215,
    "longitude": -97.1622077,
    "provider": "uber_places",
}

pickup_location = {
    "addressLine1": "2525 Pembina Hwy",
    "addressLine2": "Winnipeg, Manitoba R3T 6H3",
    "id": "3037dafa-cf26-e6b4-2614-c648fde19de8",
    "source": "SEARCH",
    "latitude": 49.800397,
    "longitude": -97.157845,
    "provider": "uber_places",
}


def download():
# vehicle type doesnt need to  be defined
    vehicle_type = ""

    # Generate the Uber Selection URL
    uber_selection_url = generate_uber_url(drop_location, pickup_location, vehicle_type)
    try:
        driver.get(uber_selection_url)
        # Add this after driver.get(uber_selection_url)
        with open("source.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        print(f"Page source saved to source.html")

    except:
        print("ERROR: Did not get Link")
        pass

    temp = []

    print("########### Fetching Elements from Uber Webpage")

    try:
        price = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_css-bIszFv"))
        )

        # Write the formatted page source to a file
    except Exception as e:
        print(f"Error saving page source: {e}")

    return temp


if __name__ == "__main__":
    data = getEmailCode()
