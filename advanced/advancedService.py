
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit, QInputDialog
)
from PyQt5.QtCore import Qt, QDate
from M_Bus_Services.M_bus_parser import parse_mbus_payload
from M_Bus_Services.mbusfunction import read_device_data
from database import get_all_meters, save_meter, save_reading, sync_mbus_to_db
from style.btnStyle import btnStyle
from tools.exportCSV import export_selected_to_csv, export_selected_to_excel, export_selected_to_txt
from tools.deleteReadings import delete_selected_rows
from settings.settingsService import translations


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


def create_table():
    table = QTableWidget()
    table.setColumnCount(12)
    table.setHorizontalHeaderLabels([
        "Select","Meter ID", "Manufacturer", "Address", "Version", "Date", "Time",
        "Meter Type", "Date No", "Value", "Unit", "Description", "Timestamp"
    ])
    
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)
    
    # Example: Fix width of "Meter ID" column
    header.setSectionResizeMode(0, QHeaderView.Fixed)
    table.setColumnWidth(0, 100)
    
    return table

def str_to_byte_list(hex_str):
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    # Convert each pair of characters to an integer (base 16)
    return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]

def get_meter_id(self):
    meter_id, ok = QInputDialog.getText(self, "Enter Meter ID", "Meter ID:")
    if ok and meter_id.strip():

        byte_list = str_to_byte_list(meter_id)
        format_ = read_device_data(serialId=byte_list)
        readings = parse_mbus_payload(format_)
        print(readings)
        Date = datetime.now().strftime("%Y-%m-%d")
        Time = datetime.now().strftime("%H:%M:%S")
        save_meter(meter_id= readings['ID'],manufacturer= readings['Manufacturer'],address= readings['Address'],version= readings['Version'],meter_type= readings['Meter Type'])
        for reading in readings['Data Records']:
            if reading['Unit'] != '-':
                save_reading(
                    meterId= readings["ID"],
                    manufacturer= readings["Manufacturer"],
                    address= readings["Address"],
                    version= readings["Version"],
                    date= Date,
                    time= Time,
                    meter_type= readings["Meter Type"],
                    value=reading['Value'],
                    unit=reading['Unit'],
                    description=reading['Description'],
                    date_no=None
                    )
            
        QMessageBox.information(self, "Meter ID Entered", f"You entered: {meter_id}")
        print(readings)
        self.display_new_readings([readings], Date, Time)
    elif ok:  # User pressed OK but left it blank
        QMessageBox.warning(self, "Invalid Input", "Please enter a valid Meter ID.")

def export_methods(self):
    formats = ["Excel (.xlsx)", "Text - Tab separated (.txt)", "CSV (.csv)"]
    format_choice, ok = QInputDialog.getItem(self, "Export Format", "Choose export format:", formats, 0, False)
    if not ok:
        return  # User canceled
    
    current_tab = self.tab_widget.currentWidget()
    if current_tab == self.home_tab:
        table = self.home_table
    elif current_tab == self.advanced_tab:
        table = self.advanced_table
    else:
        QMessageBox.warning(self, "Export Failed", "No exportable table in this tab.")
        return


    if format_choice == "Excel (.xlsx)":
        export_selected_to_excel(self, table=table)
    elif format_choice == "Text - Tab separated (.txt)":
        export_selected_to_txt(self, table=table)
    elif format_choice == "CSV (.csv)":
        export_selected_to_csv(self, table=table)

def setup_right_panel_for_Advanced(self):
        lang = self.current_language
        self.right_layout.addStretch()
        self.btn_load = QPushButton("Load All Readings")
        self.btn_load.setText(translations[lang]["btn_load"])
        # self.btn_load.setStyleSheet(btnStyle)
        self.btn_load.clicked.connect(self.update_table)
        self.right_layout.addWidget(self.btn_load)

        self.btn_load_meters = QPushButton("Load Meters")
        self.btn_load_meters.setText("load meters")
        # self.btn_load_meters.setStyleSheet(btnStyle)
        self.btn_load_meters.clicked.connect(lambda: self.display_all_meters())
        self.right_layout.addWidget(self.btn_load_meters)

        # Create the button
        self.btn_read = QPushButton("Read New Meter")
        self.btn_read.setText(translations[lang]["btn_read"])
        # self.btn_read.setStyleSheet(btnStyle)
        self.btn_read.clicked.connect(lambda: get_meter_id(self))
        
        self.right_layout.addWidget(self.btn_read)

        self.btn_read_all = QPushButton("Read All Meters")
        self.btn_read_all.setText(translations[lang]["btn_read_all"])
        # self.btn_read_all.setStyleSheet(btnStyle)
        self.btn_read_all.clicked.connect(lambda: self.read_all_meters())
        self.right_layout.addWidget(self.btn_read_all)

        self.read_mbus = QPushButton(translations[lang]["read_mbus"])
        self.read_mbus.clicked.connect(lambda: sync_mbus_to_db())
        self.right_layout.addWidget(self.read_mbus)


        self.export_btn = QPushButton("Export")
        self.export_btn.setText(translations[lang]["export_btn"])
        # self.export_btn.setStyleSheet(btnStyle)
        self.export_btn.clicked.connect(lambda: export_methods(self))
        self.right_layout.addWidget(self.export_btn)

        self.btn_delete = QPushButton("Delete") 
        self.btn_delete.setText(translations[lang]["btn_delete"])
        # self.btn_delete.setStyleSheet(btnStyle)
        self.btn_delete.clicked.connect(lambda: delete_selected_rows(self))
        self.right_layout.addWidget(self.btn_delete)

        self.right_layout.addWidget(QLabel("Sort: "))

        self.sort_box = QComboBox()
        self.sort_box.addItems(["Meter Id", "value"])
        self.right_layout.addWidget(self.sort_box)

        self.order_box = QComboBox()
        self.order_box.addItems(translations[lang]["order_box"]) 
        self.right_layout.addWidget(self.order_box)

        self.sort_button = QPushButton(translations[lang]["sort_button"])
        self.sort_button.clicked.connect(self.sort_table)
        self.right_layout.addWidget(self.sort_button)

        self.right_layout.addSpacing(10)
        self.right_layout.addWidget(QLabel(translations[lang]["date_filter"]))

        date_layout = QHBoxLayout()
        self.date_from = QDateEdit(QDate.currentDate())
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd HH-MM-SS")

        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd HH-MM-SS")

        date_layout.addWidget(self.date_from)
        date_layout.addWidget(self.date_to)
        self.right_layout.addLayout(date_layout)

        self.checkbox = QCheckBox("Date Selected \ Tarih")
        self.right_layout.addWidget(self.checkbox)

        self.filter_box = QComboBox()
        self.filter_box.addItems(translations[lang]["filter_box"])
        self.right_layout.addWidget(self.filter_box)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filter value...") 
        self.right_layout.addWidget(self.filter_input)

        self.filter_button = QPushButton("Filter")
        self.filter_button.setText(translations[lang]["filter_button"])
        # self.filter_button.setStyleSheet(btnStyle)
        self.filter_button.clicked.connect(self.apply_all_filters)
        self.right_layout.addWidget(self.filter_button)