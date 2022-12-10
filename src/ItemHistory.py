from DB import *
from Sale import *
from datetime import datetime, timedelta
import pandas as pd

DATE_NOT_FOUND = "Date not found."

class ItemHistory:

    def __init__(self, itemID = None, sales = None):
        self.itemID = itemID
        self.sales = sales
        
        if self.sales == None:
            self.sales = []
    
    def len(self):
        return len(self.sales)
    
    def addSale(self,sale):
        self.sales += [sale]

    def generateSales(self,db):
        self.sales = db.getItemSales(self.itemID, startDate = "2020:01:01 00:00:00", orderAsc = True)

    def getLastSalesDate(self, typeDoc = FATURA):
        idx = len(self.sales)-1
        while(idx >= 0):
            if (self.sales[idx].documentType == typeDoc):
                return self.sales[idx].closeDate
            idx = idx - 1
        return DATE_NOT_FOUND
    
    def generateDFs(self):

        self.dfs = {FATURA:None, FATURA_PROFORMA:None, NOTA_DE_ENCOMENDA:None}
        
        for typeDoc in [FATURA, FATURA_PROFORMA, NOTA_DE_ENCOMENDA]:
            
            dates = []
            sales = []

            for sale in self.sales:
                if sale.documentType == typeDoc:
                    saleDate = datetime(sale.closeDate.year,sale.closeDate.month,sale.closeDate.day)
                    sales  += [sale.quantity]
                    dates += [saleDate]

            d = {'date':dates,'sale':sales}
            df = pd.DataFrame(data = d)
            # df.set_index('date', inplace=True)
            self.dfs[typeDoc] = df
    

    def getDemand(self,day1,day2,typeDoc):
        df = self.dfs[typeDoc]
        return df[(df['date']>day1) & (df['date']<day2)]['sale'].sum()
    
    