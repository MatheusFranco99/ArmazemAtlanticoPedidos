import ItemGenerator
# ig = ItemGenerator.ItemGenerator()
# ig.generate()

import Sale

# typeDoc = Sale.FATURA

import PedidoBaseCreator

# pdc = PedidoBaseCreator.PedidoBaseCreator()
# pdc.write(ig.getItemsList(),typeDoc)

item_generator = None

# import Sale

# typeDoc = Sale.FATURA

# import PedidoBaseCreator

# pdc = PedidoBaseCreator.PedidoBaseCreator()
# pdc.write(ig.getItemsList(),typeDoc)




def getItemsList():
    global item_generator
    if item_generator == None:
        item_generator = ItemGenerator.ItemGenerator()
        item_generator.update()
    return item_generator.getItemsList()


# def createNewRequest(typeDoc,M6M3 = True, FBP2020 = True, FBP2021 = True):
#     global item_generator
#     pdc = PedidoBaseCreator.PedidoBaseCreator()
#     pdc.write(item_generator.getItemsList(),typeDoc,M6M3)