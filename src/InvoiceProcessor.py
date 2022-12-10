import pandas as pd
import math
from JaccardDistance import *

DESCRIPTION_STR = 'DESCRIÇÃO DO PRODUTO'
QUANTITY_STR = "QUANTIDADE TOTAL EM UNIDADES"
QUANTITYBYBOX_STR = 'QUANTIDADE EM UNIDADES POR CAIXA / FARDO'
ITEMID_STR =  "ARMAZÉM ATLÂNTICO - CÓDIGO REFERÊNCIA"


class InvoiceProcessor:


    def __init__(self,filename):
        df = pd.read_excel(filename)
        lst = df.values.tolist()

        # get start row (first after line with column TITLES)
        for i in range(len(lst)):
            if DESCRIPTION_STR in lst[i]:
                self.startRow = i+1
                for j in range(len(lst[i])):
                    if (lst[i][j] == QUANTITY_STR):
                        self.qtyCol = j
                    if (lst[i][j] == DESCRIPTION_STR):
                        self.descCol = j
                    if (lst[i][j] == ITEMID_STR):
                        self.itemIDCol = j

        self.descs = []
        self.qtys = []
        self.ids = []
        for i in range(self.startRow,len(lst)):
            if(type(lst[i][self.descCol]) != str and math.isnan(lst[i][self.descCol])):
                break
            self.descs += [lst[i][self.descCol]]
            self.qtys += [lst[i][self.qtyCol]]
            self.ids += [lst[i][self.itemIDCol]]
    
    def getLists(self):
        return self.ids, self.descs, self.qtys

    def findMatches(self,items):
        bestDists = []
        bestPair = []

        allDescs = ['']*len(items)
        i = 0
        for item in items:
            allDescs[i] = item.Description

            i = i + 1

        for desc in self.descs:
            dists = JaccardDistance.distance(desc,allDescs)
            max_dist_idx = 0
            best_dist = 0
            for i in range(len(dists)):
                if dists[i] > best_dist:
                    best_dist = dists[i]
                    max_dist_idx = i
            bestDists += [best_dist]
            bestPair += [max_dist_idx]
        
        i = 0
        for desc in self.descs:
            print(desc,"\t\t\t\t",items[bestPair[i]].Description,"\t\t\t",bestDists[i])
            i = i + 1

    @staticmethod
    def returnMatchesDescsWithId(items,itemDescMap):

        allDescs = ['']*len(items)
        allIds = []
        i = 0
        for item in items:
            allDescs[i] = item.Description
            allIds += [item.ID]
            i = i + 1
        
        itemKeyMap = {}
        for item in items:
            itemKeyMap[item.ID] = item
        
        # get db description and match value
        db_description = []
        for (itemID, desc) in itemDescMap:
            db_description += [(itemKeyMap[itemID].Description,JaccardDistance.distance(desc,itemKeyMap[itemID].Description))]
        
        # find best item match for each
        best = []
        for (itemID, desc) in itemDescMap:
            dists = JaccardDistance.distance(desc,allDescs)
            
            max_dist_idx = 0
            best_dist = 0
            for i in range(len(dists)):
                if dists[i] > best_dist:
                    best_dist = dists[i]
                    max_dist_idx = i
            bestItemId = allIds[max_dist_idx]
            bestDescription = allDescs[max_dist_idx]
            best += [(bestItemId,bestDescription,best_dist)]
        
        return db_description,best


        
