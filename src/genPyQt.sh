#!/bin/bash

PATH=$PATH:/Users/matheusfranco/.asdf/installs/python/3.10.0/bin

# python3 -m PyQt5.uic.pyuic mainWindow.ui -o mainWindow.py -x
# python3 -m PyQt5.uic.pyuic novoPedidoDone.ui -o novoPedidoDone.py -x
# python3 -m PyQt5.uic.pyuic novoPedidoGenerating.ui -o novoPedidoGenerating.py -x
# python3 -m PyQt5.uic.pyuic novoPedidoItems.ui -o novoPedidoItems.py -x
# python3 -m PyQt5.uic.pyuic novoPedidoModels.ui -o novoPedidoModels.py -x
# python3 -m PyQt5.uic.pyuic novoPedidoPackingList.ui -o novoPedidoPackingList.py -x

pyrcc5 -o resources_rc.py resources.qrc
