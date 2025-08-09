import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton
)
from PyQt5.QtCore import Qt
import pandas as pd  # For Excel export


def export_selected_to_csv(self, table):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
    )
    if not file_path:
        return

    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header, skip checkbox column
            headers = [table.horizontalHeaderItem(col).text() for col in range(1, table.columnCount())]
            writer.writerow(headers)

            # Write only checked rows
            for row in range(table.rowCount()):
                    row_data = []
                    for col in range(1, table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
        QMessageBox.information(self, "Export Successful", "Selected rows exported to CSV successfully!")
    except Exception as e:
        QMessageBox.critical(self, "Export Failed", f"An error occurred:\n{str(e)}")


def export_selected_to_txt(self, table):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save TXT", "", "Text Files (*.txt);;All Files (*)", options=options
    )
    if not file_path:
        return

    try:
        with open(file_path, mode='w', encoding='utf-8') as file:
            # Write header (tab separated), skip checkbox column
            headers = [table.horizontalHeaderItem(col).text() for col in range(1, table.columnCount())]
            file.write('\t\t'.join(headers) + '\n')

            # Write only checked rows
            for row in range(table.rowCount()):
                    row_data = []
                    for col in range(1, table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else "")
                    file.write('\t\t'.join(row_data) + '\n')
        QMessageBox.information(self, "Export Successful", "Selected rows exported to TXT successfully!")
    except Exception as e:
        QMessageBox.critical(self, "Export Failed", f"An error occurred:\n{str(e)}")


def export_selected_to_excel(self, table):
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options
    )
    if not file_path:
        return

    try:
        data = []
        headers = [table.horizontalHeaderItem(col).text() for col in range(1, table.columnCount())]

        # Collect rows that are checked
        for row in range(table.rowCount()):
                row_data = []
                for col in range(1, table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

        if not data:
            QMessageBox.warning(self, "Export Warning", "No rows selected for export.")
            return

        # Create a DataFrame and save to Excel
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(file_path, index=False)

        QMessageBox.information(self, "Export Successful", "Selected rows exported to Excel successfully!")
    except Exception as e:
        QMessageBox.critical(self, "Export Failed", f"An error occurred:\n{str(e)}")