from openpyxl import load_workbook

class ConfigEditor:

    @staticmethod
    def update(lst):

        # load workbooks and sheets
        workbook = load_workbook(filename=".data/ItemBoxDetail.xlsx")

        sheet = workbook['ItemBoxDetail']

        # map item id to its rows (also save the last row)
        map = {}

        row = 2
        while(sheet["A"+str(row)].value != None):
            map[sheet["A"+str(row)].value] = row
            row += 1
        LastRow = row-1

        
        for elm in lst:
            if elm[0] in map:
                row = map[elm[0]]
                rowStr = str(row)
            else:
                LastRow += 1
                rowStr = str(LastRow)

            sheet['A'+rowStr] = elm[0]
            sheet['B'+rowStr] = elm[1]
            sheet['C'+rowStr] = elm[2]
            sheet['D'+rowStr] = elm[3]
            sheet['E'+rowStr] = elm[4]
            sheet['F'+rowStr] = elm[5]
            sheet['G'+rowStr] = elm[6]
            sheet['H'+rowStr] = elm[7]
            sheet['I'+rowStr] = elm[8]
            sheet['J'+rowStr] = elm[9]
            sheet['K'+rowStr] = elm[10]
            sheet['L'+rowStr] = elm[11]
            sheet['M'+rowStr] = elm[12]
            sheet['N'+rowStr] = elm[13]
            sheet['O'+rowStr] = elm[14]
            sheet['P'+rowStr] = elm[15]
            sheet['Q'+rowStr] = elm[16]
            sheet['R'+rowStr] = elm[17]
        
        workbook.save(filename=".data/ItemBoxDetail.xlsx")
