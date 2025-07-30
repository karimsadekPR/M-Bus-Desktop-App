import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton
)

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
