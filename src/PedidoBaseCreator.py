import xlsxwriter
from datetime import datetime,date
from ShelfLifeReader import *
from UnidadesPorCaixaReader import *
from Day import *
from ExcelLetters import *
from DemandEstimator import *
import math
# from ProphetDemandEstimator import *
from ProgressBar import *

ID_COL = 0
DESCRIPTION_COL = 1
UNIDADESPORCAIXA_COL = 2
CURRENTSTOCK_COL = 3
SHELFLIFE_COL = 4
EMTRANSITO_COL = 5

ID_COL_LETTER = 'A'
DESCRIPTION_COL_LETTER = 'B'
UNIDADESPORCAIXA_COL_LETTER = 'C'
CURRENTSTOCK_COL_LETTER = 'D'
SHELFLIFE_COL_LETTER = 'E'

class PedidoBaseCreator:


    def __init__(self, filename = 'PedidoBase.xlsx'):
        if filename[-5:] != ".xlsx":
            filename = filename + ".xlsx"
        self.filename = filename
        self.workbook = xlsxwriter.Workbook(filename)
        today = date.today()
        self.worksheet = self.workbook.add_worksheet(name=str(today))

        self.addFormats()

        self.row = 0
        self.total = 1

        self.ProphetPrediction = {}
            
    def addFormats(self):
        self.titleFormat = self.workbook.add_format()
        self.titleFormat.set_bold()
        self.titleFormat.set_font_name('Calibri (Body)')
        self.titleFormat.set_font_size(10)
        self.titleFormat.set_align('center')
        self.titleFormat.set_align('bottom')

        self.titleFormat = self.workbook.add_format()
        self.titleFormat.set_bold()
        self.titleFormat.set_font_name('Calibri (Body)')
        self.titleFormat.set_font_size(10)
        self.titleFormat.set_align('center')
        self.titleFormat.set_align('bottom')

        self.columnNameFormat = self.workbook.add_format()
        self.columnNameFormat.set_bold()
        self.columnNameFormat.set_font_name('Calibri (Body)')
        self.columnNameFormat.set_font_size(10)
        self.columnNameFormat.set_align('center')
        self.columnNameFormat.set_align('vcenter')
        self.columnNameFormat.set_bottom()
        self.columnNameFormat.set_top()
        self.columnNameFormat.set_left()
        self.columnNameFormat.set_right()
        self.columnNameFormat.set_text_wrap()

        self.valueFormat = self.workbook.add_format()
        self.valueFormat.set_font_name('Calibri (Body)')
        self.valueFormat.set_font_size(10)
        self.valueFormat.set_align('bottom')
        self.valueFormat.set_bottom()
        self.valueFormat.set_top()
        self.valueFormat.set_left()
        self.valueFormat.set_right()
    

    def write(self,items,typeDoc):
        self.setTemplate()
        self.populateItems(items)
        self.populateLast6And3MonthsPrediction(items,typeDoc)
        self.populateProphetPrediction(items,typeDoc,datetime(2020,1,1))
        self.populateProphetPrediction(items,typeDoc,datetime(2021,1,1))
        self.populateProphetPrediction(items,typeDoc,datetime(2022,1,1))
        self.close()



    def setTemplate(self):
        self.worksheet.merge_range('A1:E1',f'Pedido em {date.today().strftime("%d/%m/%Y")}',self.titleFormat)

        self.worksheet.set_row(1, 100.75)
        self.worksheet.set_column(0, 0, 4.17) # column a
        self.worksheet.set_column(1, 1, 55) # column B
        self.worksheet.set_column(2, 50, 8) # rest of columns
        
        # Ref, Produto, Packing Unidades por Caixa, Stock, Shelf life, transito

        # media (media 6 meses, media 3 meses): consume mensal estimado, stock provavel em 2 meses, stock ideal em 2 meses, pedido em unidades, pedido em caixas
        
        # Prophet: quanto sera consumido nos proximos 2 meses, stock provavel em 2 meses, stock ideal daqui a 2 meses, pedido em unidades, pedido em caixas


        self.worksheet.write_string('A2','ref.',self.columnNameFormat)
        self.worksheet.write_string('B2','Produto',self.columnNameFormat)
        self.worksheet.write_string('C2','Packing Unidades por Caixa',self.columnNameFormat)
        self.worksheet.write_string('D2','Stock em Unidades na Data do Produto',self.columnNameFormat)
        self.worksheet.write_string('E2','Shelf Life',self.columnNameFormat)
        self.worksheet.write_string('F2','Em trânsito',self.columnNameFormat)

        self.CURRENT_COL = 'H'


    def getProgressState(self):
        return self.row, self.total

    def populateItems(self,items,itemsInTransactionMap = {}):
        self.itemsInTransactionMap = itemsInTransactionMap
        self.itemRow = {}
        self.row = 2
        self.total = len(items)
        row = 2
        for item in items:
            self.worksheet.write_number(row,ID_COL,item.ID,self.valueFormat)
            self.worksheet.write_string(row,DESCRIPTION_COL,item.Description,self.valueFormat)
            self.worksheet.write_number(row,CURRENTSTOCK_COL,item.CurrentStock,self.valueFormat)
            try:
                self.worksheet.write_number(row,SHELFLIFE_COL,item.shelfLife,self.valueFormat)
            except:
                pass
            try:
                self.worksheet.write_number(row,UNIDADESPORCAIXA_COL,item.unidadesPorCaixa,self.valueFormat)
            except:
                pass
            try:
                self.worksheet.write_number(row,EMTRANSITO_COL,itemsInTransactionMap[item.ID],self.valueFormat)
            except:
                self.worksheet.write_number(row,EMTRANSITO_COL,0,self.valueFormat)
            self.itemRow[item.ID] = row
            row = row + 1
            self.row = row
    

    def populateLast6And3MonthsPrediction(self,items,typeDoc):


        # media (media 6 meses, media 3 meses): consume mensal estimado, stock provavel em 2 meses, stock ideal em 2 meses, pedido em unidades, pedido em caixas
        

        c1 = self.CURRENT_COL
        c2 = ExcelLetters.increase(c1)
        c3 = ExcelLetters.increase(c2)
        c4 = ExcelLetters.increase(c3)
        c5 = ExcelLetters.increase(c4)

        self.CURRENT_COL = ExcelLetters.increaseN(self.CURRENT_COL,6)


        day1Str = DemandEstimator.day1Str
        day2Str = DemandEstimator.day2Str

        self.worksheet.merge_range(f'{c1}1:{c5}1',f'M(M(últimos 6 meses),M(últimos 3 meses)) ({day1Str}, {day2Str})',self.columnNameFormat)

        self.worksheet.write_string(f'{c1}2', 'Consumo mensal estimado', self.columnNameFormat)
        self.worksheet.write_string(f'{c2}2', 'Stock estimado daqui a 2 meses', self.columnNameFormat)
        self.worksheet.write_string(f'{c3}2', 'Stock ideal daqui a 2 meses', self.columnNameFormat)
        self.worksheet.write_string(f'{c4}2', 'Pedido em unidades', self.columnNameFormat)
        self.worksheet.write_string(f'{c5}2', 'Pedido em caixas', self.columnNameFormat)

        self.M6M3BoxesMap = {}

        self.total = len(items)
        self.row = 1
        for item in items:
            self.row +=1
            demand = 0
            stockEstimation = 0
            idealStock = 0
            requestUnities = 0
            requestBoxes = 0
            try:
                demand = DemandEstimator.estimate(item,typeDoc)
                inTransit = 0
                if item.ID in self.itemsInTransactionMap:
                    inTransit = self.itemsInTransactionMap[item.ID]
                stockEstimation = max(item.CurrentStock + inTransit - 2*demand + item.emTransito,0)
                idealStock = max(item.shelfLife*demand,0)
                requestUnities = max(idealStock - stockEstimation,0)
                requestBoxes = math.ceil(requestUnities/item.unidadesPorCaixa)
            except:
                pass
            
            row = self.itemRow[item.ID]
            rowTxt = row+1
            try:
                self.worksheet.write_number(f'{c1}{rowTxt}',demand,self.valueFormat)
                self.worksheet.write_number(f'{c2}{rowTxt}',stockEstimation,self.valueFormat)
                self.worksheet.write_number(f'{c3}{rowTxt}',idealStock,self.valueFormat)
                self.worksheet.write_number(f'{c4}{rowTxt}',requestUnities,self.valueFormat)
                self.worksheet.write_number(f'{c5}{rowTxt}',requestBoxes,self.valueFormat)
            except:
                pass

            self.M6M3BoxesMap[item.ID] = requestBoxes
    
    def getLast6And3MonthsPrediction(self):
        return self.M6M3BoxesMap
    

    # def populateProphetPrediction(self,items,typeDoc,startDate):


    #     # Prophet: consumo esperado em 2 meses, stock provavel em 2 meses, consumo esperado em shelflife meses após 2 meses, stock ideal daqui a 2 meses, pedido em unidades, pedido em caixas


    #     c1 = self.CURRENT_COL
    #     c2 = ExcelLetters.increase(c1)
    #     c3 = ExcelLetters.increase(c2)
    #     c4 = ExcelLetters.increase(c3)
    #     c5 = ExcelLetters.increase(c4)
    #     c6 = ExcelLetters.increase(c5)

    #     self.CURRENT_COL = ExcelLetters.increaseN(self.CURRENT_COL,7)

    #     self.worksheet.merge_range(f'{c1}1:{c5}1',f'Facebook Prophet Estimator (since {startDate.strftime("%d/%m/%Y")})',self.columnNameFormat)

    #     self.worksheet.write_string(f'{c1}2', 'Consumo esperado em 2 meses', self.columnNameFormat)
    #     self.worksheet.write_string(f'{c2}2', 'Stock estimado daqui a 2 meses', self.columnNameFormat)
    #     self.worksheet.write_string(f'{c3}2', 'Consumo esperado em (ShelfLife) meses após 2 meses', self.columnNameFormat)
    #     self.worksheet.write_string(f'{c4}2', 'Stock ideal daqui a 2 meses', self.columnNameFormat)
    #     self.worksheet.write_string(f'{c5}2', 'Pedido em unidades', self.columnNameFormat)
    #     self.worksheet.write_string(f'{c6}2', 'Pedido em caixas', self.columnNameFormat)


    #     print("Running Facebook Prophet Estimator for all items.")
    #     pb = ProgressBar(len(items))

    #     self.ProphetPrediction[startDate] = {}

    #     self.total = len(items)
    #     self.row = 1
    #     for item in items:
    #         self.row += 1
    #         next2MonthsDemand = 0
    #         stockEstimation = 0
    #         nextShelfLifeDemand = 0
    #         idealStock = 0
    #         requestUnities = 0
    #         requestBoxes = 0
    #         try:
    #             prophetModel = ProphetDemandEstimator.getModel(item,typeDoc,startDate=startDate)
    #             next2MonthsDemand = ProphetDemandEstimator.estimate(prophetModel,2)
    #             inTransit = 0
    #             if item.ID in self.itemsInTransactionMap:
    #                 inTransit = self.itemsInTransactionMap[item.ID]
    #             stockEstimation = max(item.CurrentStock + inTransit - next2MonthsDemand + item.emTransito,0)
    #             print(item.shelfLife+2)
    #             nextShelfLifeDemand = ProphetDemandEstimator.estimate(prophetModel,int(item.shelfLife + 2)) - next2MonthsDemand
    #             idealStock = nextShelfLifeDemand
    #             requestUnities = max(idealStock - stockEstimation,0)
    #             requestBoxes = math.ceil(requestUnities/item.unidadesPorCaixa)
    #         except:
    #             pass

    #         row = self.itemRow[item.ID]
    #         rowTxt = row+1
    #         try:
    #             self.worksheet.write_number(f'{c1}{rowTxt}',next2MonthsDemand,self.valueFormat)
    #             self.worksheet.write_number(f'{c2}{rowTxt}',stockEstimation,self.valueFormat)
    #             self.worksheet.write_number(f'{c3}{rowTxt}',nextShelfLifeDemand,self.valueFormat)
    #             self.worksheet.write_number(f'{c4}{rowTxt}',idealStock,self.valueFormat)
    #             self.worksheet.write_number(f'{c5}{rowTxt}',requestUnities,self.valueFormat)
    #             self.worksheet.write_number(f'{c6}{rowTxt}',requestBoxes,self.valueFormat)
    #         except:
    #             pass

    #         self.ProphetPrediction[startDate][item.ID] = requestBoxes

    #         pb.step()
    
    # def getProphetPrediction(self,startDate):
    #     return self.ProphetPrediction[startDate]
    


    def close(self):
        self.workbook.close()