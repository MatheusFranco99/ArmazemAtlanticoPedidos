import mysql.connector
from datetime import date


class Item:

    def __init__(self,ID = None, Description = None, CurrentStock = None):
        self.ID = ID
        self.Description = Description
        self.CurrentStock = CurrentStock
    
    def __str__(self):
        return '{\n' + f"\tID={self.ID},\n\tDescription = {self.Description},\n\tCurrentStock = {self.CurrentStock},\n" + '}'
    
    def __repr__(self):
        return '{\n' + f"\tID={self.ID},\n\tDescription = {self.Description},\n\tCurrentStock = {self.CurrentStock},\n" + '}'
    

FATURA = 0
FATURA_PROFORMA = 1
NOTA_DE_ENCOMENDA = 2
FATURA_STR = "Fatura"
FATURA_PROFORMA_STR = "Fatura Proforma"
NOTA_DE_ENCOMENDA_STR = "Nota de Encomenda"

class Sale:

    def __init__(self, itemID = None, quantity = None, closeDate = None, documentDescription = None):
        self.itemID = itemID
        self.quantity = quantity
        self.closeDate = closeDate
        self.documentDescription = documentDescription

        self.documentType = -1
        if self.documentDescription == FATURA_STR:
            self.documentType = FATURA
        elif self.documentDescription == FATURA_PROFORMA_STR:
            self.documentType = FATURA_PROFORMA
        elif self.documentDescription == NOTA_DE_ENCOMENDA_STR:
            self.documentType = NOTA_DE_ENCOMENDA
    

    def __str__(self):
        return '{\n' + f"\tItemID={self.itemID},\n\tQuantity = {self.quantity},\n\tCloseDate = {self.closeDate},\n\tDocument Description = {self.documentDescription},\n" + '}'
    
    def __repr__(self):
        return '{\n' + f"\tItemID={self.itemID},\n\tQuantity = {self.quantity},\n\tCloseDate = {self.closeDate},\n\tDocument Description = {self.documentDescription},\n" + '}'
    

DATE_NOT_FOUND = "Date not found."

class ItemHistory:

    def __init__(self, itemID = None, sales = None):
        self.itemID = itemID
        self.sales = sales

    def generateSales(self,db):
        self.sales = db.getItemSales(self.itemID, startDate = "2020:01:01 00:00:00", orderAsc = True)

    def getLastSalesDate(self, typeDoc = FATURA):
        idx = len(self.sales)-1
        while(idx >= 0):
            if (self.sales[idx].documentType == typeDoc):
                return self.sales[idx].closeDate
            idx = idx - 1
        return DATE_NOT_FOUND

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
                items += [Item(ID = tupleElement[0],Description=tupleElement[1],CurrentStock=tupleElement[2])]

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
            sales += [Sale(itemID = elm[0],quantity=int(elm[1]),closeDate=elm[2],documentDescription=elm[3])]
        
        return sales
    
    def getSales(self, startDate = None, orderAsc = False):
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
            sales += [Sale(itemID = elm[0],quantity=int(elm[1]),closeDate=elm[2],documentDescription=elm[3])]
        
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


if __name__ == '__main__':
    db = DB()
    db.connect()
    items = db.getItems()
    for item in items:
        print(item)

    print(len(items))


    sales = db.getItemSales(1407)
    for s in sales:
        print(s)

    print(len(sales))

    print()

    print(sales[0],sales[0].documentType)
    print(type(sales[0].closeDate))


    db.close()