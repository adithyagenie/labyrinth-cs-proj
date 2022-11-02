import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pickle
from random import choice


def sender(userid, receiver_address):
    try:
        with open("credentials.pickle", "rb") as f:
            d = pickle.load(f)
            sender_address = d["email"]
            sender_pass = d["pass"]
    except FileNotFoundError:
        print("Credentials for email missing. Terminating...")
        exit()
    # Random 6 digit number but looks cool
    l = [i for i in range(0, 10)]
    s = ""
    for _ in range(6):
        s += str(choice(l))
    otp = int(s)

    mail_content = f"""Hello {userid}, </br>
This is an automatically generated email.</br>\
The password for resetting your password in the Labyrinth CSC Project is: </br>\
<h3><b>{otp}</b></h3></br>\
<p>
Do not share this OTP with anyone. If you have not requested for a password reset, please ignore.</p>\
<p></p>\
<p>Yours,</br>\
The Labyrinth Team"""
    # The mail addresses and password
    # Setup the MIME
    message = MIMEMultipart()
    message["From"] = sender_address
    message["To"] = receiver_address
    message[
        "Subject"
    ] = "Reset your Labyrinth account password"
    message.attach(MIMEText(mail_content, "html"))

    # Create SMTP session for sending the mail
    session = smtplib.SMTP("smtp.gmail.com", 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    return otp
