import pandas as pd
import math

class ShelfLifeReader:

    def __init__(self, filename = '.data/ShelfLife.xlsx',sheetName = 'ShelfLife'):
        self.df = pd.read_excel(filename, sheet_name = sheetName)

        ID_COLUMN = 'ref.'
        PRODUTO_COLUMN = 'Produto'
        SHELFLIFE_COLUMN = 'Shelf Life'

        self.items = list(self.df[(~self.df[ID_COLUMN].isnull())][ID_COLUMN])
        self.shelfLifes = list(self.df[(~self.df[ID_COLUMN].isnull())][SHELFLIFE_COLUMN])

        for i in range(len(self.shelfLifes)):
            try:
                if (math.isnan(self.shelfLifes[i]) or self.shelfLifes[i] == "None"):
                    self.shelfLifes[i] = None
            except:
                pass

    
    def getItems(self):
        return self.items
    
    def getShelfLifes(self):
        return self.shelfLifes
    
    def getAll(self):
        return self.items, self.shelfLifes