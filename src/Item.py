from ItemHistory import *

class Item:

    def __init__(self,ID = None, Description = None, CurrentStock = None):
        self.ID = ID
        self.Description = Description
        self.CurrentStock = CurrentStock
        self.itemHistory = ItemHistory(itemID=self.ID)
        self.shelfLife = None
        self.unidadesPorCaixa = None
        self.emTransito = 0
        self.config = None
        

    def addSale(self,sale):
        self.itemHistory.addSale(sale)
    
    def generateDFs(self):
        self.itemHistory.generateDFs()
    
    def getDemand(self,day1,day2,typeDoc):
        return self.itemHistory.getDemand(day1,day2,typeDoc)
        
    def __str__(self):
        return '{\n' + f"\tID={self.ID},\n\tDescription = {self.Description},\n\tCurrentStock = {self.CurrentStock},\n" + '}'
    
    def __repr__(self):
        return '{\n' + f"\tID={self.ID},\n\tDescription = {self.Description},\n\tCurrentStock = {self.CurrentStock},\n" + '}'
    
