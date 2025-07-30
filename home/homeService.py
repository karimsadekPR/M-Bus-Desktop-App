
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton
)


from PyQt5.QtCore import Qt


def create_table() -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Select", "Meter ID", "Timestamp", "Usage (m³)"])
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
