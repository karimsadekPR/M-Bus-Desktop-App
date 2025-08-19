import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView,
    QTableWidgetItem, QMessageBox,
    QTabWidget, QCheckBox
)

from PyQt5.QtGui import QIcon

from PyQt5.QtCore import Qt
from M_Bus_Services.M_bus_parser import parse_mbus_payload
from M_Bus_Services.mbusfunction import read_device_data
from database import get_all_meters, get_all_readings,save_reading, save_meter, get_all_meter_ids
from settings.settingsService import get_settings, setup_settings_tab, translate_ui
from home.homeService import setup_home_tab, setup_right_panel_for_Home
from advanced.advancedService import setup_advanced_tab, setup_right_panel_for_Advanced, str_to_byte_list
from Graphical_visualization.Graphical_visualizationService import  setup_right_panel_for_GV
from datetime import datetime
from settings.settingsService import translations

def combine_datetime(r):
    try:
        time_str = r[5] # take only HH:MM:SS
        return datetime.strptime(f"{r[4]} {time_str}", "%Y-%m-%d %H:%M:%S")
    except (ValueError, IndexError):
        return None  # skip rows with invalid date/time
    
class WaterMeterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_table = "readings_table"
        lang = get_settings().get('lang')
        self.current_language = lang
        self.setWindowTitle("Water Meter GUI")
        self.setWindowIcon(QIcon('tools/icon/teksanIcon.ico'))
        self.resize(1800, 1000)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Left side - Tabs
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Right side - Panel
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_container.setLayout(self.right_layout)
        self.main_layout.addWidget(self.right_container)
        self.right_container.setFixedWidth(300)

        # Tabs
        self.home_tab = QWidget()
        self.advanced_tab = QWidget()
        self.graphical_visualization = QWidget()

        # self.tab_widget.addTab(self.home_tab, "Home")
        self.tab_widget.addTab(self.advanced_tab, "Advanced")
        self.tab_widget.addTab(self.graphical_visualization, "Graphical Visualization")
        
        # Setup each tab
        # setup_home_tab(self)
        # setup_right_panel_for_Home(self)
        setup_advanced_tab(self)
        setup_right_panel_for_Advanced(self)
        setup_settings_tab(self)

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setCurrentIndex(0)  

    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                elif item.layout() is not None:
                    self.clear_layout(item.layout())

    def on_tab_changed(self, index):
        tab_name = self.tab_widget.tabText(index)
        print(f"Switched to tab: {tab_name}")
        self.clear_layout(self.right_layout)

        if tab_name in ["Home", "Ana Sayfa"]:
            setup_right_panel_for_Home(self)
            self.update_table()

        elif tab_name in ["Advanced", "Gelişmiş Detaylar"]:
            setup_right_panel_for_Advanced(self)
            self.update_table()

        elif tab_name in ["Settings", "Ayarlar"]:
            self.right_layout.addWidget(QLabel("Settings Panel Placeholder"))
            translate_ui(self, self.current_language)

        elif tab_name == "Graphical Visualization":
            setup_right_panel_for_GV(self)

    def populate_table(self, readings: list[tuple], table: QTableWidget):
        lang = self.current_language
        table.setRowCount(0)
        for row_data in readings:
            row = table.rowCount()
            table.insertRow(row)

            table.setColumnCount(12)
            table.setHorizontalHeaderLabels([
            translations[lang]["select"],translations[lang]["meter_id"],translations[lang]["manufacturer"],
            translations[lang]["address"],translations[lang]["version"],translations[lang]["date"],translations[lang]["time"],
            translations[lang]["meter_type"],translations[lang]["date_no"],translations[lang]["value"],
            translations[lang]["unit"],translations[lang]["description"],translations[lang]["timestamp"]
            ])
            
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            table.setItem(row, 0, checkbox_item)
            
            for col_idx in range(12):
                if col_idx < len(row_data):
                    value = row_data[col_idx]
                else:
                    value = ""
                item = QTableWidgetItem(str(value) if value is not None else "")
                table.setItem(row, col_idx + 1, item)

    def update_table(self): 
        self.current_table = "readings_table"
        readings = get_all_readings()
        self.populate_table(readings, self.advanced_table)


    def apply_all_filters(self):
        readings = get_all_readings()            # fetch all readings
        readings = self.filter_by_date(readings)  # filter by date range
        readings = self.filter_by_input(readings) # filter by user input

        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.home_tab:
            self.populate_table(readings, self.home_table)
        elif current_tab == self.advanced_tab:
            self.populate_table(readings, self.advanced_table)
    
    def sort_table(self):
        sort_by = self.sort_box.currentText()
        order_text = self.order_box.currentText()
        print(sort_by, order_text)
        
        column_index = {"Meter Id": 1,"value": 9}.get(sort_by, 1)
        order = Qt.AscendingOrder if order_text == "Ascending" else Qt.DescendingOrder
        
        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.home_tab:
            self.home_table.sortItems(column_index, order)
        elif current_tab == self.advanced_tab:
            self.advanced_table.sortItems(column_index, order)


    def read_and_save_meter(self, meter_id: str) -> dict | None:
        """Read meter data, save it, and return the newly saved reading as a dict."""
        data = read_device_data(meter_id)
        print(data)
        if data:
            timestamp = data.get("timestamp")
            usage = data.get("value")
            if timestamp and usage is not None:
                # Extract details for saving
                manufacturer = data.get("manufacturer", "")
                address = data.get("address", "")
                version = data.get("version", "")
                meter_type = data.get("meter_type", "")

                # Save to meters table
                save_meter(
                    meter_id,
                    manufacturer=manufacturer,
                    address=address,
                    version=version,
                    meter_type=meter_type
                )

                # Current date & time split
                Date = datetime.now().strftime("%Y-%m-%d")
                Time = datetime.now().strftime("%H:%M:%S")

                # Save to readings table
                save_reading(
                    meterId=meter_id,
                    manufacturer=manufacturer,
                    address=address,
                    version=version,
                    date=Date,
                    time=Time,
                    meter_type=meter_type,
                    date_no=None,
                    value=usage,
                    unit=data.get("unit", ""),
                    description="Usage",
                    timestamp=timestamp
                )

                # Return in dict form so display_new_readings works
                return {
                    "ID": meter_id,
                    "Manufacturer": manufacturer,
                    "Address": address,
                    "Version": version,
                    "Meter Type": meter_type,
                    "Data Records": [
                        {"Value": usage, "Unit": data.get("unit", ""), "Description": "Usage"}
                    ],
                    "timestamp": timestamp
                }
        return None

    def display_new_readings(self, readings: list[dict], Date, Time):
        print(readings)
        for reading in readings:
            id_value = reading.get("ID", "")
            manufacturer = reading.get("Manufacturer", "")
            address = reading.get("Address", "")
            version = reading.get("Version", "")
            date_value = Date
            time_value = Time
            meter_type = reading.get("Meter Type", "")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            data_records = reading.get("Data Records", [])

            for idx, record in enumerate(data_records):
                row_position = self.advanced_table.rowCount()
                self.advanced_table.insertRow(row_position)

                columns = [
                    "",  # Select column
                    id_value,
                    manufacturer,
                    address,
                    version,
                    date_value,
                    time_value,
                    meter_type,
                    idx + 1,  # Data No
                    record.get("Value", ""),
                    record.get("Unit", ""),
                    record.get("Description", ""),
                    timestamp
                ]
                for col_idx, value in enumerate(columns):
                    self.advanced_table.setItem(row_position, col_idx, QTableWidgetItem(str(value)))

    def display_all_meters(self):
            self.current_table = "meters_table"
            meters = get_all_meters()  # Assuming this returns a list of dicts or objects
            # print(meters)
            self.advanced_table.setRowCount(0)
            self.advanced_table.setColumnCount(6)
            self.advanced_table.setHorizontalHeaderLabels([
                "Select", "ID", "Manufacturer", "Address", "Version", "Meter Type"
            ])
            self.advanced_table.setColumnWidth(0, 50)

            for row, meter in enumerate(meters):
                self.advanced_table.insertRow(row)

                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                self.advanced_table.setItem(row, 0, checkbox_item)

                # Fill in other columns (assuming dict keys; adjust to your data)
                self.advanced_table.setItem(row, 1, QTableWidgetItem(str(meter[1])))
                self.advanced_table.setItem(row, 2, QTableWidgetItem(meter[2]))
                self.advanced_table.setItem(row, 3, QTableWidgetItem(meter[3]))
                self.advanced_table.setItem(row, 4, QTableWidgetItem(meter[4]))
                self.advanced_table.setItem(row, 5, QTableWidgetItem(meter[5]))


    def read_new_meter(self, meterId):
        new_reading = self.read_and_save_meter(meterId)
        if new_reading:
            Date = datetime.now().strftime("%Y-%m-%d")
            Time = datetime.now().strftime("%H:%M:%S")
            self.display_new_readings([new_reading], Date, Time)
        else:
            QMessageBox.warning(self, "Warning", "Failed to read meter data.")

    def read_all_meters(self):
        new_readings = []
        meter_ids = get_all_meter_ids()
        self.advanced_table.setRowCount(0)  # clear table before adding
        for meter_id in meter_ids:
            byte_list = str_to_byte_list(meter_id)
            new_reading = parse_mbus_payload(read_device_data(serialId=byte_list))
            if new_reading:
                for record in new_reading["Data Records"]:
                    if record["Unit"] != "-":
                        Date = datetime.now().strftime("%Y-%m-%d")
                        Time = datetime.now().strftime("%H:%M:%S")
                        save_reading(meterId= new_reading["ID"], manufacturer= new_reading["Manufacturer"], address= new_reading["Address"], version = new_reading["Version"], date= Date, time= Time,
                        meter_type= new_reading["Meter Type"] , date_no= None, value= record["Value"], unit= record["Unit"], description= record["Description"], timestamp=None)
                        new_readings.append(new_reading)
                        self.display_new_readings(new_readings, Date, Time)

    def filter_by_date(self, readings: list[tuple]) -> list[tuple]:
        if not self.checkbox.isChecked():
            return readings

        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()

        print(date_from, date_to)

        filtered = []
        for r in readings:
            dt = combine_datetime(r)
            print(dt)
            if dt and date_from <= dt.date() <= date_to:
                filtered.append(r)
        return filtered


    def filter_by_input(self, readings):
        filter_type = self.filter_box.currentText().strip()
        value = self.filter_input.text().strip()
        print(readings)
        # No filter applied
        if not value:
            return readings

        # --- Meter ID filter ---
        if filter_type.lower() == "meter id":
            return [r for r in readings if len(r) > 1 and str(r[0]) == value]

        # Default: return everything if filter not recognized
        return readings


def safe_float(val):
    """Convert to float safely, return None if not valid"""
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

# ---------- Run App ----------
def launch_gui():
    print(get_settings())
    app = QApplication(sys.argv)
    window = WaterMeterGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_gui()
