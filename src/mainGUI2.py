from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Sale import FATURA,FATURA_PROFORMA,NOTA_DE_ENCOMENDA
import api
import random

from PyQt5 import uic
from PyQt5 import sip

import sys
import threading
from PedidoBaseCreator import *
from datetime import datetime
import time
from ShelfLifeQtyEditor import *
from ConfigEditor import *
from InvoiceProcessor import *
from PedidoFinalCreator import *

import resources_rc

from Item import *
from Canvas import *


def insertSuffix(filename,suffix,ending):
    if ending in filename:
        idx = filename.find(ending)
        return filename[:idx] + suffix + ending
    else:
        return filename + suffix + ending



#   ============================================
#   UI Class
#   ============================================

class UI(QMainWindow):
    def __init__(self,fname):
        super(UI,self).__init__()

        uic.loadUi(fname,self)
    def showWindow(self,width,height):
        self.resize(width,height)
        self.show()
    def hideWindow(self):
        self.hide()


#   ============================================
#   Switch window 
#   ============================================

def openNewWindow(origin,destination):
    destination.showWindow(origin.width(),origin.height())
    destination.move(origin.x(),origin.y())
    origin.hideWindow()


#   ============================================
#   Packing List
#   ============================================

def packingListBrowseFile(ui):
    global BROWSER_DIR
    fname = QFileDialog.getOpenFileName(ui,'Open file',BROWSER_DIR)
    try:
        if(fname[0]!=''):
            for i in range(len(fname)-1):
                fileName = fname[i]
                ui.PackingListFilesTable.insertRow(ui.PackingListFilesTable.rowCount())
                ui.PackingListFilesTable.setItem(ui.PackingListFilesTable.rowCount()-1,0,QTableWidgetItem(fileName))
                for i in range(len(fileName)-1,-1,-1):
                    if fileName[i] == '/':
                        BROWSER_DIR = fileName[:i]
                        break

    except:
        pass

def gatherItemsInTransaction():
    global itemsInTransaction
    global newRequestPackingListItems


    priorIDs = []
    newIDs = []
    rows = newRequestPackingListItems.ItemsTable.rowCount()
    for row in range(rows):
        priorid = int(float((newRequestPackingListItems.ItemsTable.item(row,0).text())))
        priordesc = str((newRequestPackingListItems.ItemsTable.item(row,1).text()))
        priorIDs += [(priorid,priordesc)]

    rows = newRequestPackingListItems.ItemsConfirmTable.rowCount()
    for row in range(rows):
        newIDs += [int(float((newRequestPackingListItems.ItemsConfirmTable.item(row,0).text())))]

    idmap = {}
    i = 0
    for priorID in priorIDs:
        idmap[priorID] = newIDs[i]
        i = i+1

    newItemsInTransaction = {}
    for (itemID,desc) in itemsInTransaction:
        if (itemID,desc) not in priorIDs:
            if itemID in newItemsInTransaction:
                newItemsInTransaction[itemID] += itemsInTransaction[(itemID,desc)]
            else:
                newItemsInTransaction[itemID] = itemsInTransaction[(itemID,desc)]
        else:
            newItemID = idmap[(itemID,desc)]
            if newItemID in newItemsInTransaction:
                newItemsInTransaction[newItemID] += itemsInTransaction[(itemID,desc)]
            else:
                newItemsInTransaction[newItemID] = itemsInTransaction[(itemID,desc)]

    return newItemsInTransaction


def openPackingListItems(newRequestPackingList,newRequestPackingListItems):
    # get files from packing list window
    global items, itemsInTransaction
    rows = newRequestPackingList.PackingListFilesTable.rowCount()
    files = []
    for row in range(rows):
        files += [str(newRequestPackingList.PackingListFilesTable.item(row,0).text())]

    itemMap = {}
    for filename in files:
        invoiceProcessor = InvoiceProcessor(filename)
        ids, descs, qts = invoiceProcessor.getLists()
        for i in range(len(ids)):
            try:
                ids[i] = float(ids[i])
                ids[i] = int(ids[i])

                key = (ids[i],descs[i])
                if key not in itemMap:
                    itemMap[key] = qts[i]
                else:
                    itemMap[key] += qts[i]
            except:
                pass

    # get DB associate and best match from DB
    # db_desc: list(desc, match)
    # best_desc: list(ID, desc, match)
    db_desc, best_desc = InvoiceProcessor.returnMatchesDescsWithId(items,itemMap)


    # clear packingListItems window table
    newRequestPackingListItems.ItemsTable.setRowCount(0)

    itemsInTransaction = {}

    row = 0
    i = 0
    for (itemID, desc) in itemMap:
        if desc != db_desc[i][0]:
            newRequestPackingListItems.ItemsTable.insertRow(row)

            newRequestPackingListItems.ItemsTable.setItem(row,0,QTableWidgetItem(str(itemID)))
            newRequestPackingListItems.ItemsTable.setItem(row,1,QTableWidgetItem(str(desc)))

            newRequestPackingListItems.ItemsTable.setItem(row,2,QTableWidgetItem(str(db_desc[i][0])))
            newRequestPackingListItems.ItemsTable.setItem(row,3,QTableWidgetItem(str(db_desc[i][1])))

            newRequestPackingListItems.ItemsTable.setItem(row,4,QTableWidgetItem(str(best_desc[i][0])))
            newRequestPackingListItems.ItemsTable.setItem(row,5,QTableWidgetItem(str(best_desc[i][1])))
            newRequestPackingListItems.ItemsTable.setItem(row,6,QTableWidgetItem(str(best_desc[i][2])))

            newRequestPackingListItems.ItemsConfirmTable.insertRow(row)

            newRequestPackingListItems.ItemsConfirmTable.setItem(row,0,QTableWidgetItem(str(itemID)))

            row = row + 1
        itemsInTransaction[(itemID,desc)] = itemMap[(itemID,desc)]
        i = i + 1
    newRequestPackingListItems.ItemsTable.setColumnWidth(0, 50)
    newRequestPackingListItems.ItemsTable.setColumnWidth(1, 400)
    newRequestPackingListItems.ItemsTable.setColumnWidth(2, 400)
    newRequestPackingListItems.ItemsTable.setColumnWidth(3, 160)
    newRequestPackingListItems.ItemsTable.setColumnWidth(4, 140)
    newRequestPackingListItems.ItemsTable.setColumnWidth(5, 400)
    newRequestPackingListItems.ItemsTable.setColumnWidth(6, 140)
    openNewWindow(newRequestPackingList,newRequestPackingListItems)



#   ============================================
#   New Request - Items
#   ============================================

def setupNewRequestItems(ui):
    global items
    # items = []
    # for i in range(100):
    #     items += [Item(ID=i,Description="No"+str(i))]


    itemsFrameLayout = QVBoxLayout()
    itemsFrameLayout.setObjectName("ItemsFrameLayout")

    itemsFrameLayout.setContentsMargins(0, 0, 0, 0)
    itemsFrameLayout.setSpacing(-1)

    _translate = QCoreApplication.translate

    checkboxesTuples = []

    for i in range(len(items)):
        checkbox = QCheckBox(items[i].Description)
        checkbox.setChecked(True)
        itemsFrameLayout.addWidget(checkbox)
        checkboxesTuples += [(checkbox,items[i].ID)]
        font = QFont()
        font.setFamily(".AppleSystemUIFont")
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        checkbox.setFont(font)
        checkbox.setStyleSheet("QCheckBox {\n"
"\n"
"    color: rgb(218, 215, 224);\n"
"    font: 13pt \".AppleSystemUIFont\";\n"
"\n"
"}")
    
    ui.SelectItemsLabel.setText(_translate("newRequestItems", "Selecionar items"))
    ui.checkboxesTuples = checkboxesTuples
    ui.itemsWidget.setLayout(itemsFrameLayout)


#   ============================================
#   Search Inactive
#   ============================================

def setupSearchInactives(ui):
    global items
    lst = []
    for item in items:
        lst += [(item.ID,item.Description,item.itemHistory.getLastSalesDate())]
    
    lstWithDate = []
    lstWithoutDate = []
    for elm in lst:
        if type(elm[2]) == str:
            lstWithoutDate += [elm]
        else:
            lstWithDate += [elm]


    lstWithDate = sorted(lstWithDate, key=lambda tup: tup[2])

    lst = lstWithoutDate+lstWithDate
    row = 0
    for elm in lst:
        ui.ItemsTable.insertRow(row)
        ui.ItemsTable.setItem(row,0,QTableWidgetItem(str(elm[0])))
        ui.ItemsTable.setItem(row,1,QTableWidgetItem(elm[1]))
        ui.ItemsTable.setItem(row,2,QTableWidgetItem(str(elm[2])))
        row = row + 1

    ui.ItemsTable.setColumnWidth(1, 400)


#   ============================================
#   Configuration
#   ============================================

def setupConfiguration(ui):
    global items
    row = 0
    for item in items:
        ui.PedidoBaseTable.insertRow(row)
        ui.PedidoBaseTable.setItem(row,0,QTableWidgetItem(str(item.ID)))
        ui.PedidoBaseTable.setItem(row,1,QTableWidgetItem(item.Description))
        ui.PedidoBaseTable.setItem(row,2,QTableWidgetItem(str(item.shelfLife)))
        ui.PedidoBaseTable.setItem(row,3,QTableWidgetItem(str(item.unidadesPorCaixa)))
        row = row + 1
    ui.PedidoBaseTable.setColumnWidth(1, 400)


    row = 0
    for item in items:
        if item.config != None:
            ui.PedidoFinalTable.insertRow(row)
            ui.PedidoFinalTable.setItem(row,0,QTableWidgetItem(str(item.ID)))
            ui.PedidoFinalTable.setItem(row,1,QTableWidgetItem(item.Description))
            ui.PedidoFinalTable.setItem(row,2,QTableWidgetItem(str(item.config['embalagem'])))
            ui.PedidoFinalTable.setItem(row,3,QTableWidgetItem(str(item.config['codigo_nf_fornecedor'])))
            ui.PedidoFinalTable.setItem(row,4,QTableWidgetItem(str(item.config['fornecedor'])))
            ui.PedidoFinalTable.setItem(row,5,QTableWidgetItem(str(item.config['categoria'])))
            ui.PedidoFinalTable.setItem(row,6,QTableWidgetItem(str(item.config['tradebras_sistem_code'])))
            ui.PedidoFinalTable.setItem(row,7,QTableWidgetItem(str(item.config['shelf_life'])))
            ui.PedidoFinalTable.setItem(row,8,QTableWidgetItem(str(item.config['products'])))
            ui.PedidoFinalTable.setItem(row,9,QTableWidgetItem(str(item.config['hs_code'])))
            ui.PedidoFinalTable.setItem(row,10,QTableWidgetItem(str(item.config['ncm'])))
            ui.PedidoFinalTable.setItem(row,11,QTableWidgetItem(str(item.config['c'])))
            ui.PedidoFinalTable.setItem(row,12,QTableWidgetItem(str(item.config['l'])))
            ui.PedidoFinalTable.setItem(row,13,QTableWidgetItem(str(item.config['a'])))
            ui.PedidoFinalTable.setItem(row,14,QTableWidgetItem(str(item.config['m3_unit'])))
            ui.PedidoFinalTable.setItem(row,15,QTableWidgetItem(str(item.config['embarque'])))
            ui.PedidoFinalTable.setItem(row,16,QTableWidgetItem(str(item.config['peso_liq_unit'])))
            ui.PedidoFinalTable.setItem(row,17,QTableWidgetItem(str(item.config['peso_bruto_unit'])))
            row = row + 1
    ui.PedidoFinalTable.setColumnWidth(0, 80)
    ui.PedidoFinalTable.setColumnWidth(1, 400)
    ui.PedidoFinalTable.setColumnWidth(2, 120)
    ui.PedidoFinalTable.setColumnWidth(3, 120)
    ui.PedidoFinalTable.setColumnWidth(4, 100)
    ui.PedidoFinalTable.setColumnWidth(5, 100)
    ui.PedidoFinalTable.setColumnWidth(6, 120)
    ui.PedidoFinalTable.setColumnWidth(7, 100)
    ui.PedidoFinalTable.setColumnWidth(8, 400)
    ui.PedidoFinalTable.setColumnWidth(9, 140)
    ui.PedidoFinalTable.setColumnWidth(10, 140)
    ui.PedidoFinalTable.setColumnWidth(11, 80)
    ui.PedidoFinalTable.setColumnWidth(12, 80)
    ui.PedidoFinalTable.setColumnWidth(13, 80)
    ui.PedidoFinalTable.setColumnWidth(14, 120)
    ui.PedidoFinalTable.setColumnWidth(15, 80)
    ui.PedidoFinalTable.setColumnWidth(16, 80)
    ui.PedidoFinalTable.setColumnWidth(17, 100)

def turnToFloat(x):
    try:
        if ',' in x:
            for i in range(len(x)):
                if x[i] == ",":
                    x[i] = "."
                    break
        return float(x)
    except:
        return x

def turnToInt(x):
    try:
        if ',' in x:
            for i in range(len(x)):
                if x[i] == ",":
                    x[i] = "."
                    break
        return int(float(x))
    except:
        return x



def configurationPedidoFinalSave(ui):
    global items
    rows = ui.PedidoFinalTable.rowCount()
    lst = []
    for row in range(rows):
        id = str(ui.PedidoFinalTable.item(row,0).text())
        desc = str(ui.PedidoFinalTable.item(row,1).text())
        embalagem = str(ui.PedidoFinalTable.item(row,2).text())
        codigo_nf_fornecedor = str(ui.PedidoFinalTable.item(row,3).text())
        fornecedor = str(ui.PedidoFinalTable.item(row,4).text())
        categoria = str(ui.PedidoFinalTable.item(row,5).text())
        tradebras_sistem_code = str(ui.PedidoFinalTable.item(row,6).text())
        shelf_life = str(ui.PedidoFinalTable.item(row,7).text())
        products = str(ui.PedidoFinalTable.item(row,8).text())
        hs_code = str(ui.PedidoFinalTable.item(row,9).text())
        ncm = str(ui.PedidoFinalTable.item(row,10).text())
        c = str(ui.PedidoFinalTable.item(row,11).text())
        l = str(ui.PedidoFinalTable.item(row,12).text())
        a = str(ui.PedidoFinalTable.item(row,13).text())
        m3_unit = str(ui.PedidoFinalTable.item(row,14).text())
        embarque = str(ui.PedidoFinalTable.item(row,15).text())
        peso_liq_unit = str(ui.PedidoFinalTable.item(row,16).text())
        peso_bruto_unit = str(ui.PedidoFinalTable.item(row,17).text())



        id = turnToInt(id)
        c = turnToFloat(c)
        l = turnToFloat(l)
        a = turnToFloat(a)
        m3_unit = turnToFloat(m3_unit)
        peso_liq_unit = turnToFloat(peso_liq_unit)
        peso_bruto_unit = turnToFloat(peso_bruto_unit)

        lst += [(id,desc,embalagem,codigo_nf_fornecedor,fornecedor,categoria,tradebras_sistem_code,shelf_life,products,hs_code,ncm,c,l,a,m3_unit,embarque,peso_liq_unit,peso_bruto_unit)]
    
    # for elm in lst:
    #     print(elm)
    ConfigEditor.update(lst)

    items = api.getItemsList()

def configurationPedidoBaseSave(ui):
    global items
    rows = ui.PedidoBaseTable.rowCount()
    lst = []
    for row in range(rows):
        id = str(ui.PedidoBaseTable.item(row,0).text())
        desc = str(ui.PedidoBaseTable.item(row,1).text())
        shelfLife = str(ui.PedidoBaseTable.item(row,2).text())
        qtd = str(ui.PedidoBaseTable.item(row,3).text())
        try:
            id = int(float(id))
        except:
            pass
        try:
            if ',' in shelfLife:
                for i in range(len(shelfLife)):
                    if shelfLife[i] == ",":
                        shelfLife[i] = "."
                        break
            shelfLife = float(shelfLife)
        except:
            pass
        try:
            qtd = float(qtd)
        except:
            pass
        lst += [(id,desc,shelfLife,qtd)]
    
    # for elm in lst:
    #     print(elm)
    ShelfLifeQtyEditor.update(lst)

    items = api.getItemsList()

def configurationPedidoBaseAddRow(ui):
    row = ui.PedidoBaseTable.rowCount()
    # row = row + 1
    ui.PedidoBaseTable.insertRow(row)
    ui.PedidoBaseTable.setItem(row,0,QTableWidgetItem(""))
    ui.PedidoBaseTable.setItem(row,1,QTableWidgetItem(""))
    ui.PedidoBaseTable.setItem(row,2,QTableWidgetItem(""))
    ui.PedidoBaseTable.setItem(row,3,QTableWidgetItem(""))


def configurationPedidoFinalAddRow(ui):
    row = ui.PedidoFinalTable.rowCount()
    # row = row + 1

    ui.PedidoFinalTable.insertRow(row)
    ui.PedidoFinalTable.setItem(row,0,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,1,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,2,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,3,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,4,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,5,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,6,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,7,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,8,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,9,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,10,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,11,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,12,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,13,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,14,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,15,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,16,QTableWidgetItem(''))
    ui.PedidoFinalTable.setItem(row,17,QTableWidgetItem(''))


#   ============================================
#   New Request - Generate
#   ============================================

def generateRequest():
    global items,filename,itemsInTransaction
    global newRequestModels, mainUI,newRequestGenerating,newRequestDone

    M6M3 = newRequestModels.Mean63CheckBox.isChecked()
    FBP2020 = newRequestModels.FBP2020CheckBox.isChecked()
    FBP2021 = newRequestModels.FBP2021CheckBox.isChecked()

    docTypeStr = newRequestModels.DocumentTypeCheckBox.currentText()
    docType = FATURA
    if docTypeStr == "Fatura Proforma":
        docType = FATURA_PROFORMA
    if docTypeStr == "Nota de Encomenda":
        docType = NOTA_DE_ENCOMENDA

    totalSteps = 1 + (M6M3 == True) + (FBP2020 == True) + (FBP2021 == True)
    currentStep = 1
    
    filename = newRequestModels.SaveAsLineEdit.text()

    newRequestGenerating.LogLabel.setText("Log: Creating excel document.")
    QCoreApplication.processEvents()
    pdc = PedidoBaseCreator(filename=filename)
    
    newRequestGenerating.LogLabel.setText("Log: Setting up excel template.")
    
    QCoreApplication.processEvents()
    pdc.setTemplate()

    itemInTransitMap=gatherItemsInTransaction()
    newRequestGenerating.LogLabel.setText("Log: Populating item:")
    t = threading.Thread(target=lambda: pdc.populateItems(items,itemsInTransactionMap=itemInTransitMap), args=())
    t.start()
    while(t.is_alive()):
        state = pdc.getProgressState()
        row = state[0]-1
        total = state[1]
        newRequestGenerating.LogLabel.setText("Log: Populating item: " + str(row) + ".")

        value = row/total * 100/totalSteps + (100/totalSteps) * (currentStep-1)
        newRequestGenerating.progressBar.setValue(int(value))
        
        QCoreApplication.processEvents()
    currentStep += 1


    if M6M3:
        newRequestGenerating.LogLabel.setText("Log: Estimating with Mean(6,3). Item:")
        t = threading.Thread(target=lambda: pdc.populateLast6And3MonthsPrediction(items,docType), args=())
        t.start()
        while(t.is_alive()):
            state = pdc.getProgressState()
            row = state[0]-1
            total = state[1]
            newRequestGenerating.LogLabel.setText("Log: Estimating with Mean(6,3). Item:" + str(row) + ".")
            
            value = row/total * 100/totalSteps + (100/totalSteps) * (currentStep-1)
            newRequestGenerating.progressBar.setValue(int(value))
            
            QCoreApplication.processEvents()
        currentStep+=1
    if M6M3:
        requestBoxesMap = pdc.getLast6And3MonthsPrediction()
        pedidoFinalM6M3Filename = insertSuffix(filename,"A.A.M6M3",".xlsx")
        pfc = PedidoFinalCreator(filename=pedidoFinalM6M3Filename)
        pfc.addItems(items,requestBoxesMap)



    if FBP2020:
        newRequestGenerating.LogLabel.setText("Log: Estimating with Facebook Prophet 2020. Item:")
        t = threading.Thread(target=lambda: pdc.populateProphetPrediction(items,docType,datetime(2020,1,1)), args=())
        t.start()
        while(t.is_alive()):
            state = pdc.getProgressState()
            row = state[0]-1
            total = state[1]
            newRequestGenerating.LogLabel.setText("Log: Estimating with Facebook Prophet 2020. Item:" + str(row) + ".")
            
            value = row/total * 100/totalSteps + (100/totalSteps) * (currentStep-1)
            newRequestGenerating.progressBar.setValue(int(value))
            QCoreApplication.processEvents()
        currentStep+=1
    if FBP2020:
        requestBoxesMap = pdc.getProphetPrediction(datetime(2020,1,1))
        pedidoFinalFilename = insertSuffix(filename,"A.A.FBP2020",".xlsx")
        pfc = PedidoFinalCreator(filename=pedidoFinalFilename)
        pfc.addItems(items,requestBoxesMap)

    if FBP2021:
        newRequestGenerating.LogLabel.setText("Log: Estimating with Facebook Prophet 2021. Item:")
        t = threading.Thread(target=lambda: pdc.populateProphetPrediction(items,docType,datetime(2021,1,1)), args=())
        t.start()
        while(t.is_alive()):
            state = pdc.getProgressState()
            row = state[0]-1
            total = state[1]
            newRequestGenerating.LogLabel.setText("Log: Estimating with Facebook Prophet 2021. Item:" + str(row) + ".")
            
            value = row/total * 100/totalSteps + (100/totalSteps) * (currentStep-1)
            newRequestGenerating.progressBar.setValue(int(value))
            QCoreApplication.processEvents()
        currentStep+=1
    if FBP2021:
        requestBoxesMap = pdc.getProphetPrediction(datetime(2021,1,1))
        pedidoFinalFilename = insertSuffix(filename,"A.A.FBP2021",".xlsx")
        pfc = PedidoFinalCreator(filename=pedidoFinalFilename)
        pfc.addItems(items,requestBoxesMap)

    pdc.close()
    filename = pdc.filename

    newRequestGenerating.progressBar.setValue(100)
    openNewWindow(newRequestGenerating,newRequestDone)
    newRequestDone.InFileLabel.setText("em: " + str(filename))
    QCoreApplication.processEvents()


def generateRequestWindow(newRequestModels,newRequestGenerating):
    openNewWindow(newRequestModels,newRequestGenerating)
    QCoreApplication.processEvents()
    generateRequest()
    # threading.Thread(target=lambda: generateRequest(), args=()).start()
    # t.start()
    # t.join()

    # newRequestGenerating.progressBar.setValue(100)
    # openNewWindow(newRequestGenerating,newRequestDone)
    # newRequestDone.InFileLabel.setText("em: " + str(filename))

#   ============================================
#   Statistics
#   ============================================


def firstOpenStatistics(mainUI,statisticsChoose):
    global items

    statisticsChoose.ItemComboBox.clear()

    descs = []
    for item in items:
        descs += [item.Description]

    statisticsChoose.ItemComboBox.addItems(descs)

    openNewWindow(mainUI,statisticsChoose)

def generateStatistics(statisticsChoose,statisticsUi):
    global items, mainUI, statisticsLayout
    
    # get description and id
    desc = statisticsChoose.ItemComboBox.currentText()
    id = -1
    itemChoosen = None
    for item in items:
        if item.Description == desc:
            id = item.ID
            itemChoosen = item
            break
    if id == -1:
        openNewWindow(statisticsChoose,mainUI)
        return

    # get document type
    typeDoc = FATURA
    typeDocCB = statisticsChoose.DocTypeComboBox.currentText()
    if typeDocCB == "Fatura":
        typeDoc = FATURA
    if typeDocCB == "Fatura Proforma":
        typeDoc = FATURA_PROFORMA
    if typeDocCB == "Nota de Encomenda":
        typeDoc = NOTA_DE_ENCOMENDA
    
    # set label

    statisticsUi.ChooseAProductLabel.setText("Estatísticas do Produto: " + str(id) + " | " + desc.lower().replace("*",'').replace('  ',' ')+ " (" + typeDocCB + ")")
    
    # clear current children 
    for child in statisticsUi.BodyBodyFrame.children():
        try:
            print(type(child))
            child.hide()
        except:
            print("couldnt: ",type(child))
            pass
    
    # create layout
    
    if statisticsLayout != None:
        
        if statisticsLayout is not None:
            while statisticsLayout.count():
                widgetItem = statisticsLayout.takeAt(0)
                widget = widgetItem.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    statisticsUi.BodyBodyFrame.deleteLayout(widgetItem.layout())
            sip.delete(statisticsLayout)

    statisticsLayout = QVBoxLayout()
    statisticsLayout.setObjectName("statisticsLayout")

    statisticsLayout.setContentsMargins(24, 0, 24, 0)
    statisticsLayout.setSpacing(-1)


    item = itemChoosen

    # Sales per year

    df = item.itemHistory.dfs[typeDoc]
    if (len(df) == 0):
        statisticsUi.ChooseAProductLabel.setText("Sem dados para: " + str(id) + " " + desc.lower().replace("*",'').replace('  ',' ')+ " (" + typeDocCB + ")")
        openNewWindow(statisticsChoose,statisticsUi)
        return

    s2020 = df.loc[(df['date']>='2020-01-01') & (df['date']<'2021-01-01')]['sale'].sum()
    s2021 = df.loc[(df['date']>='2021-01-01') & (df['date']<'2022-01-01')]['sale'].sum()
    s2022 = df.loc[(df['date']>='2022-01-01') & (df['date']<'2023-01-01')]['sale'].sum()
    c = Canvas(statisticsUi.BodyBodyFrame)
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]
    c.bar(['2020','2021','2022'],[s2020,s2021,s2022],color=color,width=0.4,xlabel="Ano",ylabel="Qtds. vendidas",title="Qtd. vendida por ano",grid=True)    
    statisticsLayout.addWidget(c)


    # Sales per month in 2020

    df2020 = df.loc[(df['date']>='2020-01-01') & (df['date']<'2021-01-01')]
    dans = df2020.groupby(df2020['date'].dt.month)['sale'].sum()

    dans = dans.reset_index()
    for i in range(1,13):
        if i not in list(dans['date']):
            dans = pd.concat([dans, pd.DataFrame.from_records([{ 'date': i, 'sale': 0 }])])

    dans = dans.sort_values(by=['date'])

    months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    mymodel = np.poly1d(np.polyfit(dans['date'], dans['sale'], 3))
    monthsLine = np.linspace(1, 12, 100)

    c = Canvas(statisticsUi.BodyBodyFrame)
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]
    c.bar(months,dans['sale'],color = color)    
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]
    c.plot(np.linspace(0, 11, 100), mymodel(monthsLine),color=color,xlabel='Mês',ylabel="Qtds. vendidas",title="Qtd. vendida por mês de 2020",grid=True)
    statisticsLayout.addWidget(c)

    # Sales per month in 2021

    df2021 = df.loc[(df['date']>='2021-01-01') & (df['date']<'2022-01-01')]
    dans = df2021.groupby(df2021['date'].dt.month)['sale'].sum()

    dans = dans.reset_index()
    for i in range(1,13):
        if i not in list(dans['date']):
            dans = pd.concat([dans, pd.DataFrame.from_records([{ 'date': i, 'sale': 0 }])])

    dans = dans.sort_values(by=['date'])

    months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    mymodel = np.poly1d(np.polyfit(dans['date'], dans['sale'], 3))
    monthsLine = np.linspace(1, 12, 100)

    c = Canvas(statisticsUi.BodyBodyFrame)
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]
    c.bar(months,dans['sale'],color=color,xlabel='Mês',ylabel="Qtds. vendidas",title="Qtd. vendida por mês de 2021")
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]
    c.plot(np.linspace(0, 11, 100), mymodel(monthsLine),color=color,xlabel='Mês',ylabel="Qtds. vendidas",title="Qtd. vendida por mês de 2021",grid=True)
    statisticsLayout.addWidget(c)

    # Sales per month in 2022

    df2022 = df.loc[(df['date']>='2022-01-01') & (df['date']<'2023-01-01')]
    dans = df2022.groupby(df2022['date'].dt.month)['sale'].sum()

    dans = dans.reset_index()
    for i in range(1,13):
        if i not in list(dans['date']):
            dans = pd.concat([dans, pd.DataFrame.from_records([{ 'date': i, 'sale': 0 }])])

    dans = dans.sort_values(by=['date'])

    months = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
    mymodel = np.poly1d(np.polyfit(dans['date'], dans['sale'], 3))
    monthsLine = np.linspace(1, 12, 100)

    c = Canvas(statisticsUi.BodyBodyFrame)
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]
    c.bar(months,dans['sale'],color=color,xlabel='Mês',ylabel="Qtds. vendidas",title="Qtd. vendida por mês de 2022")   
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0] 
    c.plot(np.linspace(0, 11, 100), mymodel(monthsLine),color=color,xlabel='Mês',ylabel="Qtds. vendidas",title="Qtd. vendida por mês de 2022",grid=True)
    statisticsLayout.addWidget(c)

    # Sales per day

    dans = df.groupby(df['date'].dt.day)['sale'].sum()
    dans = dans.reset_index()

    for i in range(1,31):
        if i not in list(dans['date']):
            dans = pd.concat([dans, pd.DataFrame.from_records([{ 'date': i, 'sale': 0 }])])


    dans = dans.sort_values(by=['date'])

    mymodel = np.poly1d(np.polyfit(dans['date'], dans['sale'], 3))
    myline = np.linspace(1, 31, 100)

    c = Canvas(statisticsUi.BodyBodyFrame)
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]
    c.bar(dans['date'],dans['sale'],color=color,xlabel='Dia',ylabel="Qtds. vendidas",title="Qtd. vendida por dia do mês")  
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]  
    c.plot(myline, mymodel(myline),color=color,xlabel='Mês',ylabel="Qtds. vendidas",title="Qtd. vendida por dia do mês",grid=True)
    statisticsLayout.addWidget(c)

    # Sales per weekday

    dans = df.groupby(df['date'].dt.weekday)['sale'].sum()

    dans = dans.reset_index()

    for i in range(0,7):
        if i not in list(dans['date']):
            dans = pd.concat([dans, pd.DataFrame.from_records([{ 'date': i, 'sale': 0 }])])


    dans = dans.sort_values(by=['date'])

    days = ['Seg','Ter','Qua','Qui','Sex','Sab','Dom']

    mymodel = np.poly1d(np.polyfit(dans['date'], dans['sale'], 3))
    myline = np.linspace(0, 6, 100)
    c = Canvas(statisticsUi.BodyBodyFrame)
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0]
    c.bar(days,dans['sale'],color=color,xlabel='Dia da semana',ylabel="Qtds. vendidas",title="Qtd. vendida por dia da semana")   
    color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])][0] 
    c.plot(myline, mymodel(myline),color=color,xlabel='Mês',ylabel="Qtds. vendidas",title="Qtd. vendida por dia da semana",grid=True)
    statisticsLayout.addWidget(c)



    try:
        statisticsUi.BodyBodyFrame.setLayout(statisticsLayout)
    except:
        pass

    openNewWindow(statisticsChoose,statisticsUi)

# init
width = 858
height = 681
app = QApplication(sys.argv)
BROWSER_DIR = './'
items = api.getItemsList()
filename = ""
itemsInTransaction = {}
statisticsLayout = None

# ui
mainUI = UI("mainWindow.ui")
newRequestPackingList = UI("novoPedidoPackingList.ui")
newRequestPackingListItems = UI("novoPedidoPackingListItems.ui")
newRequestItems = UI("novoPedidoItems.ui")
newRequestModels = UI("novoPedidoModels.ui")
newRequestGenerating = UI("novoPedidoGenerating.ui")
newRequestDone = UI("novoPedidoDone.ui")
searchInactives = UI("searchInactives.ui")
configuration = UI("Configuration.ui")
statisticsChoose = UI("StatisticsChoose.ui")
statisticsUi = UI("Statistics.ui")

# main buttons
mainUI.NewRequestButton.clicked.connect(lambda: openNewWindow(mainUI,newRequestPackingList))
mainUI.SearchInactiveButton.clicked.connect(lambda: openNewWindow(mainUI,searchInactives))
mainUI.ConfigurationButton.clicked.connect(lambda: openNewWindow(mainUI,configuration))
mainUI.EstatisticsButton.clicked.connect(lambda: firstOpenStatistics(mainUI,statisticsChoose))


# newRequestPackingList
newRequestPackingList.HomeButton.clicked.connect(lambda: openNewWindow(newRequestPackingList,mainUI))
newRequestPackingList.GoBackButton.clicked.connect(lambda: openNewWindow(newRequestPackingList,mainUI))
newRequestPackingList.BrowseButton.clicked.connect(lambda: packingListBrowseFile(newRequestPackingList))
newRequestPackingList.AdvanceButton.clicked.connect(lambda: openPackingListItems(newRequestPackingList,newRequestPackingListItems))


# newRequestPackingListItems
newRequestPackingListItems.HomeButton.clicked.connect(lambda: openNewWindow(newRequestPackingListItems,mainUI))
newRequestPackingListItems.GoBackButton.clicked.connect(lambda: openNewWindow(newRequestPackingListItems,newRequestPackingList))
newRequestPackingListItems.AdvanceButton.clicked.connect(lambda: openNewWindow(newRequestPackingListItems,newRequestItems))


# newRequestItems
# threading.Thread(target=lambda: setupNewRequestItems(newRequestItems), args=()).start()
setupNewRequestItems(newRequestItems)
newRequestItems.HomeButton.clicked.connect(lambda: openNewWindow(newRequestItems,mainUI))
newRequestItems.GoBackButton.clicked.connect(lambda: openNewWindow(newRequestItems,newRequestPackingListItems))
newRequestItems.AdvanceButton.clicked.connect(lambda: openNewWindow(newRequestItems,newRequestModels))

# newRequestModels

newRequestModels.HomeButton.clicked.connect(lambda: openNewWindow(newRequestModels,mainUI))
newRequestModels.GoBackButton.clicked.connect(lambda: openNewWindow(newRequestModels,newRequestItems))
newRequestModels.GenerateButton.clicked.connect(lambda: generateRequestWindow(newRequestModels,newRequestGenerating))

# newRequestGenerating
newRequestGenerating.CancelButton.clicked.connect(lambda: openNewWindow(newRequestGenerating,mainUI))


# newRequestDone
newRequestDone.MenuButton.clicked.connect(lambda: openNewWindow(newRequestDone,mainUI))
newRequestDone.ConfirmButton.clicked.connect(lambda: openNewWindow(newRequestDone,mainUI))

# searchInactives
setupSearchInactives(searchInactives)
searchInactives.HomeButton.clicked.connect(lambda: openNewWindow(searchInactives,mainUI))

# configuration
setupConfiguration(configuration)
configuration.PedidoBaseHomeButton.clicked.connect(lambda: openNewWindow(configuration,mainUI))
configuration.PedidoBaseSaveButton.clicked.connect(lambda: configurationPedidoBaseSave(configuration))
configuration.PedidoBaseAddRowButton.clicked.connect(lambda: configurationPedidoBaseAddRow(configuration))

configuration.PedidoFinalHomeButton.clicked.connect(lambda: openNewWindow(configuration,mainUI))
configuration.PedidoFinalSaveButton.clicked.connect(lambda: configurationPedidoFinalSave(configuration))
configuration.PedidoFinalAddRowButton.clicked.connect(lambda: configurationPedidoFinalAddRow(configuration))

# Statistics

statisticsChoose.HomeButton.clicked.connect(lambda: openNewWindow(statisticsChoose,mainUI))
statisticsChoose.GenerateButton.clicked.connect(lambda: generateStatistics(statisticsChoose,statisticsUi))

statisticsUi.HomeButton.clicked.connect(lambda: openNewWindow(statisticsUi,mainUI))



# start
mainUI.showWindow(width,height)

app.exec_()
# parallel

# setupNewRequestItems(newRequestItems)
# print('a')