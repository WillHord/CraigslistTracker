import sys
import argparse
import sched
import time
import threading

from datetime import datetime, timedelta
import os

from Database import Database
from CraigslistTracker import CraigslistTracker
import Errors

class Controller():
    scheduler = sched.scheduler(time.time, time.sleep)
    def __init__(self, flags:argparse.Namespace, database:str = "craigslist.db"):
        options = vars(flags)
        if options['database']:
            self.database = options['database']
        else:
            self.database = database
        self.getEmailPasswd()
        self.Tracker = CraigslistTracker(self.email, self.passwd, self.database)
        # self.checkInterval = 3600
        self.checkInterval = 5
        self.emailHour = 12

        if options['remove']:
            self.Tracker.removePage(options['remove'])
        if options['add']:
            self.Tracker.addPage(options['add'])
        if options['cleanup']:
            self.cleanup()

    def getEmailPasswd(self) -> None:
        if os.path.exists("/etc/emailCredentials"):
            with open("/etc/emailCredentials", "r") as f:
                lines = [line.rstrip() for line in f]
                self.email = lines[0]
                self.passwd = lines[1]
        else:
            print("Email credentials not found")
            self.email = input("Please enter your email: ")
            self.passwd = input("Please enter your password: ")
            with open("/etc/emailCredentials", "w") as f:
                f.write(self.email+'\n'+self.passwd)
                print("Email and Password saved in /etc/emailCredentials")

    def commands(self) -> None:
        while(True):
            command = input("> ").split()
            if len(command) == 0:
                continue
            elif command[0][0] == "#":
                continue
            elif command[0].lower() in ["exit","q"]:
                self.stop()
            elif command[0].lower() in ["add","a"]:
                if len(command) < 3:
                    print("ERROR: add command requires 2 additional arguments")
                    print("Format: add {url} {name}")
                    continue
                print("Adding page:", command[1])
                self.Tracker.addPage(command[1],command[2])
            elif command[0].lower() in ["remove","rm"]:
                if len(command) < 2:
                    print("ERROR: add command requires 1 additional arguments")
                    print("Format: add {url}")
                    continue
                print("Removing page:", command[1])
                self.Tracker.removePage(command[1])
            elif command[0].lower() in ["check","c"]:
                print("Checking pages")
                self.Tracker.checkActivePages()
            elif command[0].lower() in ["help","h"]:
                print("usage: [h] [a ADD] [rm REMOVE] [c CHECK] [q EXIT]")
            else:
                print(f"ERROR: command {' '.join(command)} not recognized")

    def cleanup(self):
        if os.path.exists(self.database):
            print(f"Deleting {self.database}...")
            os.remove(self.database)

    def checkPages(self):
        # print("Checking pages")
        self.Tracker.checkActivePages()
        self.scheduler.enter(self.checkInterval,1,self.checkPages)
        
    def sendEmail(self) -> None:
        # TODO: Fix send Email to send email with actual information
        # self.Tracker.sendEmail("contactwillhord@gmail.com","Test Subject","This is a test message")
        self.emailHandler()
        
    def emailHandler(self) -> None:
        x=datetime.today()
        y = x.replace(day=x.day, hour=self.emailHour, minute=0, second=0, microsecond=0) + timedelta(days=1)
        delta_t=y-x
        secs=delta_t.total_seconds()
        t = threading.Timer(secs, self.sendEmail)
        t.start()

    def start(self):
        self.scheduler.enter(self.checkInterval,1,self.checkPages)
        self.pageThread = threading.Thread(target=self.scheduler.run)
        self.emailHandler()
        self.commandThread = threading.Thread(target=self.commands)
        
        self.pageThread.daemon = True
        self.commandThread.daemon = True
        
        self.checkPages()
        self.pageThread.start()
        # emailThread.start()
        self.commandThread.start()
    
    def stop(self):
        print("Stopping all processes")
        os._exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Craigslist Tracker")
    parser.add_argument("-d", "--database", help="Define database file location")
    parser.add_argument("-a", "--add", help="Add page to track")
    parser.add_argument("-rm","--remove", help="Remove page from being tracked")
    parser.add_argument("-c","--cleanup", help="Clean up created files", action='store_true')

    args = parser.parse_args()
    Tracker = Controller(args)
    Tracker.start()


    # Testing
    # Tracker.addPage("https://sfbay.craigslist.org/search/scz/zip","Free")
    # Tracker.commands()
