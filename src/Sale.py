
FATURA = 0
FATURA_PROFORMA = 1
NOTA_DE_ENCOMENDA = 2
FATURA_STR = "Fatura"
FATURA_PROFORMA_STR = "Fatura Proforma"
NOTA_DE_ENCOMENDA_STR = "Nota de Encomenda"

class Sale:

    def __init__(self, itemID = None, quantity = None, closeDate = None, documentDescription = None):
        self.itemID = itemID
        self.quantity = quantity
        self.closeDate = closeDate
        self.documentDescription = documentDescription

        self.documentType = -1
        if self.documentDescription == FATURA_STR:
            self.documentType = FATURA
        elif self.documentDescription == FATURA_PROFORMA_STR:
            self.documentType = FATURA_PROFORMA
        elif self.documentDescription == NOTA_DE_ENCOMENDA_STR:
            self.documentType = NOTA_DE_ENCOMENDA
    

    def __str__(self):
        return '{\n' + f"\tItemID={self.itemID},\n\tQuantity = {self.quantity},\n\tCloseDate = {self.closeDate},\n\tDocument Description = {self.documentDescription},\n" + '}'
    
    def __repr__(self):
        return '{\n' + f"\tItemID={self.itemID},\n\tQuantity = {self.quantity},\n\tCloseDate = {self.closeDate},\n\tDocument Description = {self.documentDescription},\n" + '}'
    