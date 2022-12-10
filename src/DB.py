import mysql.connector
from datetime import date

from Item import *
from Sale import *

class DB:

    def __init__(self):
        self.host = 'armatlantico.ddns.net'
        self.port = 3308
        self.user = 'root'
        self.passwd = 'xd'
        self.database = 'xdaa'
    
    def connect(self):
        self.cnx = mysql.connector.connect(host = self.host, port = self.port, database = self.database, user = self.user, passwd = self.passwd)
        self.cur = self.cnx.cursor(buffered = True)

    def query(self,queryTxt):
        self.cur.execute(queryTxt)
        return self.cur
    
    def close(self):
        self.cnx.close()
    
    def getItems(self, removeInactive = True):
        queryTxt = "SELECT KeyId, Description, CurrentStock FROM xdaa.items ORDER BY Description;"
        result = self.query(queryTxt)
        
        items = []
        for tupleElement in result:
            desc = tupleElement[1].lower()
            
            if not removeInactive or not ("z fora linha" in desc or "z fora de linha" in desc):
                try:
                    items += [Item(ID = int(tupleElement[0]),Description=tupleElement[1],CurrentStock=float(tupleElement[2]))]
                except:
                    print(f"Warning: could not add item: {tupleElement}.")

        return items

    def getItemSales(self,itemID, startDate = None, orderAsc = False):
        if startDate == None:
            # today = date.today()
            # startDate = f"{today.year}:{today.month}:01 00:00:00"
            startDate = f"2020:01:01 00:00:00"


        order = "DESC"
        if orderAsc == True:
            order = "ASC"
        queryTxt = f"SELECT ItemKeyId, Quantity, CloseDate, DocumentDescription FROM xdaa.salesdocumentsreportview WHERE CloseDate > '{startDate}' AND ItemKeyId = {itemID} ORDER BY CloseDate {order};"
        result = self.query(queryTxt)
        
        sales = []
        for elm in result:
            sales += [Sale(itemID = int(elm[0]),quantity=float(elm[1]),closeDate=elm[2],documentDescription=elm[3])]
        
        return sales
    
    def getAllSales(self, startDate = None, orderAsc = False):
        if startDate == None:
            # today = date.today()
            # startDate = f"{today.year}:{today.month}:01 00:00:00"
            startDate = f"2020:01:01 00:00:00"


        order = "DESC"
        if orderAsc == True:
            order = "ASC"
        queryTxt = f"SELECT ItemKeyId, Quantity, CloseDate, DocumentDescription FROM xdaa.salesdocumentsreportview WHERE CloseDate > '{startDate}' ORDER BY CloseDate {order};"
        result = self.query(queryTxt)
        
        sales = []
        for elm in result:
            try:
                sales += [Sale(itemID = int(elm[0]),quantity=float(elm[1]),closeDate=elm[2],documentDescription=elm[3])]
            except:
                # print(f"Warning: could not add sale: {elm}.")
                pass

        return sales


"""
SELECT * FROM xdaa.salesdocumentsreportview WHERE CloseDate > '2022-11-25 00:00:00' ORDER BY CloseDate DESC;
"""
"""
SELECT * FROM xdaa.items;
SELECT Id, KeyId, Description, ShortName1, CurrentStock FROM xdaa.items ORDER BY Description;
"""
"""
SELECT * FROM xdaa.itemstock;
SELECT xdaa.items.KeyId, xdaa.itemstock.ItemKeyId, xdaa.items.Description, xdaa.itemstock.AvailableQuantity, xdaa.items.CurrentStock FROM xdaa.itemstock, xdaa.items WHERE xdaa.items.KeyId = xdaa.itemstock.ItemKeyId ORDER BY xdaa.items.Description;
SELECT ItemKeyId, Quantity, CloseDate, DocumentDescription FROM xdaa.salesdocumentsreportview WHERE CloseDate > '2021-11-25 00:00:00' AND ItemKeyId = 1407 ORDER BY CloseDate DESC;
"""
