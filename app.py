from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import json
import os
import time
import imaplib
import email
from email.header import decode_header
from selenium import webdriver
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Chrome driver outside of the request handler
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=./userProfile-1")
# options.add_argument("--headless")
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
chrome_driver = webdriver.Chrome(options=options)

imap_ssl_host = "imap.gmail.com"
imap_ssl_port = 993
gmail = "fatitomifin@gmail.com"
password = "miph lfrq punz jjnz"


def getEmailCode(driver):
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


def login(driver, origin, destination):
    print("########### Signing in to Uber Webpage")

    # vehicle type doesnt need to be defined
    vehicle_type = ""

    # Generate the Uber Selection URL
    uber_selection_url = generate_uber_url(destination, origin, vehicle_type)

    try:
        driver.get(uber_selection_url)

    except:
        print("ERROR: Did not get Link")
        pass
    # time.sleep(50)

    email_input = driver.find_element(By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS")
    email_input.send_keys(gmail)
    continue_button = driver.find_element(By.ID, "forward-button")
    continue_button.click()
    verification_code = getEmailCode(driver)

    with open("source.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)
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
    print("########### Signed in to Uber Webpage")


def download(driver):
    # get the data
    print("########### Fetching Elements from Uber Webpage")
    try:
        price = WebDriverWait(driver, 20).until(
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


def scraper(driver, origin, destination):
    # Check if the element is found
    vehicle_type = ""
    uber_selection_url = generate_uber_url(destination, origin, vehicle_type)
    try:
        driver.get(uber_selection_url)

    except:
        print("ERROR: Did not get Link")
        pass

    try:
        # Check for the presence of the element
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/div/div[1]/div/main/div/section/div[2]/ul/li[1]/div[2]/div/div[1]/div",
                )
            )
        )
        # If the element is found, download directly
        price = download(driver)
        return price.text

    except TimeoutException:
        # Handle the timeout exception here
        print("Timeout exception occurred. Assuming not logged in.")
        try:
            login(driver, origin, destination)
            price = download(driver)

        except NoSuchElementException as e:
            print("login failed")
            return

        return "trip price: " + price.text


@app.route("/execute-script-1", methods=["POST"])
def execute_script_1():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver, origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/execute-script-2", methods=["POST"])
def execute_script_2():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver, origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/execute-script-3", methods=["POST"])
def execute_script_3():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver, origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/execute-script-4", methods=["POST"])
def execute_script_4():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver, origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/execute-script-5", methods=["POST"])
def execute_script_5():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver, origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/execute-script-6", methods=["POST"])
def execute_script_6():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver, origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/execute-script-7", methods=["POST"])
def execute_script_7():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver, origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/execute-script-8", methods=["POST"])
def execute_script_8():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract origin and destination from the JSON data
        origin = data.get("origin", {})
        destination = data.get("destination", {})

        # Pass the extracted data and the Chrome instance to the scraper_script
        result = scraper(chrome_driver, origin, destination)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
