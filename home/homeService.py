
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton
)

from PyQt5.QtCore import Qt
from style.btnStyle import btnStyle
from database import delete_meter

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
        self.btn_delete.clicked.connect(self.delete_selected_rows)
        self.right_layout.addWidget(self.btn_delete)
