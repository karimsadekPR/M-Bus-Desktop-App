
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton
)

from PyQt5.QtCore import Qt
from style.btnStyle import btnStyle

from tools.deleteReadings import delete_selected_rows

def create_table() -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Select", "Meter ID", "Timestamp", "Value"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        table.setColumnWidth(1, 100)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        return table

def setup_home_tab(self):
        layout = QVBoxLayout()
        self.home_tab.setLayout(layout)

        self.home_title = QLabel("Water Meter Readings")
        self.home_title.setObjectName("home_title")
        self.home_title.setAlignment(Qt.AlignCenter)
        self.home_title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px; padding: 10px;")
        layout.addWidget(self.home_title)

        self.home_table = create_table()
        layout.addWidget(self.home_table)

def setup_right_panel_for_Home(self):
        self.right_layout.addStretch()
        self.btn_load = QPushButton("Load All Readings")
        self.btn_load.setObjectName("btn_load")
        self.btn_load.setStyleSheet(btnStyle)
        self.btn_load.clicked.connect(self.update_table)
        self.right_layout.addWidget(self.btn_load)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.setStyleSheet(btnStyle)
        self.btn_delete.clicked.connect(lambda: delete_selected_rows(self))
        self.right_layout.addWidget(self.btn_delete)
