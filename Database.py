import sqlite3
from sqlite3 import Error

import os
import time

class Database():
    def __init__(self, database: str):
        self.conn = self.connect(database)

    def connect(self, database: str) -> sqlite3.Connection:
        conn = None
        try:
            if os.path.exists(database):
                conn = sqlite3.connect(database, check_same_thread=False)
            else:
                conn = self.setUpDatabase(database)
            print("Connected to database:",database)
            print("sqlite3 version:", sqlite3.version)
        except Error as e:
            print(e)
        return conn

    def setUpDatabase(self, database: str) -> sqlite3.Connection:
        createBaseTable = """CREATE TABLE IF NOT EXISTS pages(
            id integer PRIMARY KEY,
            name text NOT NULL,
            url text NOT NULL UNIQUE,
            active integer NOT NULL,
            added integer NOT NULL,
            lastChecked integer NOT NULL);"""
        try:
            conn = sqlite3.connect(database, check_same_thread=False)
            c = conn.cursor()
            c.execute(createBaseTable)
            conn.commit()
            return conn
        except Error as e:
            raise(e)


    def addPage(self, url:str, name:str) -> None:
        c = self.conn.cursor()
        exists = c.execute(f"""SELECT url, active from pages WHERE url='{url}';""").fetchone()
        if exists:
            print(exists)
            if exists[1] == 1:
                print(f"ERROR: URL {url} already being tracked")
            else:
                c.execute(f"""UPDATE pages SET active=1 WHERE url='{url}';""")
                self.conn.commit()
        else:
            print(f"URL {url} is now being tracked")
            c.execute(f"""INSERT INTO pages(url, name, active, added, lastChecked) values('{url}', '{name}', 1, {int(time.time())}, {int(time.time())});""")
            c.execute(f"""CREATE TABLE IF NOT EXISTS {name.replace(" ","_")}(
            id integer PRIMARY KEY,
            title text NOT NULL,
            url text NOT NULL UNIQUE,
            price integer NOT NULL,
            location text NOT NULL,
            posted text NOT NULL,
            active integer NOT NULL,
            added integer NOT NULL,
            lastChecked integer NOT NULL);""")
            self.conn.commit()

    def removePage(self, url:str) -> None:
        c = self.conn.cursor()
        exists = c.execute(f"""SELECT url, active from pages WHERE url='{url}';""").fetchone()
        if exists:
            if exists[1] == 0:
                print(f"ERROR: URL {url} is already not being tracked")
            else:
                c.execute(f"""UPDATE pages SET active=0 WHERE url='{url}';""")
                self.conn.commit()
                print(f"URL: {url} is no longer being tracked")
        else:
            print(f"ERROR: URL {url} is already not being tracked")

    def addItem(self, pageUrl:str, url:str, title:str, datePosted: str, price: int, location: str) -> None:
        c = self.conn.cursor()
        name = c.execute(f"""SELECT name from pages WHERE url='{pageUrl}';""").fetchone()[0]
        exists = c.execute(f"""SELECT title, active FROM {name.replace(" ", "_")} where url='{url}';""").fetchone()
        if exists:
            # print(f"URL {url} exists in table")
            if exists[1] == 0:
                c.execute(f"""UPDATE {name.replace(" ","_")} SET lastChecked={int(time.time())}, active=1 WHERE url='{url}';""")
            else:
                c.execute(f"""UPDATE {name.replace(" ","_")} SET lastChecked={int(time.time())} WHERE url='{url}';""")
            self.conn.commit()
        else:
            try:
                tempTitle = title.replace("'","")
                c.execute(f"""INSERT INTO {name.replace(" ","_")}(title, url, price, location, posted, active, added, lastChecked)
                        values('{tempTitle}','{url}',{price},'{location}','{datePosted}',1,{int(time.time())},{int(time.time())});""")
                self.conn.commit()
            except Exception as e:
                print(f"""INSERT INTO {name.replace(" ","_")}(title, url, price, location, posted, active, added, lastChecked)
                        values('{tempTitle}','{url}',{price},'{location}','{datePosted}',1,{int(time.time())},{int(time.time())});""")
                print(e)
                exit()

    def removeItem(self, pageUrl:str, url: str) -> None:
        c = self.conn.cursor()
        name = c.execute(f"""SELECT name from pages WHERE url='{pageUrl}';""").fetchone()[0]
        exists = c.execute(f"""SELECT id FROM {name.replace(" ","_")} where url='{url}';""").fetchone()
        if exists:
            # print(f"URL {url} exists in table")
            c.execute(f"""UPDATE {name.replace(" ","_")} SET active=0, lastChecked={int(time.time())} WHERE url='{url}';""")
            self.conn.commit()
        else:
            print(f"Item {url} does not exist (this should be the right choice)")

    def checkItems(self, pageUrl:str, items: list) -> None:
        c = self.conn.cursor()
        name = c.execute(f"""SELECT name from pages WHERE url='{pageUrl}';""").fetchone()[0]
        allitems = c.execute(f"""SELECT title, url from {name.replace(" ","_")} WHERE active=1""").fetchall()
        itemsToRemove = [i[1] for i in allitems if i[1] not in [i[1] for i in items]]
        for i in items:
            self.addItem(pageUrl=pageUrl, title=i[0], url=i[1], datePosted=i[2], price=i[3], location=i[4])
        for i in itemsToRemove:
            self.removeItem(pageUrl=pageUrl, url=i)
    
    def getActivePages(self) -> list:
        c = self.conn.cursor()
        return c.execute("SELECT url from pages WHERE active=1;").fetchall()

    def getAllActiveItems(self) -> dict:
        print("getAllActiveItems")
        pageitemdict = {}
        c = self.conn.cursor()
        pages = c.execute("SELECT name from pages WHERE active=1;").fetchall()
        for i in pages:
            pageitemdict[i[0]] = c.execute(f"SELECT title, price, location, posted FROM {i[0].replace(' ','_')} WHERE active=1;").fetchall()
        return pageitemdict

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def TestingConnection(self) -> sqlite3.Connection:
        return self.conn
