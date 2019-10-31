from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QBrush, QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView


class TreeItem(QTreeWidgetItem):
    def __init__(self, value):
        super().__init__(['', ''])
        self.value = value
        self.setForeground(1, QBrush(QColor('red')))

    @property
    def value(self):
        return [self.text(0), *self.data(0, Qt.UserRole)]

    @value.setter
    def value(self, value):
        text, *value = value
        self.setText(0, text)
        self.setData(0, Qt.UserRole, value)

class Tree(QTreeWidget):
    addAccount = pyqtSignal()
    editAccount = pyqtSignal(TreeItem)
    removeAccount = pyqtSignal(TreeItem)
    reloadAccount = pyqtSignal(TreeItem)

    def __init__(self, menu):
        super().__init__()
        self.setMinimumSize(QSize(100, 200))
        self.setColumnCount(2)
        self.header().setMinimumSectionSize(0)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.setHeaderHidden(True)
        menu.relatesTo(self)
        self._menu = menu
        for action in menu.actions():
            try:
                action.triggered.connect(getattr(self, f'on{action.__class__.__name__}Triggered'))
            except AttributeError:
                pass
        self.itemActivated.connect(self.onItemActivated)
        self.itemChanged.connect(self.onItemChanged)

    def sizeHint(self):
        return QSize(150, 300)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self._menu.popup(event.globalPos())

    def onAddAccountTriggered(self, event):
        self.addAccount.emit()

    def onEditAccountTriggered(self, event):
        self.editAccount.emit(self.currentItem())

    def onRemoveAccountTriggered(self, event):
        self.removeAccount.emit(self.currentItem())

    def onReloadAccountTriggered(self, event):
        item = self.currentItem()
        self.reloadAccount.emit(item.parent() or item)

    def onItemActivated(self, item):
        if item.parent() is None:
            self.editAccount.emit(item)

    def onItemChanged(self, item):
        self.sortItems(0, Qt.AscendingOrder)
        if item.parent() is None:
            self.reloadAccount.emit(item)

    def addTopLevelItem(self, item):
        super().addTopLevelItem(item)
        self.onItemChanged(item)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        key = event.key()
        item = self.currentItem()
        if key == Qt.Key_Insert:
            self.addAccount.emit()
        elif item is not None:
            if key == Qt.Key_Delete:
                if item.parent() is None:
                    self.removeAccount.emit(item)
            elif key == Qt.Key_F5:
                self.reloadAccount.emit(item.parent() or item)
