import pandas as pd
import math

class UnidadesPorCaixaReader:

    def __init__(self, filename = '.data/UnidadesPorCaixa.xlsx',sheetName = 'UnidadesPorCaixa'):
        self.df = pd.read_excel(filename, sheet_name = sheetName)

        ID_COLUMN = 'ref.'
        PRODUTO_COLUMN = 'Produto'
        UNIDADESPORCAIXA_COLUMN = 'Unidades Por Caixa'

        self.items = list(self.df[(~self.df[ID_COLUMN].isnull())][ID_COLUMN])
        self.unidadesPorCaixa = list(self.df[(~self.df[ID_COLUMN].isnull())][UNIDADESPORCAIXA_COLUMN])


        for i in range(len(self.unidadesPorCaixa)):
            try:
                if (math.isnan(self.unidadesPorCaixa[i]) or self.unidadesPorCaixa[i] == "None"):
                    self.unidadesPorCaixa[i] = None
            except:
                pass

    
    def getItems(self):
        return self.items
    
    def getUnidadesPorCaixa(self):
        return self.unidadesPorCaixa
    
    def getAll(self):
        return self.items, self.unidadesPorCaixa