import pandas as pd
import math

class ConfigReader:

    def __init__(self, filename = 'data/ItemBoxDetail.xlsx',sheetName = 'ItemBoxDetail'):
        self.df = pd.read_excel(filename, sheet_name = sheetName)

        ID_COLUMN = 'Ref.'
        PRODUTO_COLUMN = 'DESCRIÇÃO PORTUGAL'
        EMBALAGEM_COL = 'EMBALAGEM'
        CODIGO_NF_FORNECEDOR_COL = 'CODIGO NF FORNECEDOR'
        FORNECEDOR_COL = "FORNECEDOR"
        CATEGORIA_COL = "CATEGORIA"
        TRADEBRAS_SISTEM_CODE_COL = "TRADEBRAS SISTEMA CODE"
        SHELF_LIFE_COL = "SHELF LIFE"
        PRODUCTS_COL = "PRODUCTS"
        HS_CODE_COL = "HS CODE"
        NCM_COL = "NCM"
        C_COL = "C"
        L_COL = "L"
        A_COL = "A"
        M3_UNIT_COL = "M³ UNIT."
        EMBARQUE_COL = "EMBARQUE"
        PESO_LIQ_UNIT_COL = "PESO LIQ. UNIT."
        PESO_BRUTO_UNIT_COL = "PESO BRUTO UNIT."

        self.items = list(self.df[(~self.df[ID_COLUMN].isnull())][ID_COLUMN])
        self.descs = list(self.df[(~self.df[ID_COLUMN].isnull())][PRODUTO_COLUMN])
        self.embalagem = list(self.df[(~self.df[ID_COLUMN].isnull())][EMBALAGEM_COL])
        self.codigo_nf_fornecedor = list(self.df[(~self.df[ID_COLUMN].isnull())][CODIGO_NF_FORNECEDOR_COL])
        self.fornecedor = list(self.df[(~self.df[ID_COLUMN].isnull())][FORNECEDOR_COL])
        self.categoria = list(self.df[(~self.df[ID_COLUMN].isnull())][CATEGORIA_COL])
        self.tradebras_sistem_code = list(self.df[(~self.df[ID_COLUMN].isnull())][TRADEBRAS_SISTEM_CODE_COL])
        self.shelf_life = list(self.df[(~self.df[ID_COLUMN].isnull())][SHELF_LIFE_COL])
        self.products = list(self.df[(~self.df[ID_COLUMN].isnull())][PRODUCTS_COL])
        self.hs_code = list(self.df[(~self.df[ID_COLUMN].isnull())][HS_CODE_COL])
        self.ncm = list(self.df[(~self.df[ID_COLUMN].isnull())][NCM_COL])
        self.c = list(self.df[(~self.df[ID_COLUMN].isnull())][C_COL])
        self.l = list(self.df[(~self.df[ID_COLUMN].isnull())][L_COL])
        self.a = list(self.df[(~self.df[ID_COLUMN].isnull())][A_COL])
        self.m3_unit = list(self.df[(~self.df[ID_COLUMN].isnull())][M3_UNIT_COL])
        self.embarque = list(self.df[(~self.df[ID_COLUMN].isnull())][EMBARQUE_COL])
        self.peso_liq_unit = list(self.df[(~self.df[ID_COLUMN].isnull())][PESO_LIQ_UNIT_COL])
        self.peso_bruto_unit = list(self.df[(~self.df[ID_COLUMN].isnull())][PESO_BRUTO_UNIT_COL])
    

        configs = [self.embalagem,self.codigo_nf_fornecedor,self.fornecedor,self.categoria,self.tradebras_sistem_code,self.shelf_life,self.products,self.hs_code,self.ncm,self.c,self.l,self.a,self.m3_unit,self.embarque,self.peso_liq_unit,self.peso_bruto_unit]
        for config in configs:
            for i in range(len(config)):
                try:
                    if (math.isnan(config[i]) or config[i] == "None"):
                        config[i] = None
                except:
                    pass

        self.map = {}
        i = 0
        for itemID in self.items:
            dictElm = { \
                'embalagem':self.embalagem[i], \
                'codigo_nf_fornecedor':self.codigo_nf_fornecedor[i], \
                'fornecedor':self.fornecedor[i], \
                'categoria':self.categoria[i], \
                'tradebras_sistem_code':self.tradebras_sistem_code[i], \
                'shelf_life':self.shelf_life[i], \
                'products':self.products[i], \
                'hs_code':self.hs_code[i], \
                'ncm':self.ncm[i], \
                'c':self.c[i], \
                'l':self.l[i], \
                'a':self.a[i], \
                'm3_unit':self.m3_unit[i], \
                'embarque':self.embarque[i], \
                'peso_liq_unit':self.peso_liq_unit[i], \
                'peso_bruto_unit':self.peso_bruto_unit[i] \
                }
            self.map[itemID] = dictElm
            i = i + 1

    
    def getItems(self):
        return self.items
    
    def getMap(self):
        return self.map