
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
        "export_btn":"Export to CSV",
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
        "export_btn":"CSV'ye aktar",
        # Add more as needed
    }
}
def setup_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout()

        self.lang_label = QLabel(translations[self.current_language]['lang_label'])
        self.lang_label.setObjectName("lang_label")
        layout.addWidget(self.lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.setObjectName("lang_combo")
        self.lang_combo.addItems(translations[self.current_language]['lang_combo'])
        self.lang_combo.setCurrentIndex(0 if self.current_language == 'en' else 1)
        self.lang_combo.currentTextChanged.connect(on_language_change(self, self.current_language))
        layout.addWidget(self.lang_combo)

        settings_tab.setLayout(layout)
        self.tab_widget.addTab(settings_tab, translations[self.current_language]['tab_2'])

def translate_ui(self, lang):
        for widget in self.findChildren(QWidget):
            name = widget.objectName()
            if name in translations[lang]:
                if isinstance(widget, QComboBox):
                    current = widget.currentText()
                    widget.clear()
                    widget.addItems(translations[lang][name])
                    if current in translations[lang][name]:
                        widget.setCurrentText(current)
                elif isinstance(widget, (QAbstractButton, QLabel)):
                    widget.setText(translations[lang][name])

        # Update tab titles
        for i, tab_key in enumerate(['tab_0', 'tab_1', 'tab_2']):
            if i < self.tab_widget.count():
                self.tab_widget.setTabText(i, translations[lang][tab_key])

        # Update window title
        self.setWindowTitle(translations[lang]['window_title'])

def on_language_change(self, selected_lang):
        self.lang_combo.blockSignals(True)
        self.current_language = 'tr' if selected_lang.lower().startswith('t') else 'en'
        self.translate_ui(self.current_language)
        self.lang_combo.blockSignals(False)