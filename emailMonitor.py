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

        print("Email sent successfully.")

    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
def process_dataframe(dataframe):
    if "zip" in dataframe.columns:
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
        return dataframe
    else:
        return None
def monitor_gmail(username, app_password):
    try:
        while True:
            # Connect to the IMAP server
            mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            mail.login(username, app_password)

            # Search for unread messages
            mail.select("inbox")
            result, data = mail.search(None, "UNSEEN")

            # Get the list of message IDs
            message_ids = data[0].split()

            if not message_ids:
                print("No new messages.")
            else:
                print(f"Found {len(message_ids)} new message(s).")

            for message_id in message_ids:
                # Fetch the message data
                result, data = mail.fetch(message_id, "(RFC822)")

                if result == "OK":
                    # Parse the email content
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    sender = msg["From"]

                    # Detect attachments
                    if msg.get_content_maintype() == "multipart":
                        print("Message has attachment")
                        for part in msg.walk():
                            content_type = part.get_content_type()

                            # Check if the attachment is a spreadsheet (CSV or XLSX)
                            if content_type == "text/csv" or content_type == "application/vnd.ms-excel" or content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                attachment_name = part.get_filename()
                                print(f"Attachment Name: {attachment_name}")

                                # Save the spreadsheet file
                                save_folder = 'input'
                                in_file_path = os.path.join(save_folder, attachment_name)
                                with open(in_file_path, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                print(f"Saved attachment: {attachment_name}")

                                # Process the spreadsheet

                                # This could be threaded if necessary
                                # Build a class to handle tasks from here until end of loop

                                # Read csv and process
                                df = pd.read_csv(in_file_path)
                                processed_df = process_dataframe(df)
                                if processed_df is not None:
                                    # save returned dataframe to output folder
                                    save_folder = 'output'
                                    out_file_path = os.path.join(save_folder, attachment_name)
                                    processed_df.to_csv(out_file_path)

                                    # send output.csv to sender
                                    subject = "SCAMP Analysis"
                                    message = """
                                    SCAMP - SOC Calculation And Mapping Program v0.1
                                    
                                    SCAMP calculates the distance between the location zip code
                                    and the Seattle, Philly, and Chicago datacenters, and automatically
                                    assigns SOC codes based on closest DC location. 
                                    
                                    Questions - robert.lagrasse@t-mobile.com
                                    """
                                    send_email(username, app_password, sender, subject, message, out_file_path)

                                    # delete old files
                                    os.remove(out_file_path)
                                else:
                                    subject = "SCAMP Could not analyze your file"
                                    message = """
                                    SCAMP - SOC Calculation And Mapping Program v0.1

                                    There was a problem processing your file.
                                    Files must be csv formatted and
                                    contain a column called 'zip' with US postal codes  

                                    Questions - robert.lagrasse@t-mobile.com
                                    """
                                    send_email(username, app_password, sender, subject, message, in_file_path)
                                os.remove(in_file_path)

                # Mark the message as read
                mail.store(message_id, "+FLAGS", "\\Seen")
            mail.logout()
            time.sleep(10)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        mail.logout()


# Get the username and app password
with open("creds/creds.json", "r") as file:
    # Load the JSON content
    creds = json.load(file)

username = creds["username"]
password = creds["password"]

# Start monitoring the Gmail inbox
monitor_gmail(username, password)
