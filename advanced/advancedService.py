
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton
)
from PyQt5.QtCore import Qt, QDate
from style.btnStyle import btnStyle
from tools.exportCSV import export_table_to_csv
from tools.deleteReadings import delete_selected_rows

def setup_advanced_tab(self):
        layout = QVBoxLayout()
        self.advanced_tab.setLayout(layout)

        self.advanced_title = QLabel("Advanced Water Meter Readings")
        self.advanced_title.setObjectName("advanced_title")
        self.advanced_title.setAlignment(Qt.AlignCenter)
        self.advanced_title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px; padding: 10px;")
        layout.addWidget(self.advanced_title)

        self.advanced_table = create_table()
        layout.addWidget(self.advanced_table)


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


def setup_right_panel_for_Advanced(self):
        self.right_layout.addStretch()
        self.btn_load = QPushButton("Load All Readings")
        self.btn_load.setObjectName("btn_load")
        self.btn_load.setStyleSheet(btnStyle)
        self.btn_load.clicked.connect(self.update_table)
        self.right_layout.addWidget(self.btn_load)

        self.btn_read = QPushButton("Read New Meter")
        self.btn_read.setObjectName("btn_read")
        self.btn_read.setStyleSheet(btnStyle)
        self.btn_read.clicked.connect(self.read_new_meter)
        self.right_layout.addWidget(self.btn_read)

        self.btn_read_all = QPushButton("Read All Meters")
        self.btn_read_all.setObjectName("btn_read_all")
        self.btn_read_all.setStyleSheet(btnStyle)
        self.btn_read_all.clicked.connect(self.read_all_meters)
        self.right_layout.addWidget(self.btn_read_all)

        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.setObjectName("btn_export")
        self.export_btn.setStyleSheet(btnStyle)
        self.export_btn.clicked.connect(lambda: export_table_to_csv(self))
        self.right_layout.addWidget(self.export_btn)

        self.usage_chart_btn = QPushButton("Show Usage Chart")
        self.usage_chart_btn.setStyleSheet(btnStyle)
        self.usage_chart_btn.clicked.connect(self.show_usage_chart)
        self.right_layout.addWidget(self.usage_chart_btn)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.setStyleSheet(btnStyle)
        self.btn_delete.clicked.connect(lambda: delete_selected_rows(self))
        self.right_layout.addWidget(self.btn_delete)

        self.sort_box = QComboBox()
        self.sort_box.addItems(["Meter ID", "Timestamp", "Value"])
        self.sort_box.setObjectName("sort_box")
        self.right_layout.addWidget(self.sort_box)

        self.sort_button = QPushButton("Sort")
        self.sort_button.setObjectName("sort_button")
        self.sort_button.clicked.connect(self.sort_table)
        self.right_layout.addWidget(self.sort_button)

        self.right_layout.addSpacing(10)
        self.right_layout.addWidget(QLabel("Date From:"))

        date_layout = QHBoxLayout()
        self.date_from = QDateEdit(QDate.currentDate())
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")

        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")

        date_layout.addWidget(self.date_from)
        date_layout.addWidget(self.date_to)
        self.right_layout.addLayout(date_layout)

        self.checkbox = QCheckBox("Date Selected \ Tarih")
        self.right_layout.addWidget(self.checkbox)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["Meter ID", "Timestamp", "Value"])
        self.filter_box.setObjectName("sort_box")
        self.right_layout.addWidget(self.filter_box)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filter value...") #to be changed
        self.right_layout.addWidget(self.filter_input)

        self.filter_button = QPushButton("Filter")
        self.filter_button.setObjectName("filter_button")
        self.filter_button.setStyleSheet(btnStyle)
        self.filter_button.clicked.connect(self.apply_all_filters)
        self.right_layout.addWidget(self.filter_button)
