import sys
from PySide.QtGui import *

import pyrock


app = QApplication(sys.argv)

tree_view = QTreeView()
tree_view.setWindowTitle('PyRock TaskInspector')
tree_view.setMinimumSize(600, 400)
model = QStandardItemModel(tree_view)
tree_view.setModel(model)

model.setHorizontalHeaderLabels(('Name', 'Type'))
tree_view.setUniformRowHeights(True)

tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
icon_in = QIcon.fromTheme('go-next')
icon_out = QIcon.fromTheme('go-previous')

proxies = map(pyrock.TaskProxy, pyrock.nameservice.names())
for proxy in proxies:
    task_item = QStandardItem(proxy.name)
    for name, type_name in proxy.output_ports.iteritems():
        print name, type_name
        item_name = QStandardItem(name)
        item_name.setIcon(icon_out)
        item_type = QStandardItem(type_name)
        task_item.appendRow((item_name, item_type))
    for name, type_name in proxy.input_ports.iteritems():
        print name, type_name
        item_name = QStandardItem(name)
        item_name.setIcon(icon_in)
        item_type = QStandardItem(type_name)
        task_item.appendRow((item_name, item_type))

    if proxy.is_connected():
        if proxy.is_running():
            status_item = QStandardItem('running')
        elif proxy.is_configured():
            status_item = QStandardItem('stopped')
        else:
            status_item = QStandardItem('pre-configured')
    else:
        status_item = QStandardItem('not connected')
        task_item.setEnabled(False)
        status_item.setEnabled(False)
    model.appendRow((task_item, status_item))
#index = model.indexFromItem(task_item)
#tree_view.expandAll()
#tree_view.setCurrentIndex(index)
tree_view.show()

#table.verticalHeader().hide()

tree_view.header().setResizeMode(QHeaderView.ResizeToContents)
# enable sorting
#table.setSortingEnabled(True)


# Enter Qt application main loop
app.exec_()
sys.exit()
