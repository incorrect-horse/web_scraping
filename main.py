import requests
import selectorlib
import smtplib, ssl
import os
import time
import sqlite3


URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def scrape(url):
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("files/extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    username = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("SEND_EMAIL")

    receiver = os.getenv("EMAIL_ADDRESS")
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)

    print("email sent")
    return


def store_data(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
    connection.commit()
    return


def read_data(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    band, city, date = row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band_name=? AND city=? AND date=?",
                   (band, city, date))
    contents = cursor.fetchall()
    return contents


connection = sqlite3.connect("files/data.db")

if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            content = read_data(extracted)
            if not content:
                store_data(extracted)
                message = f"""\
Subject: New Event Notification.

A new concert event was found:
{extracted}
"""
                message = message.encode("utf-8")
                send_email(message)
        time.sleep(2)
