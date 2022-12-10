import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget


class Canvas(FigureCanvas):
    def __init__(self,parent):
        fig,self.ax = plt.subplots(figsize=(500,400))#dpi=200)
        super().__init__(fig)
        self.setParent(parent)
    
    def plot(self,x,y,xlabel='',ylabel='',title='',grid=False,color='blue'):
        self.ax.plot(x,y,color=color)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_title(title)
        if grid:
            self.ax.grid()
    
    def bar(self,x,y,xlabel='',ylabel='',title='',grid=False,color='blue',width=0.4):
        self.ax.bar(x,y,color=color,width=width)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_title(title)
        if grid:
            self.ax.grid()

    