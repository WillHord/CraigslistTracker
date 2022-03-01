import sys
import argparse
# import email, smtplib, ssl
# from lxml import html
# import requests
# import sqlite3
# from sqlite3 import Error

# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# import os
# import time

from Database import Database
from CraigslistTracker import CraigslistTracker
import Errors

# from . import Errors

# TODO: Finish Controller

class Controller():
    def __init__(self,database:str = "craigslist.db"):
        return
    def start(self, flags):
        pass
    def run(self):
        pass


if __name__ == "__main__":
    # test = CraigslistTracker()
    # test.sendEmail(email,"Test Email", "This is a new test email")
    # test.checkPage("https://sfbay.craigslist.org/search/scz/zip")
    
    # databasetest = Database("./craigslistTesting.db")
    # databasetest.addPage("testURL", "test")
    # databasetest.addItem('testURL',"test title", "March 5th")
    # databasetest.removePage("test")
    # databasetest.close()
    
    argv = sys.argv
    print(argv)