import imaplib
import email
from email.header import decode_header
import os

imap_ssl_host = "imap.gmail.com"
imap_ssl_port = 993
username = "samuelironkwec@gmail.com"

password = os.getenv("GMAIL_PASSWORD")


# Function to fetch and print the subject of the most recent email
def fetch_most_recent_email_subject():
    # Connect to Gmail IMAP server
    with imaplib.IMAP4_SSL(imap_ssl_host) as mail:
        # Log in to the Gmail account using App Password
        mail.login(username, password)

        # Select the 'inbox' folder
        mail.select("inbox")

        # Search for all emails in the 'inbox'
        result, data = mail.search(None, "ALL")
        latest_email_id = data[0].split()[-1]  # Get the ID of the most recent email

        if latest_email_id:
            # Fetch the most recent email using its ID
            result, message_data = mail.fetch(latest_email_id, "(RFC822)")

            if result == "OK":
                # Decode the email message
                msg = email.message_from_bytes(message_data[0][1])

                # Extract and print the subject
                subject, encoding = decode_header(msg["Subject"])[0]
                print(f"Subject: {subject}")
            else:
                print("Error fetching the most recent email.")


# Call the function to fetch and print the subject of the most recent email
fetch_most_recent_email_subject()
