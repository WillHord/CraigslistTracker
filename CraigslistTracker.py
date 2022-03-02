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

    def checkActivePages(self) -> None:
        print("Checking active pages")
        active = self.db.getActivePages()
        for i in active:
            self.checkPage(i[0])

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

    def handleEmails(self):
        
        css = """<style>
                    #Page {
                    font-family: Arial, Helvetica, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                    }

                    #Page td, #Page th {
                    border: 1px solid #ddd;
                    padding: 8px;
                    }

                    #Page tr:nth-child(even){background-color: #f2f2f2;}

                    #Page tr:hover {background-color: #ddd;}

                    #Page th {
                    padding-top: 12px;
                    padding-bottom: 12px;
                    text-align: left;
                    background-color: #0d7dd9;
                    color: white;
                    }
                </style>"""
        html = f"""
            <html>
                <head>
                {css}
                </head>
                <body>
                <h2><a href="willhord.org">Page Name</a></h2>
                    <table id="Page">
                    <tr>
                        <th>Item</th>
                        <th>Price</th>
                        <th>Location</th>
                        <th>Date Posted</th>
                    </tr>
                    <tr>
                        <td><a href="willhord.org">Item 1</a></td>
                        <td>$23</td>
                        <td>Santa Cruz</td>
                        <td>March 4</td>
                    </tr>
                    <tr>
                        <td><a href="willhord.org">Item 2</a></td>
                        <td>$3</td>
                        <td>Santa Cruz</td>
                        <td>March 2</td>
                    </tr>
                </table>
                </body>
                </html>"""
        pass

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