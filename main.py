from selenium.webdriver.common.by import By  # Import the By class
from selenium.common.exceptions import NoSuchElementException

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
from bs4 import BeautifulSoup  # Import BeautifulSoup
import time
import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

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

imap_ssl_host = "imap.gmail.com"
imap_ssl_port = 993
username = "samuelironkwec@gmail.com"

password = os.getenv("GMAIL_PASSWORD")


import time


def getEmailCode():
    time.sleep(4)
    # Connect to Gmail IMAP server
    with imaplib.IMAP4_SSL(imap_ssl_host) as mail:
        # Log in to the Gmail account using App Password
        mail.login(username, password)

        # Select the 'inbox' folder
        mail.select("inbox")

        # Search for all emails in the 'inbox'
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()

        for email_id in reversed(email_ids):
            # Fetch the email using its ID
            result, message_data = mail.fetch(email_id, "(RFC822)")

            if result == "OK":
                # Decode the email message
                msg = email.message_from_bytes(message_data[0][1])

                # Extract the subject
                subject, encoding = decode_header(msg["Subject"])[0]

                # Check if the subject matches the desired subject
                if subject and "Your Uber account verification code" in subject:
                    # Get the body of the email
                    email_body = msg.get_payload(decode=True).decode("utf-8")

                    # Extract the verification code using BeautifulSoup
                    soup = BeautifulSoup(email_body, "html.parser")
                    number_element = soup.find("td", class_="p2b")

                    if number_element:
                        code_value = number_element.text.strip()
                        print("Verification Code:", code_value)

                        # Exit the loop after finding the first email with the desired subject
                        return code_value
            else:
                print("Error fetching the most recent email.")

    print("No verification code found after multiple attempts.")
    return None


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


def login():
    print("########### Signing in to Uber Webpage")

    # vehicle type doesnt need to  be defined
    vehicle_type = ""

    # Generate the Uber Selection URL
    uber_selection_url = generate_uber_url(drop_location, pickup_location, vehicle_type)

    try:
        driver.get(uber_selection_url)

    except:
        print("ERROR: Did not get Link")
        pass
    # time.sleep(50)

    email_input = driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS")
    email_input.send_keys("samuelironkwec@gmail.com")

    continue_button = driver.find_element(By.ID, "forward-button")
    continue_button.click()
    verification_code = getEmailCode()

    # after clicking continue, get the code from gmail
    # print(code)
    otp_input_ids = [
        "EMAIL_OTP_CODE-0",
        "EMAIL_OTP_CODE-1",
        "EMAIL_OTP_CODE-2",
        "EMAIL_OTP_CODE-3",
    ]
    for i in range(min(len(verification_code), len(otp_input_ids))):
        otp_input = driver.find_element(By.ID, otp_input_ids[i])
        otp_input.send_keys(verification_code[i])
    continue_button = driver.find_element(By.ID, "forward-button")
    # Click the forward button
    continue_button.click()


def download():
    # get the data
    print("########### Fetching Elements from Uber Webpage")
    try:
        price = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/div/div[1]/div/main/div/section/div[2]/ul/li[1]/div[2]/div/div[1]/div",
                )
            )
        )
        return price

        # Write the formatted page source to a file
    except Exception as e:
        print(f"Error retrieving data: {e}")


if __name__ == "__main__":
    # Check if the element is found
    vehicle_type = "UberX"
    uber_selection_url = generate_uber_url(drop_location, pickup_location, vehicle_type)
    try:
        driver.get(uber_selection_url)

    except:
        print("ERROR: Did not get Link")
        pass

    try:
        # Check for the presence of the element
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/div/div[1]/div/main/div/section/div[2]/ul/li[1]/div[2]/div/div[1]/div",
                )
            )
        )
        # If the element is found, download directly
        price = download()
        print("trip price: " + price.text)
        #time.sleep(1000)
    except Exception as e:
        # If the element is not found, assume not logged in, then login and download
        login()
        price = download()
        print("trip price: " + price.text)
