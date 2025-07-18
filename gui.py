import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from database import get_all_readings, save_reading, save_meter
from mbus_reader import read_meter

class WaterMeterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Water Meter GUI")
        self.resize(900, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        # Main horizontal layout: Left (title + table), Right (buttons)
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Left vertical layout: Title on top of table
        self.left_layout = QVBoxLayout()
        self.layout.addLayout(self.left_layout)

        # Title
        self.title_label = QLabel("Water Meter Readings")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        self.left_layout.addWidget(self.title_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Meter ID", "Timestamp", "Usage (m³)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.left_layout.addWidget(self.table)

        # Right vertical layout: Buttons
        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.btn_load = QPushButton("Load All Readings")
        self.btn_load.clicked.connect(self.update_table)
        self.button_layout.addWidget(self.btn_load)

        self.btn_read = QPushButton("Read New Meter")
        self.btn_read.clicked.connect(self.read_new_meter)
        self.button_layout.addWidget(self.btn_read)

        self.btn_read_all = QPushButton("Read All Meters")
        self.btn_read_all.clicked.connect(self.read_all_meters)
        self.button_layout.addWidget(self.btn_read_all)

        # Update table initially
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
