import sys, csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from database import get_all_readings, save_reading, save_meter, delete_meter, get_last_7_days
from mbus_reader import read_meter
from datetime import datetime

# ⬇️ New matplotlib imports for embedding charts
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
        self.resize(1500, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.right_container = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_container.setLayout(self.right_layout)
        self.main_layout.addWidget(self.right_container)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.right_container)
        self.right_container.setFixedWidth(300)

        self.home_tab = QWidget()
        self.advanced_tab = QWidget()
        self.settings_tab = QWidget()
        self.graphical_visualization  = QWidget()

        self.tab_widget.addTab(self.home_tab, "Home")
        self.tab_widget.addTab(self.advanced_tab, "Advanced")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.graphical_visualization, "Graphical Visualization")
        
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.setup_home_tab()
        self.setup_advanced_tab()
        self.setup_settings_tab()
        self.setup_graphical_visualization_tab()
        self.setup_right_panel_for_Home()

    def setup_home_tab(self):
        layout = QVBoxLayout()
        self.home_tab.setLayout(layout)

        title = QLabel("Water Meter Readings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px; padding: 10px;")
        layout.addWidget(title)

        self.home_table = self.create_table()
        layout.addWidget(self.home_table)

    def setup_advanced_tab(self):
        layout = QVBoxLayout()
        self.advanced_tab.setLayout(layout)

        title = QLabel("Advanced Water Meter Readings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px; padding: 10px;")
        layout.addWidget(title)

        self.advanced_table = self.create_table()
        layout.addWidget(self.advanced_table)
        
    def setup_settings_tab(self):
        layout = QVBoxLayout()
        self.settings_tab.setLayout(layout)

        title = QLabel("Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px; padding: 10px;")
        layout.addWidget(title)

    def setup_graphical_visualization_tab(self):
        layout = QVBoxLayout()
        self.graphical_visualization.setLayout(layout)

        title = QLabel("Graphical Visualization")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        self.graphical_chart = self.create_graphical_chart()
        layout.addWidget(self.graphical_chart)

    def create_graphical_chart(self):
        last_7_days = get_last_7_days()

        days = [row[0] for row in last_7_days]
        usage = [row[1] for row in last_7_days]

        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)

        ax.plot(days, usage, marker='o', linestyle='-', color='blue', label='Usage (m³)')

        # Add value labels on the points
        for i, value in enumerate(usage):
            ax.text(days[i], value, f"{value:.2f}", fontsize=9, ha='center', va='bottom')

        ax.set_title("Water Usage Over Last 7 Days")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Usage (m³)")

        ax.set_yscale('log')  

        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.updateGeometry()

        return canvas
    
    def create_table(self) -> QTableWidget:
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

    def setup_right_panel_for_Home(self):
        self.right_layout.addStretch()
        self.btn_load = QPushButton("Load All Readings")
        self.btn_load.setStyleSheet(btnStyle)
        self.btn_load.clicked.connect(self.update_table)
        self.right_layout.addWidget(self.btn_load)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setStyleSheet(btnStyle)
        self.btn_delete.clicked.connect(self.delete_selected_rows)
        self.right_layout.addWidget(self.btn_delete)

    def setup_right_panel_for_advanced(self):
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

        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.setStyleSheet(btnStyle)
        self.export_btn.clicked.connect(self.export_table_to_csv)
        self.right_layout.addWidget(self.export_btn)

        self.usage_chart_btn = QPushButton("Show Usage Chart")
        self.usage_chart_btn.setStyleSheet(btnStyle)
        self.usage_chart_btn.clicked.connect(self.show_usage_chart)
        self.right_layout.addWidget(self.usage_chart_btn)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setStyleSheet(btnStyle)
        self.btn_delete.clicked.connect(self.delete_selected_rows)
        self.right_layout.addWidget(self.btn_delete)

        self.sort_box = QComboBox()
        self.sort_box.addItems(["Meter ID", "Timestamp", "Value"])
        self.right_layout.addWidget(self.sort_box)

        self.sort_button = QPushButton("Sort")
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

        self.checkbox = QCheckBox("Date Selected")
        self.right_layout.addWidget(self.checkbox)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["Meter ID", "Timestamp", "Value"])
        self.right_layout.addWidget(self.filter_box)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filter value...")
        self.right_layout.addWidget(self.filter_input)

        self.filter_button = QPushButton("Filter")
        self.filter_button.setStyleSheet(btnStyle)
        self.filter_button.clicked.connect(self.apply_all_filters)
        self.right_layout.addWidget(self.filter_button)

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

        if tab_name == "Home":
            self.setup_right_panel_for_Home()
            self.update_table()
        elif tab_name == "Advanced":
            self.setup_right_panel_for_advanced()
            self.update_table()
        elif tab_name == "Settings":
            self.right_layout.addWidget(QLabel("Settings Panel Placeholder"))
        
    def populate_table(self, readings: list[tuple], table: QTableWidget):
        table.setRowCount(0)
        for row_data in readings:
            row = table.rowCount()
            table.insertRow(row)
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            table.setItem(row, 0, checkbox_item)
            table.setItem(row, 1, QTableWidgetItem(str(row_data[1])))
            table.setItem(row, 2, QTableWidgetItem(str(row_data[2])))
            table.setItem(row, 3, QTableWidgetItem(str(row_data[3])))

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
        column_index = {"Meter ID": 0, "Timestamp": 1, "Value": 2}.get(sort_by, 0)
        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.home_tab:
            self.home_table.sortItems(column_index, Qt.AscendingOrder)
        elif current_tab == self.advanced_tab:
            self.advanced_table.sortItems(column_index, Qt.AscendingOrder)

    def read_and_save_meter(self, meter_id: int) -> bool:
        data = read_meter(meter_id)
        if data:
            timestamp = data.get("timestamp")
            usage = data.get("value")
            if timestamp and usage is not None:
                save_meter(meter_id)
                save_reading(meter_id, timestamp, usage)
                return True
        return False

    def read_new_meter(self):
        if self.read_and_save_meter(3):
            self.update_table()
        else:
            QMessageBox.warning(self, "Warning", "Failed to read meter data.")

    def read_all_meters(self):
        for meter_id in [1, 2, 3]:
            self.read_and_save_meter(meter_id)
        self.update_table()

    def filter_by_date(self, readings: list[tuple]) -> list[tuple]:
        if not self.checkbox.isChecked():
            return readings
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        return [r for r in readings if date_from <= r[2][:10] <= date_to]

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

    def delete_selected_rows(self):
        current_tab = self.tab_widget.currentWidget()
        table = None

        if current_tab == self.home_tab:
            table = self.home_table
        elif current_tab == self.advanced_tab:
            table = self.advanced_table

        if not table:
            return

        rows_to_delete = []
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                rows_to_delete.append(row)

        if not rows_to_delete:
            QMessageBox.information(self, "No Selection", "No meters selected for deletion.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(rows_to_delete)} selected meter(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            for row in reversed(rows_to_delete):
                meter_id_item = table.item(row, 1)
                meter_time_item = table.item(row, 2)
                meter_value_item = table.item(row, 3)
                if meter_id_item:
                    try:
                        meter_id = int(meter_id_item.text())
                        meter_value = float(meter_value_item.text())
                        meter_time = meter_time_item.text()
                        delete_meter(meter_id, meter_value, meter_time)
                    except Exception as e:
                        print(f"Error deleting meter: {e}")
                table.removeRow(row)

            QMessageBox.information(self, "Deleted", "Selected meters deleted.")

    def export_table_to_csv(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.home_tab:
            table = self.home_table
        elif current_tab == self.advanced_tab:
            table = self.advanced_table
        else:
            QMessageBox.warning(self, "Export Failed", "No exportable table in this tab.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]
                    writer.writerow(headers)
                    for row in range(table.rowCount()):
                        row_data = []
                        for col in range(table.columnCount()):
                            item = table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                QMessageBox.information(self, "Export Successful", "Table data exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"An error occurred:\n{str(e)}")

    def show_usage_chart(self):
        QMessageBox.information(self, "Info", "Usage chart feature is now in the Graphical Visualization tab.")


# ---------- Run App ----------
def launch_gui():
    app = QApplication(sys.argv)
    window = WaterMeterGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_gui()
