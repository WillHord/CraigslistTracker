import sys
import requests
import email, smtplib, ssl
from lxml import html
import re

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from Database import Database

class CraigslistTracker():
    def __init__(self, email:str, passwd:str, databaseName:str):
        self.email = email
        self.passwd = passwd
        self.db = Database(databaseName)

    def addPage(self, url:str, name:str) -> None:
        self.db.addPage(url, name)
        self.db.checkItems(url,self.checkPage(url))

    def removePage(self, url:str) -> None:
        self.db.removePage(url)

    def getActivePages(self) -> list:
        return self.db.getActivePages()

    def checkPage(self, url: str) -> list:
        output = []
        res = requests.get(url)
        page = html.fromstring(res.content)
        content = page.xpath(".//div[@class='content']/ul/h4/preceding-sibling::li")
        if not content:
            content = page.xpath(".//div[@class='content']/ul/li")
        for i in content:
            title = i.xpath("div/h3/a")[0]
            date = i.xpath("div/time")[0]
            price = i.xpath("div/span/span[@class='result-price']/text()")
            location = i.xpath("div/span/span[@class='result-hood']/text()")[0]
            if price == []:
                price = 0
            else:
                price = int(price[0].strip("$ ").replace(",",""))
            output.append([title.text, title.attrib["href"], date.attrib["datetime"], price, location.strip(" ()")])
        nextPage = page.xpath(".//div[@class='search-legend']/div/span/a[@class='button next']")[0]
        if nextPage.attrib["href"] != "":
            print("Checking next page")
            output = output + self.checkPage(re.search(r".+?(?:org)", url).group() + nextPage.attrib["href"])
        return output

    def sendEmail(self, recipient: str, subject: str, message: str):
        print(f"Sending email to {recipient}\nsubject:{subject}\nmessage:{message}")
        Email = MIMEMultipart()
        Email["From"] = self.email
        Email["To"] = recipient
        Email["Subject"] = subject

        Email.attach(MIMEText(message, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.email, self.passwd)
            server.sendmail(self.email, recipient, Email.as_string())