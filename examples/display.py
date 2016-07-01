import sys

from PySide.QtGui import *
from PySide.QtCore import QThread

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

from time import sleep

import pyrock


class TaskModel(QtCore.QAbstractItemModel):

    HEADERS = ('Name', 'Value')
    ICON_IN  = QIcon.fromTheme('go-next')
    ICON_OUT = QIcon.fromTheme('go-previous')
    ICON_START  = QIcon.fromTheme('media-playback-start')
    ICON_STOP = QIcon.fromTheme('process-stop')
    ICON_CONFIGURE = QIcon.fromTheme('preferences-system')
    ICON_CLEANUP = QIcon.fromTheme('view-refresh')

    def __init__(self, tasks):
        QtCore.QAbstractItemModel.__init__(self)
        self.tasks = tasks

    def columnCount(self, parent):
        return 2

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.tasks)
        node = parent.internalPointer()
        if isinstance(node, pyrock.TaskProxy):
            return len(node.ports)
        return 0

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            if isinstance(node, pyrock.TaskProxy):
                if index.column() == 0:
                    return node.name
                if index.column() == 1:
                    return str(node.state())
            
            if isinstance(node, pyrock.Port):
                if index.column() == 0:
                    return node.name
                if index.column() == 1:
                    return node.type_name

        if role == QtCore.Qt.DecorationRole and isinstance(node, pyrock.Port) and index.column() == 0:
            if node.port_type == pyrock.Port.COutput:
                return self.ICON_OUT
            else:
                return self.ICON_IN
            
    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole):
            return self.HEADERS[column]

    def index(self, row, column, parent=None):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, self.tasks[row])

        task = parent.internalPointer()
        return self.createIndex(row, column, task.ports[row])

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        node = index.internalPointer()
        if isinstance(node, pyrock.Port):
            return self.createIndex(self.tasks.index(node.task), 0, node.task)
        else:
            return QtCore.QModelIndex()


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(FilterProxyModel, self).__init__()

    def filterAcceptsColumn(self, column, parent):
        return True
    
    def filterAcceptsRow(self, row, parent):
        idx = self.sourceModel().index(row, 0, parent)
        if idx.isValid() and not idx.parent().isValid(): # check for top level entry aka Task
            task = idx.internalPointer()
            if '_Logger' in task.name:
                return False
        return True

    def lessThan(self, left, right):
        return self.sourceModel().data(left, QtCore.Qt.DisplayRole) < self.sourceModel().data(right, QtCore.Qt.DisplayRole)


class TaskTreeView(QtGui.QTreeView):

    REFRESH_TIMEOUT = 100
    ICON_IN  = QIcon.fromTheme('go-next')
    ICON_OUT = QIcon.fromTheme('go-previous')
    ICON_START  = QIcon.fromTheme('media-playback-start')
    ICON_STOP = QIcon.fromTheme('process-stop')
    ICON_CONFIGURE = QIcon.fromTheme('preferences-system')
    ICON_CLEANUP = QIcon.fromTheme('view-refresh')

    def __init__(self, parent=None):
        super(TaskTreeView, self).__init__(parent)

        # menu = QtGui.QMenu("menu", self)
        # menu.addAction(QtGui.QAction('50%', menu, checkable=True))
        # self.parent.menuBar().addMenu(menu)


        self.setWindowTitle('PyRock TaskInspector')
        self.setMinimumSize(600, 400)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        # self.header().setStretchLastSection(False)
        # self.header().setResizeMode(1, QHeaderView.Interactive)
        # self.header().setResizeMode(QHeaderView.ResizeToContents)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)
        self.setAlternatingRowColors(True)

        self.tasks = map(pyrock.TaskProxy, pyrock.nameservice.names())
        self.model = TaskModel(self.tasks)

        self.proxy_model = FilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        self.setModel(self.proxy_model)

        self.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.setSortingEnabled(True)

        # setup refresh timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(TaskTreeView.REFRESH_TIMEOUT)


    def open_menu(self, point):
        index = self.indexAt(point)
        if index.isValid() and not index.parent().isValid(): # check for top level rows
            index = self.proxy_model.mapToSource(index)
            menu = QMenu()
            proxy = index.internalPointer()
            if proxy.is_configured():
                if proxy.is_running():
                    action = menu.addAction(TaskTreeView.ICON_STOP, 'stop', proxy.stop).setIconVisibleInMenu(True)
                    #action.setEnabled(False)
                else:
                    item = menu.addAction(TaskTreeView.ICON_START, 'start', proxy.start).setIconVisibleInMenu(True)
                    menu.addAction(TaskTreeView.ICON_CLEANUP, 'cleanup', proxy.cleanup).setIconVisibleInMenu(True)
            else:
                menu.addAction(TaskTreeView.ICON_CONFIGURE, 'configure', proxy.configure).setIconVisibleInMenu(True)

            menu.exec_(self.viewport().mapToGlobal(point))        


    def refresh(self):
        task_names = set(pyrock.nameservice.names())
        proxy_names = set([p.name for p in self.model.tasks])

        if len(task_names) == len(proxy_names) == len(task_names & proxy_names):
            return
   
        # delete tasks
        for task_name in proxy_names - task_names:
            idx = [p.name for p in self.model.tasks].index(task_name)
            self.model.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
            del self.model.tasks[idx]
            self.model.endRemoveRows()

        # add tasks
        for task_name in task_names - proxy_names:
            proxy = pyrock.TaskProxy(task_name)
            idx = len(self.model.tasks)
            self.model.beginInsertRows(QtCore.QModelIndex(), idx, idx)
            self.model.tasks.append(proxy)
            self.model.endInsertRows()


class PyRockDisplay(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.treeview = TaskTreeView()
        self.setCentralWidget(self.treeview)

        # self.menu = QtGui.QMenu('View', self)
        # self.menu.addAction(QtGui.QAction('filter Loggers', self.menu, checkable=True))
        # self.menuBar().addMenu(self.menu)

        self.toolbar = QtGui.QToolBar('', self)
        self.toolbar.setMovable(False)

        self.filter_action = QtGui.QAction('Loggers', self.toolbar, checkable=True, checked=True)
        # self.filter_action.triggered.connect(self.foo)

        self.lineedit = QtGui.QLineEdit('', self.toolbar, placeholderText='filter...')

        self.toolbar.addWidget(self.lineedit)
        self.toolbar.addAction(self.filter_action)


        # self.check = QtGui.QCheckBox('filter &loggers', self.toolbar)
        # self.toolbar.addWidget(self.check)

        self.addToolBar(self.toolbar)

        self.connect(QtGui.QShortcut(QtGui.QKeySequence('Ctrl+F'), self), QtCore.SIGNAL('activated()'), self.activate_lineedit)
#        self.connect(QtGui.QShortcut(QtGui.QKeySequence('Ctrl+C'), self), QtCore.SIGNAL('activated()'), self.close)


    def activate_lineedit(self):
        self.lineedit.selectAll()
        self.lineedit.setFocus()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    window = PyRockDisplay()
    window.show()

    # treeview = TaskTreeView()
    # treeview.show()

    sys.exit(app.exec_())
