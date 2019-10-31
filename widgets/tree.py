from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class TreeItem(QTreeWidgetItem):
    def __init__(self, value):
        super().__init__([''])
        self.value = value

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

    def __init__(self, menu):
        super().__init__()
        self.setMinimumSize(QSize(100, 200))
        self.setHeaderHidden(True)
        menu.relatesTo(self)
        self._menu = menu
        for action in menu.actions():
            try:
                action.triggered.connect(getattr(self, f'on{action.__class__.__name__}Triggered'))
            except AttributeError:
                pass
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

    def sizeHint(self):
        return QSize(150, 300)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self._menu.popup(event.globalPos())

    def onAddAccountTriggered(self, event):
        self.addAccount.emit()

    def onEditAccountTriggered(self, event):
        self.editAccount.emit(self.currentItem())

    def onRemoveAccountTriggered(self, event):
        self.deleteAccount.emit(self.currentItem())

    def onItemDoubleClicked(self, item):
        if item.parent() is None:
            self.editAccount.emit(item)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        key = event.key()
        item = self.currentItem()
        if key == Qt.Key_Insert:
            self.addAccount.emit()
        elif item is not None:
            if key == Qt.Key_Return:
                if item.parent() is None:
                    self.editAccount.emit(item)
            if key == Qt.Key_Delete:
                if item.parent() is None:
                    self.removeAccount.emit(item)
