import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget,QLabel,QHeaderView,QPushButton,QComboBox,QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from database import get_all_readings, save_reading, save_meter
from mbus_reader import read_meter

btnStyle = """
QPushButton {
    font-size: 16px;
    padding: 10px;
    margin: 5px;
    border: 1px solid #555;
    border-radius: 6px;
    background-color: #e6e6e6;
}

QPushButton:hover {
    background-color: #d4d4d4;
    border: 1px solid #333;
}
"""

class WaterMeterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Water Meter GUI")
        # Set up central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Start with specific size (but allow resizing)
        self.resize(1800, 900)  # 👈 Applies to the QMainWindow, not central_widget

        # Main layout
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)



        # ✅ Left Layout (Title + Table)
        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)

        self.title_label = QLabel("Water Meter Readings")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px; padding: 10px;")
        self.left_layout.addWidget(self.title_label)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Meter ID", "Timestamp", "Usage (m³)"])

        # Make all columns stretch evenly
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFixedWidth(1000)
        self.left_layout.addWidget(self.table)

        # ✅ Right Layout (Buttons + Filters)
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.right_layout)

        self.right_layout.addStretch()
        
        self.btn_load = QPushButton("Load All Readings")
        self.btn_load.setStyleSheet(btnStyle)
        self.btn_load.clicked.connect(self.update_table)
        self.right_layout.addWidget(self.btn_load)

        self.btn_read = QPushButton("Read New Meter")
        self.btn_read.setStyleSheet(btnStyle)
        self.btn_read.clicked.connect(self.read_new_meter)
        self.right_layout.addWidget(self.btn_read)

        self.btn_read_all = QPushButton("Read All Meters")
        self.btn_read_all.setStyleSheet(btnStyle)
        self.btn_read_all.clicked.connect(self.read_all_meters)
        self.right_layout.addWidget(self.btn_read_all)

        self.sort_box = QComboBox()
        self.sort_box.addItems(["Meter ID", "Timestamp", "Value"])
        self.right_layout.addWidget(self.sort_box)

        self.sort_button = QPushButton("Sort")
        self.sort_button.clicked.connect(self.sort_table)
        self.right_layout.addWidget(self.sort_button)


        # ✅ Load data into table at start
        self.update_table()


    def update_table(self):
        self.table.setRowCount(0)
        readings = get_all_readings()
        if readings:
            for row_data in readings:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(row_data[1])))
                self.table.setItem(row, 1, QTableWidgetItem(str(row_data[2])))
                self.table.setItem(row, 2, QTableWidgetItem(str(row_data[3])))
                
    def sort_table(self):
        sort_by = self.sort_box.currentText()
        column_index = 0

        if sort_by == "Meter ID":
            column_index = 0
        elif sort_by == "Timestamp":
            column_index = 1
        elif sort_by == "Value":
            column_index = 2

        self.table.sortItems(column_index, Qt.AscendingOrder)

    def read_new_meter(self):
        data = read_meter(3)
        if data:
            timestamp = data.get("timestamp")
            usage = data.get("value")
            meter_id = data.get("id")
            if timestamp and usage is not None:
                save_meter(meter_id)
                save_reading(meter_id, timestamp, usage)
                self.update_table()
            else:
                QMessageBox.warning(self, "Warning", "Incomplete meter data received.")
        else:
            QMessageBox.warning(self, "Warning", "Failed to read meter data.")

    def read_all_meters(self):
        meter_ids = [1, 2, 3]
        for meter_id in meter_ids:
            data = read_meter(meter_id)
            if data:
                timestamp = data.get("timestamp")
                usage = data.get("value")
                meter_id = data.get("id")
                if timestamp and usage is not None:
                    save_meter(meter_id)
                    save_reading(meter_id, timestamp, usage)
        self.update_table()

def launch_gui():
    app = QApplication(sys.argv)
    window = WaterMeterGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_gui()
