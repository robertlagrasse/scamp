# SCAMP - SOC Calculation and Mapping Program

import imaplib
import email
import json
import time
import os
import pandas as pd
from locationutils import Geocoder
from locationutils import closest_dc
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
logging.basicConfig(filename='scamp.log', encoding='utf-8', level=logging.INFO)

# Gmail SMTP server details
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Gmail IMAP server details
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


def send_email(username, app_password, recipient, subject, message, attachment_path):
    try:
        # Create a multipart message
        msg = MIMEMultipart()
        msg["From"] = username
        msg["To"] = recipient
        msg["Subject"] = subject

        logging.info(f"{time.time()}: send_email {recipient} {attachment_path}")
        # Add message body
        msg.attach(MIMEText(message, "plain"))

        if attachment_path:
            # Open the file in bytestring mode
            with open(attachment_path, "rb") as attachment_file:
                # Create attachment object
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(attachment_file.read())

            # Encode the attachment and set filename
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment_path.split('/')[-1]}",
            )

            # Add attachment to the message
            msg.attach(attachment)

        # Connect to the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()

        # Login with the app password
        server.login(username, app_password)

        # Send the email
        server.send_message(msg)

        # Disconnect from the server
        server.quit()

        logging.info(f"{time.time()}: send_email {recipient} successful")

    except Exception as e:
        logging.info(f"{time.time()}: send_email {recipient} failed: {e}")
def process_dataframe(dataframe):
    logging.info(f"{time.time()}: process_dataframe()")
    if "zip" in dataframe.columns:
        logging.info(f"{time.time()}: process_dataframe(): Headers OK")
        dataframe['latitude'] = None
        dataframe['longitude'] = None
        dataframe['phone_soc'] = None
        dataframe['mobile_internet'] = None
        for index, row in dataframe.iterrows():
            try:
                resolver = Geocoder()
                zipcode = row["zip"]
                lat, long = resolver.resolve(zipcode)
                phone_soc, mobile_internet = closest_dc(float(lat),float(long))
                dataframe.loc[index, 'latitude'] = lat
                dataframe.loc[index, 'longitude'] = long
                dataframe.loc[index, 'phone_soc'] = phone_soc
                dataframe.loc[index, 'mobile_internet'] = mobile_internet
            except:
                dataframe.loc[index, 'latitude'] = "-1"
                dataframe.loc[index, 'longitude'] = "-1"
                dataframe.loc[index, 'phone_soc'] = "ZSIPV4"
                dataframe.loc[index, 'mobile_internet'] = "ZSIPV4MI"
        logging.info(f"{time.time()}: process_dataframe(): Complete. Returning Dataframe")
        return dataframe
    else:
        logging.info(f"{time.time()}: process_dataframe(): Headers Check Failed. Returning None")
        return None
def monitor_gmail(username, app_password):
    logging.info(f"{time.time()}: monitor_gmail(): Started")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(username, app_password)
        logging.info(f"{time.time()}: monitor_gmail(): Logged into gmail")
        while True:
            # Search for unread messages
            mail.select("inbox")
            result, data = mail.search(None, "UNSEEN")

            # Get the list of message IDs
            message_ids = data[0].split()

            if not message_ids:
                logging.info(f"{time.time()}: monitor_gmail(): No new messages.")
            else:
                logging.info(f"{time.time()}: monitor_gmail(): Found {len(message_ids)} new message(s).")

            for message_id in message_ids:
                # Fetch the message data
                result, data = mail.fetch(message_id, "(RFC822)")

                if result == "OK":
                    # Parse the email content
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    sender = msg["From"]
                    logging.info(f"{time.time()}: monitor_gmail(): From: {sender}")

                    # Detect attachments
                    if msg.get_content_maintype() == "multipart":
                        logging.info(f"{time.time()}: monitor_gmail(): Message has attachment")
                        for part in msg.walk():
                            content_type = part.get_content_type()

                            # Check if the attachment is a spreadsheet (CSV or XLSX)
                            if content_type == "text/csv" or content_type == "application/vnd.ms-excel" or content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                attachment_name = part.get_filename()
                                logging.info(f"{time.time()}: monitor_gmail(): {attachment_name} is valid type")

                                # Save the spreadsheet file
                                save_folder = 'input'
                                in_file_path = os.path.join(save_folder, attachment_name)
                                with open(in_file_path, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                    logging.info(f"{time.time()}: monitor_gmail(): {attachment_name} saved")

                                # Process the spreadsheet

                                # This could be threaded if necessary
                                # Build a class to handle tasks from here until end of loop

                                # Read csv and process
                                logging.info(f"{time.time()}: monitor_gmail(): sending {attachment_name} to process_df()")
                                df = pd.read_csv(in_file_path)
                                processed_df = process_dataframe(df)
                                if processed_df is not None:
                                    # save returned dataframe to output folder
                                    logging.info(f"{time.time()}: monitor_gmail(): processed dataframe returned")
                                    save_folder = 'output'
                                    out_file_path = os.path.join(save_folder, attachment_name)
                                    processed_df.to_csv(out_file_path)
                                    logging.info(f"{time.time()}: monitor_gmail(): {out_file_path} saved")


                                    # send output.csv to sender
                                    subject = "SCAMP Analysis"
                                    message = """
                                    SCAMP - SOC Calculation And Mapping Program v0.1
                                    
                                    SCAMP calculates the distance between the location zip code
                                    and the Seattle, Philly, and Chicago datacenters, and automatically
                                    assigns SOC codes based on closest DC location. 
                                    
                                    Questions - robert.lagrasse@t-mobile.com
                                    """
                                    logging.info(f"{time.time()}: monitor_gmail(): sending to send_email()")
                                    send_email(username, app_password, sender, subject, message, out_file_path)

                                    # delete old files
                                    os.remove(out_file_path)
                                    logging.info(f"{time.time()}: monitor_gmail(): deleted {out_file_path}")

                                else:
                                    subject = "SCAMP Could not analyze your file"
                                    message = """
                                    SCAMP - SOC Calculation And Mapping Program v0.1

                                    There was a problem processing your file.
                                    Files must be csv formatted and
                                    contain a column called 'zip' with US postal codes  

                                    Questions - robert.lagrasse@t-mobile.com
                                    """
                                    logging.info(f"{time.time()}: monitor_gmail(): Sending error message email")
                                    send_email(username, app_password, sender, subject, message, in_file_path)
                                os.remove(in_file_path)
                                logging.info(f"{time.time()}: monitor_gmail(): deleted {in_file_path}")

                # Mark the message as read
                mail.store(message_id, "+FLAGS", "\\Seen")
                logging.info(f"{time.time()}: monitor_gmail(): updated mailbox (email flagged as seen)")
            time.sleep(10)
    except Exception as e:
        logging.info(f"{time.time()}: monitor_gmail(): An error occurred: {e}")
    finally:
        # Close the connection
        logging.info(f"{time.time()}: monitor_gmail(): logged out of gmail")
        mail.close()

# Get the username and app password
with open("creds/creds.json", "r") as file:
    # Load the JSON content
    creds = json.load(file)

username = creds["username"]
password = creds["password"]

# Start monitoring the Gmail inbox
monitor_gmail(username, password)
