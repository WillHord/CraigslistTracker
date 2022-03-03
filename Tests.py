import os
import sys
import argparse
from sqlite3 import Error

from Database import Database
from CraigslistTracker import CraigslistTracker
import Errors


class Tests():
    email = "contactwillhord@gmail.com"
    with open("/etc/contactwillhordpasswd") as f:
        passwd = f.read()

    def __init__(self, flags):
        self.flags = flags

    def DatabaseTest(self) -> None:
        print("\nStarting Database test...")
        testdb = Database("testdb.db")

        if os.path.exists("testdb.db"):
            print("Database creation successful")
        else:
            raise Errors.TestFailedError("Database creation failed")

        # Add pages
        try:
            testdb.addPage("https://www.willhord.org/","Will Hord")
            testdb.addPage("https://testurl1.com/","Test Page 1")
            testdb.addPage("https://testurl2.com/","Test Page 2")
            testdb.addPage("https://testurl3.com/","Test Page 3")
            testdb.addPage("https://testurl4.com/","Test Page 4")
        except Error as e:
            print("ERROR")
            self.Cleanup(Error=Errors.TestFailedError("Adding pages test failed"))
        conn = testdb.TestingConnection()
        c = conn.cursor()

        test = c.execute("""SELECT id,name,url from pages""").fetchall()
        correct = [(1, 'Will Hord', 'https://www.willhord.org/'),
                (2, 'Test Page 1', 'https://testurl1.com/'),
                (3, 'Test Page 2', 'https://testurl2.com/'),
                (4, 'Test Page 3', 'https://testurl3.com/'),
                (5, 'Test Page 4', 'https://testurl4.com/')]
        if test == correct:
            print("Add Page Test PASSED")
        else:
            self.Cleanup(Error=Errors.TestFailedError("Adding pages test FAILED"))

        # Add item test
        tp1Items = [
            ["item1", "https://testurl1.com/test1","2022-03-25 03:47",0,"New York"],
            ["item3", "https://testurl1.com/test2","2022-25-25 07:47",0,"New York"],
            ["item4", "https://testurl1.com/test3","2022-06-25 05:47",0,"New York"],
            ["item2", "https://testurl1.com/test4","2022-09-25 07:47",0,"New York"],
            ["item5", "https://testurl1.com/test5","2022-02-25 08:47",0,"New York"]]
        tp2Items = [
            ["item1", "https://testurl1.com/test1","2022-03-25 03:47",0,"New York"],
            ["item4", "https://testurl1.com/test3","2022-06-25 05:47",0,"New York"],
            ["item2", "https://testurl1.com/test4","2022-09-25 07:47",0,"New York"],
            ["item5", "https://testurl1.com/test5","2022-02-25 08:47",0,"New York"]]
        tp3Items = [
            ["item1", "https://testurl1.com/test1","2022-03-25 03:47",0,"New York"],
            ["item3", "https://testurl1.com/test2","2022-25-25 07:47",0,"New York"],
            ["item4", "https://testurl1.com/test3","2022-06-25 05:47",0,"New York"],
            ["item5", "https://testurl1.com/test5","2022-02-25 08:47",0,"New York"]]

        testdb.checkItems("https://testurl1.com/",tp1Items)
        testdb.checkItems("https://testurl1.com/",tp2Items)
        testdb.checkItems("https://testurl1.com/",tp3Items)

        itemTest = c.execute("SELECT title, url, active FROM Test_Page_1;").fetchall()
        correctItemTest = [('item1', 'https://testurl1.com/test1', 1),
                        ('item3', 'https://testurl1.com/test2', 1),
                        ('item4', 'https://testurl1.com/test3', 1),
                        ('item2', 'https://testurl1.com/test4', 0),
                        ('item5', 'https://testurl1.com/test5', 1)]
        if itemTest == correctItemTest:
            print("Add item Test PASSED")
        else:
            self.Cleanup(Error=Errors.TestFailedError("Add item test FAILED"))

        # Remove Page Test
        testdb.removePage("https://testurl2.com/")
        testdb.removePage("https://testurl3.com/")
        testdb.removePage("https://testurl4.com/")

        removePageTest = c.execute("SELECT url, active from pages;").fetchall()
        correctRemovePageTest = [('https://www.willhord.org/', 1),
                                ('https://testurl1.com/', 1),
                                ('https://testurl2.com/', 0),
                                ('https://testurl3.com/', 0),
                                ('https://testurl4.com/', 0)]
        if removePageTest == correctRemovePageTest:
            print("Remove page test PASSED")
        else:
            self.Cleanup(Error=Errors.TestFailedError("Remove page test FAILED"))

        pagedict = testdb.getAllActiveItems()

        testdb.close()
        print("ALL DATABASE TESTS PASSED")
        self.Cleanup()

    def EmailTest(self, email:str, passwd:str):
        testTracker = CraigslistTracker(email, passwd)
        try:
            testTracker.sendEmail("contactwillhord@gmail.com","Test Subject","This is a test message")
            print("Email test PASSED")
        except Exception as e:
            print("Email test FAILED")
            self.Cleanup()
            raise e

    def Cleanup(self, *args, **kwargs) -> None:
        error = kwargs.get('Error',None)
        if error:
            print("An error has occured, now cleaning up...")
            if os.path.exists("testdb.db"):
                print("Deleting testdb.db...")
                os.remove("testdb.db")
            raise error
        else:
            print("Cleaning Up...")
            if os.path.exists("testdb.db"):
                print("Deleting testdb.db...")
                os.remove("testdb.db")

    def webTests(self) -> None:
        testTracker = CraigslistTracker(self.email, self.passwd,"testdb.db")
        testTracker.addPage("https://sfbay.craigslist.org/search/scz/sss?query=bike&excats=141-1", "Bikes")
        testTracker.addPage("https://sfbay.craigslist.org/search/scz/zip", "Free")
        print(testTracker.getActivePages())
        print("ALL Web Tests PASSED")
        self.Cleanup()

    def run(self) -> None:
        options = vars(self.flags)
        if options["all"]:
            print("Running All Tests...")
            self.DatabaseTest()
            self.EmailTest(self.email, self.passwd)
        if options["email"]:
            print("Running Email Tests...")
            self.EmailTest(self.email, self.passwd)
        if options["database"]:
            print("Running Database Tests...")
            self.DatabaseTest()
        if options["cleanup"]:
            self.Cleanup()
        if options["scrape"]:
            self.webTests()
        print("Done Running all Tests")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Craigslist Tracker")
    parser.add_argument("-a","--all",help="Run all tests", action='store_true')
    parser.add_argument("-e","--email",help="Run email tests", action='store_true')
    parser.add_argument("-d","--database",help="Run database tests", action='store_true')
    parser.add_argument("-c","--cleanup",help="Cleanup testing files", action='store_true')
    parser.add_argument("-s","--scrape",help="Run web scraping tests", action='store_true')
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    args = parser.parse_args()
    tests = Tests(args)
    tests.run()