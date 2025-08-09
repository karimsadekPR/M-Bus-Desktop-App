
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton
)

translations = {
    'en': {
        "btn_ok": "OK",
        "btn_cancel": "Cancel",
        'lang_label': 'Language:',
        'lang_combo': ['English', 'Türkçe'],
        'btn_load': "Load All Readings",
        'btn_read': "Read New Meter",
        'btn_read_all': "Read All Meters",
        'btn_delete': "Delete",
        'btn_export': "Export to CSV",
        'filter_button': "Filter",
        'sort_button': "Sort",
        "sort_box": ["Meter ID", "Timestamp", "Value"],
        'lang_combo_0': "English",
        'lang_combo_1': "Türkçe",
        'auto_refresh_checkbox': "Enable Auto Refresh",
        'window_title': "Water Meter GUI",
        'home_title': "Water Meter Readings",
        'advanced_title': "Advanced Water Meter Readings",
        'refresh_interval_suffix': " sec",
        'tab_0': "Home",
        'tab_1': "Advanced",
        'tab_2': "Settings",
        'Graphical Visualization':"Graphical Visualization",
        "chart_title": "Water Usage Over Last 7 Days",
        "x_label": "Date",
        "y_label": "Total Usage (m³)",
        "usage_chart_btn": "Show Usage Chart",
        "export_btn":"Export",
        # Add more as needed
    },
    'tr': {
        "btn_ok": "OK",
        "btn_cancel": "Cancel",
        'lang_label': 'Dil:',
        'lang_combo': ['İngilizce', 'Türkçe'],
        'btn_load': "Tüm Verileri Yükle",
        'btn_read': "Yeni Sayaç Oku",
        'btn_read_all': "Tüm Sayaçları Oku",
        'btn_delete': "Sil",
        'btn_export': "CSV'ye aktar",
        'filter_button': "Filtrele",
        'sort_button': "Sırala",
        "sort_box": ["Sayaç Kimliği", "Zaman Damgası", "Değer"],
        'lang_combo_0': "İngilizce",
        'lang_combo_1': "Türkçe",
        'auto_refresh_checkbox': "Otomatik Yenilemeyi Etkinleştir",
        'window_title': "Su Sayaçları Uygulaması",
        'home_title': "Su Sayacı Okumaları",
        'advanced_title': "Gelişmiş Su Sayaçı Okumaları",
        'refresh_interval_suffix': " sn",
        'tab_0': "Ana Sayfa",
        'tab_1': "Gelişmiş",
        'tab_2': "Ayarlar",
        'Graphical Visualization':"Grafiksel Görünüm",
        "chart_title": "Son 7 Günlük Su Kullanımı",
        "x_label": "Tarih",
        "y_label": "Toplam Kullanım (m³)",
        "usage_chart_btn":"Kullanım Tablosunu Göster",
        "export_btn":"aktar",
        # Add more as needed
    }
}

def setup_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout()

        # Language label
        self.lang_label = QLabel("Language:")
        self.lang_label.setObjectName("lang_label")
        layout.addWidget(self.lang_label)

        # Language combo box
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', 'Türkçe'])
        self.lang_combo.setCurrentIndex(0)
        layout.addWidget(self.lang_combo)

        # Connect language change signal
        self.lang_combo.currentTextChanged.connect(lambda: change_language(self, self.lang_combo.currentText()))

        # Set layout to the tab
        settings_tab.setLayout(layout)
        self.tab_widget.addTab(settings_tab, "Settings")

def translate_ui(self, lang):
        for widget in self.findChildren(QWidget):
            obj_name = widget.objectName()
            if obj_name in translations[lang]:
                if isinstance(widget, QComboBox):
                    current_text = widget.currentText()
                    widget.clear()
                    widget.addItems(translations[lang][obj_name])
                    if current_text in translations[lang][obj_name]:
                        widget.setCurrentText(current_text)
                elif isinstance(widget, QAbstractButton):
                    widget.setText(translations[lang][obj_name])
                elif isinstance(widget, QLabel):
                    widget.setText(translations[lang][obj_name])

def change_language(self, selected_lang):
        self.lang_combo.blockSignals(True)
        if selected_lang.lower().startswith("t"):
            self.current_language = "tr"
        else:
            self.current_language = "en"

        translate_ui(self, self.current_language)
        self.lang_combo.blockSignals(False)