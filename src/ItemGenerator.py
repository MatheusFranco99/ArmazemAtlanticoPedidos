from DB import *
from Item import *
from ItemHistory import *
from Sale import *
from ProgressBar import *
from datetime import datetime
import pandas as pd
from ShelfLifeReader import *
from UnidadesPorCaixaReader import *
import pickle
import os
from ConfigReader import ConfigReader

def datetimeToSqlDate(dt):
    ans = str(dt.year) + ":"
    if dt.month <= 9:
        ans = ans + "0"
    ans = ans + str(dt.month) + ":"
    if dt.day <= 9:
        ans = ans + "0"
    ans = ans + str(dt.day) + ": "

    if dt.hour <= 9:
        ans = ans + "0"
    ans = ans + str(dt.hour) + ":"
    if dt.minute <= 9:
        ans = ans + "0"
    ans = ans + str(dt.minute) + ":"
    if dt.second <= 9:
        ans = ans + "0"
    ans = ans + str(dt.second)
    return ans



class ItemGenerator:
    
    def __init__(self):
        self.items = {}
        self.lastDate = None

        fileExists = os.path.isfile('itemgen.pkl')
        if fileExists:
            self.load()
        
    def load(self):
        with open('itemgen.pkl','rb') as f:
            self.items = pickle.load(f)
            self.lastDate = pickle.load(f)
    
    def save(self):
        with open('itemgen.pkl','wb') as f:
            pickle.dump(self.items,f)
            pickle.dump(self.lastDate,f)
    
    def printSummary(self):
        lst = []
        for item in self.items.values():
            lst += [(item.ID,item.Description,item.itemHistory.len())]
        
        lst = sorted(lst, key=lambda tup: tup[0])

        for i in range(len(lst)):
            print(lst[i])


    
    def getItemsList(self):
        return list(self.items.values())

    def update(self,force = False):

        if force:
            self.items = {}
            self.lastDate = None
            self.generate()

        if len(self.items) == 0:
            self.generate()
        else:
            self.getNewSales()
        
        self.save()

    def getNewSales(self):

        db = DB()
        db.connect()
        
        itemsLst = db.getItems()

        print("\tGetting new items")
        pb = ProgressBar(n = len(itemsLst))
        for item in itemsLst:
            if item.ID not in self.items:
                self.items[item.ID] = item
            pb.step()

        itemLstIDs = []
        for item in itemsLst:
            itemLstIDs += [item.ID]
        
        idsToRemove = []
        for itemID in self.items:
            if itemID not in itemLstIDs:
                idsToRemove += [itemID]
        for itemID in idsToRemove:
                del self.items[itemID]

        print("\tGetting sales from",self.lastDate)
        nextLastDate = datetimeToSqlDate(datetime.now())
        allsales = db.getAllSales(startDate=self.lastDate,orderAsc = True)
        self.lastDate = nextLastDate

        print("\tAdding sales to each item")
        if len(allsales) > 0:
            pb = ProgressBar(n = len(allsales))
            for sale in allsales:
                try:
                    self.items[sale.itemID].addSale(sale)
                except:
                    pass
                pb.step()

        print("\tGenerating dataframes for each item")
        pb = ProgressBar(n = len(self.items))
        for item in self.items:
            self.items[item].generateDFs()
            pb.step()

        for item in self.items:
            self.items[item].shelfLife = None
            self.items[item].unidadesPorCaixa = None
        self.addShelfLife()
        self.addUnidadesPorCaixa()
        self.addConfigs()

        db.close()


    def generate(self):

        db = DB()
        db.connect()

        itemsLst = db.getItems()
        self.items = {}

        print("\tCreating items")
        pb = ProgressBar(n = len(itemsLst))
        for item in itemsLst:
            self.items[item.ID] = item
            pb.step()

        print("\tGetting all sales")
        pb = ProgressBar(n = 1)
        self.lastDate = datetimeToSqlDate(datetime.now())
        allsales = db.getAllSales(orderAsc = True)
        pb.step()
        db.close()

        print("\tAdding sales to each item")
        pb = ProgressBar(n = len(allsales))
        for sale in allsales:
            try:
                self.items[sale.itemID].addSale(sale)
            except:
                pass
            pb.step()

        print("\tGenerating dataframes for each item")
        pb = ProgressBar(n = len(self.items))
        for item in self.items:
            self.items[item].generateDFs()
            pb.step()

        self.addShelfLife()
        self.addUnidadesPorCaixa()
        self.addConfigs()
    
    def addShelfLife(self):
        slr = ShelfLifeReader()
        itemsID = slr.getItems()
        shelfLifes = slr.getShelfLifes()

        for i in range(len(itemsID)):
            try:
                self.items[itemsID[i]].shelfLife = float(shelfLifes[i])
            except:
                pass
        
    def addUnidadesPorCaixa(self):
        upcr = UnidadesPorCaixaReader()
        itemsID = upcr.getItems()
        unidadesPorCaixa = upcr.getUnidadesPorCaixa()

        for i in range(len(itemsID)):
            try:
                self.items[itemsID[i]].unidadesPorCaixa = float(unidadesPorCaixa[i])
                i = i + 1
            except:
                pass
    
    def addConfigs(self):
        cr = ConfigReader()
        crMap = cr.getMap()

        for itemID in crMap.keys():
            try:
                self.items[itemID].config = crMap[itemID]
            except:
                pass

        



