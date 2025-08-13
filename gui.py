import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView,
    QTableWidgetItem, QMessageBox,
    QTabWidget
)

from PyQt5.QtGui import QIcon

from PyQt5.QtCore import Qt
from database import get_all_readings, save_reading, save_meter, get_all_meter_ids
from M_Bus_Services.mbus_reader import read_meter
from settings.settingsService import setup_settings_tab, translate_ui
from home.homeService import setup_home_tab, setup_right_panel_for_Home
from advanced.advancedService import setup_advanced_tab, setup_right_panel_for_Advanced
from Graphical_visualization.Graphical_visualizationService import  setup_right_panel_for_GV

class WaterMeterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language = 'en'
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
        table.setRowCount(0)
        for row_data in readings:
            row = table.rowCount()
            table.insertRow(row)
            
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
        readings = get_all_readings()
        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.home_tab:
            self.populate_table(readings, self.home_table)
        elif current_tab == self.advanced_tab:
            self.populate_table(readings, self.advanced_table)

    def apply_all_filters(self):
        readings = get_all_readings()
        readings = self.filter_by_date(readings)
        readings = self.filter_by_input(readings)
        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.home_tab:
            self.populate_table(readings, self.home_table)
        elif current_tab == self.advanced_tab:
            self.populate_table(readings, self.advanced_table)

    def sort_table(self):
        sort_by = self.sort_box.currentText()
        order_text = self.order_box.currentText()
        print(sort_by, order_text)
        
        column_index = {"Meter ID": 1, "Timestamp": 2, "Value": 3}.get(sort_by, 1)
        order = Qt.AscendingOrder if order_text == "Ascending" else Qt.DescendingOrder
        
        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.home_tab:
            self.home_table.sortItems(column_index, order)
        elif current_tab == self.advanced_tab:
            self.advanced_table.sortItems(column_index, order)


    def read_and_save_meter(self, meter_id: int) -> tuple:
        """Read meter data and return the newly saved reading."""
        data = read_meter(meter_id)
        print(data)
        if data:
            timestamp = data.get("timestamp")
            usage = data.get("value")
            if timestamp and usage is not None:
                save_meter(meter_id)
                save_reading(meter_id, timestamp, usage)
                # self.display_new_readings([data])
                return (None, meter_id, timestamp, usage)
        return None

    def display_new_readings(self, new_readings: list[tuple], table: QTableWidget = None):
        """Display only the newly read readings in the appropriate table."""
        if table is None:
            current_tab = self.tab_widget.currentWidget()
            if current_tab == self.home_tab:
                table = self.home_table
            elif current_tab == self.advanced_tab:
                table = self.advanced_table
            else:
                return

        table.setRowCount(0)
        for row_data in new_readings:
            if row_data:
                row = table.rowCount()
                table.insertRow(row)
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                table.setItem(row, 0, checkbox_item)
                table.setItem(row, 1, QTableWidgetItem(str(row_data[1])))
                table.setItem(row, 2, QTableWidgetItem(str(row_data[2])))
                table.setItem(row, 3, QTableWidgetItem(str(row_data[3])))

    def read_new_meter(self, meterId):
        new_reading = self.read_and_save_meter(meterId)
        if new_reading:
            self.display_new_readings([new_reading])
        else:
            QMessageBox.warning(self, "Warning", "Failed to read meter data.")

    def read_all_meters(self):
        new_readings = []
        meter_ids = get_all_meter_ids()  # ✅ Now dynamic
        for meter_id in meter_ids:
            new_reading = self.read_and_save_meter(meter_id)
            if new_reading:
                new_readings.append(new_reading)

        if new_readings:
            self.populate_table(new_readings, self.advanced_table)
        else:
            QMessageBox.warning(self, "Warning", "No new meter data was read.")

    def filter_by_date(self, readings: list[tuple]) -> list[tuple]:
        if not self.checkbox.isChecked():
            return readings
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        return [r for r in readings if date_from <= datetime.strptime(r[2][:10], "%Y-%m-%d").date() <= date_to]  # ✅ Proper date comparison

    def filter_by_input(self, readings: list[tuple]) -> list[tuple]:
        filter_type = self.filter_box.currentText()
        value = self.filter_input.text().strip()
        if not value:
            return readings
        if filter_type == "Meter ID":
            return [r for r in readings if str(r[1]) == value]
        elif filter_type == "Timestamp":
            return [r for r in readings if value in r[2]]
        elif filter_type == "Value":
            try:
                return [r for r in readings if float(r[3]) == float(value)]
            except ValueError:
                return []
        return readings

# ---------- Run App ----------
def launch_gui():
    app = QApplication(sys.argv)
    window = WaterMeterGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_gui()
