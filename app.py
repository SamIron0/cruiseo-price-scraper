import uvicorn
from fastapi import FastAPI, Request
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse
import json
import os
import time
import imaplib
import email
from email.header import decode_header
from selenium import webdriver
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
global gmail, password

options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=./userProfile-1")
options.add_argument("--window-size=600,600")
options.add_experimental_option(
    "excludeSwitches",
    [
        "ignore-certificate-errors",
        "safebrowsing-disable-download-protection",
        "safebrowsing-disable-auto-update",
        "disable-client-side-phishing-detection",
    ],
)

# LINK TO Chromedriver goes here (Need to change)
chromedriver = "./chromedriver-mac-x64/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
chrome_driver_1 = webdriver.Chrome(options=options)

options2 = webdriver.ChromeOptions()
options2.add_argument("user-data-dir=./userProfile-2")
options2.add_argument("--window-size=600,600")
options2.add_experimental_option(
    "excludeSwitches",
    [
        "ignore-certificate-errors",
        "safebrowsing-disable-download-protection",
        "safebrowsing-disable-auto-update",
        "disable-client-side-phishing-detection",
    ],
)

chrome_driver_2 = webdriver.Chrome(options=options2)

from dotenv import load_dotenv

load_dotenv()

imap_ssl_host = "imap.gmail.com"
imap_ssl_port = 993
gmail2 = os.getenv("FATI_GMAIL")
gmail1 = os.getenv("TELA_GMAIL")
gmail3 = os.getenv("QUINCY_GMAIL")

password2 = os.getenv("FATI_GMAIL_PASSWORD")
password1 = os.getenv("TELA_GMAIL_PASSWORD")
password3 = os.getenv("QUINCY_GMAIL_PASSWORD")
gmail = gmail1
password = password1


def getEmailCode(driver, gmail, password):
    time.sleep(4)
    # Connect to Gmail IMAP server
    with imaplib.IMAP4_SSL(imap_ssl_host) as mail:
        # Log in to the Gmail account using App Password
        mail.login(gmail, password)
        print("########### Signed in to Gmail")

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


def login(driver, origin, destination, gmail, password):
    print("########### Signing in to Uber Webpage")

    email_input = driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS")
    email_input.send_keys(gmail)
    continue_button = driver.find_element(By.ID, "forward-button")
    continue_button.click()
    verification_code = getEmailCode(driver, gmail, password)
    otp_input_ids = [
        "EMAIL_OTP_CODE-0",
        "EMAIL_OTP_CODE-1",
        "EMAIL_OTP_CODE-2",
        "EMAIL_OTP_CODE-3",
    ]
    print("verification code: ", verification_code)

    for i in range(min(len(verification_code), len(otp_input_ids))):
        otp_input = driver.find_element(By.ID, otp_input_ids[i])
        otp_input.send_keys(verification_code[i])
    continue_button = driver.find_element(By.ID, "forward-button")
    # Click the forward button
    continue_button.click()
    print("########### Signed in to Uber Webpage")
    return


def download(driver):
    # get the data

    print("########### Fetching Elements from Uber Webpage")
    try:
        price = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/div/div[1]/div/main/div/section/div[2]/ul/li[1]/div[2]/div/div[1]/div",
                )
            )
        )
        print("########### price fetched")

        return price

        # Write the formatted page source to a file
    except TimeoutException as e:
        print(f"Error retrieving data: {e}")


def userIsLoggedIn(driver):
    try:
        if driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS"):
            return False
    except:
        return True


def logout(driver):
    try:
        print("########### Signing out of Uber Webpage")
        driver.find_element(
            By.XPATH, '//button[@data-buttonkey="smallHeaderRight"]'
        ).click()
        driver.find_element(
            By.XPATH, '//button[@data-buttonkey="https://riders.uber.com/profile"]'
        ).click()
        time.sleep(2)
        driver.find_element(By.XPATH, '//button[@data-buttonkey="logOut"]').click()
    except:
        print("########### Error signing out of Uber Webpage")
    print("########### Signed out of Uber Webpage")

    return


def switch_gmail():
    global gmail, password
    if gmail == gmail1:
        gmail, password = gmail2, password2
    elif gmail == gmail2:
        gmail, password = gmail3, password3
    elif gmail == gmail3:
        gmail, password = gmail1, password1


def scraper(driver, origin, destination, linkNotGotten):

    # Check if the element is found
    vehicle_type = ""
    uber_selection_url = generate_uber_url(destination, origin, vehicle_type)

    if linkNotGotten == True:
        try:
            driver.get(uber_selection_url)

        except:
            print("ERROR: Did not get Link")
            pass

    try:
        # Check for the presence of the element
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/div/div[1]/div/main/div/section/div[2]/ul/li[1]/div[2]/div/div[1]/div",
                )
            )
        )
        # If the element is found, download directly
        price = download(driver)
        # print("price: ", price.text)
        return price.text

    except Exception:
        # Handle the timeout exception here
        print("Timeout exception occurred. Assuming not logged in.")
        try:
            loginStatus = userIsLoggedIn(driver)
            # if user is logged in, log out and switch gmails
            if loginStatus == True:
                logout(driver)
                print("switching gmail from ", str(gmail))
                switch_gmail()
                print("switched gmail to: " + str(gmail))
            login(driver, origin, destination, gmail, password)
            linkNotGotten = False
            time.sleep(1)
            # recall scraper
            price = scraper(driver, origin, destination, linkNotGotten=False)
            return price
        except Exception as e:
            print("price retrieval failed, error: " + str(e))
            return


@app.post("/execute-script-1")
async def execute_script_1(request: Request):
    try:
        # Get JSON data from the request
        data = await request.json()
        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})
        userID = data.get("userID", {})
        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver_1, origin, destination, linkNotGotten=True)
        return JSONResponse({"result": result, "userID": userID})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/execute-script-2")
async def execute_script_2(request: Request):
    try:
        data = await request.json()
        origin = data.get("origin", {})
        destination = data.get("destination", {})
        userID = data.get("userID", {})
        result = scraper(chrome_driver_2, origin, destination, linkNotGotten=True)
        return JSONResponse({"result": result, "userID": userID})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
