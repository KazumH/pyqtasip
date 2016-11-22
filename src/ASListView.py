import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

FOODS = [
    'Cookie dough',  # Must be store-bought
    'Hummus',  # Must be homemade
    'Spaghetti',  # Must be saucy
    'Dal makhani',  # Must be spicy
    'Chocolate whipped cream'  # Must be plentiful
]

COLOR_LIST = [
    QBrush(QColor(255, 255, 255)),
    QBrush(QColor(240, 240, 240))
]



def addItemInRow(model, datas):
    for data in datas:
        # Create an item with a caption
        item = QStandardItem(data)
        # Add a checkbox to it
        item.setCheckable(True)
        item.setCheckState(True)
        # Add the item to the model
        model.appendRow(item)

def on_item_changed(self, item):
    # If the changed item is not checked, don't bother checking others
    if not item.checkState():
        return

    # Loop through the items until you get None, which
    # means you've passed the end of the list
    i = 0
    while self.model.item(i):
        if not self.model.item(i).checkState():
            return
        i += 1


class ASListView(QListView):
    def __init__(self, parent=None):
        super(ASListView, self).__init__(parent)
        self.setMinimumSize(512, 512)
        self.addItemInRow()
        self.model.itemChanged.connect(self.on_item_changed)

    def addItemInRow(self):
        for food in FOODS:
            # Create an item with a caption
            item = QStandardItem(food)

            # Add a checkbox to it
            item.setCheckable(True)
            item.setCheckState(True)

            # Add the item to the model
            self.model.appendRow(item)
    def on_item_changed(self, item):
        # If the changed item is not checked, don't bother checking others
        if not item.checkState():
            return

        # Loop through the items until you get None, which
        # means you've passed the end of the list
        i = 0
        while self.model.item(i):
            if not self.model.item(i).checkState():
                return
            i += 1




