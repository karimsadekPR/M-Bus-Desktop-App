
from PyQt5.QtWidgets import ( QMessageBox )

from PyQt5.QtCore import Qt
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
