
from PyQt5.QtWidgets import ( QMessageBox )

from PyQt5.QtCore import Qt
from database import delete_Reading, delete_meter


def delete_selected_rows(self, func_key_word):
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
        if func_key_word == 'readings_table':
            for row in reversed(rows_to_delete):
                # Get table items
                meter_id_item = table.item(row, 1)
                meter_date_item = table.item(row, 5)
                meter_time_item = table.item(row, 6)
                meter_type_item = table.item(row, 7)
                meter_value_item = table.item(row, 9)
                meter_unit_item = table.item(row, 10)
                meter_description_item = table.item(row, 11)

                try:
                    # Extract and convert values safely
                    meter_id = meter_id_item.text() if meter_id_item else None
                    meter_date = meter_date_item.text().strip() if meter_date_item else None
                    meter_time = meter_time_item.text().strip() if meter_time_item else None
                    meter_type = meter_type_item.text().strip() if meter_type_item else None
                    meter_value = float(meter_value_item.text().strip()) if meter_value_item else None
                    meter_unit = meter_unit_item.text().strip() if meter_unit_item else None
                    meter_description = meter_description_item.text().strip() if meter_description_item else None

                    # Pass all values to delete_meter
                    delete_Reading(
                        meter_id,
                        meter_date,
                        meter_time,
                        meter_type,
                        meter_value,
                        meter_unit,
                        meter_description
                    )

                except (ValueError, AttributeError) as e:
                    print(f"Error processing row {row}: {e}")
                except Exception as e:
                    print(f"Error deleting meter: {e}")

                table.removeRow(row)

            QMessageBox.information(self, "Deleted", "Selected meters deleted.")
        
        elif func_key_word == 'meters_table':
            for row in reversed(rows_to_delete):
                print(rows_to_delete)
                try:
                    # Extract text values from table cells
                    meter_id_item = table.item(row, 1).text() if table.item(row, 1) else None
                    meter_name_manufacture = table.item(row, 2).text() if table.item(row, 2) else None
                    meter_address = table.item(row, 3).text() if table.item(row, 3) else None
                    meter_version = table.item(row, 4).text() if table.item(row, 4) else None
                    meter_meter_type = table.item(row, 5).text() if table.item(row, 5) else None
                    print(meter_id_item,meter_name_manufacture,meter_address)
                    delete_meter(
                        meter_id_item,
                        meter_name_manufacture,
                        meter_address,
                        meter_version,
                        meter_meter_type
                    )

                    # Remove row from table after deletion
                    table.removeRow(row)

                except (ValueError, AttributeError) as e:
                    print(f"Error processing row {row}: {e}")
                except Exception as e:
                    print(f"Error deleting meter: {e}")

            QMessageBox.information(self, "Deleted", "Selected meters deleted.")



                

