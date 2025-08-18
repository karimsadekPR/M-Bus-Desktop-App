
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton, QRadioButton,
    QGridLayout, QSpinBox
)
import json


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
        "read_mbus":"Read MBUS",
        "export_btn":"Export",
        "order_box":["Ascending","Descending"],
        "filter_box":["Meter ID"],
        "date_filter":"Date Filter:",
        "select": "Select",
        "meter_id": "Meter ID",
        "manufacturer": "Manufacturer",
        "address": "Address",
        "version": "Version",
        "date": "Date",
        "time": "Time",
        "meter_type": "Meter Type",
        "date_no": "Date No",
        "value": "Value",
        "unit": "Unit",
        "description": "Description",
        "timestamp": "Timestamp",
        "load_meters":"Load meters",
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
        "read_mbus":"MBUS Oku",
        "export_btn":"aktar",
        "order_box":["Artan","Azalan"],
        "filter_box":["Sayaç Kimliği"],
        "date_filter":"tarih_filtresi: ",
        "select": "Seç",
        "meter_id": "Sayaç ID",
        "manufacturer": "Üretici",
        "address": "Adres",
        "version": "Versiyon",
        "date": "Tarih",
        "time": "Saat",
        "meter_type": "Sayaç Türü",
        "date_no": "Tarih No",
        "value": "Değer",
        "unit": "Birim",
        "description": "Açıklama",
        "timestamp": "Zaman Damgası",
        "load_meters":"yük metre",
    }
}

def setup_settings_tab(self):
    settings_info = get_settings()
    settings_tab = QWidget()
    main_layout = QVBoxLayout()

    # --- Settings Grid ---
    grid = QGridLayout()

    # Comm Port
    grid.addWidget(QLabel("Comm Port"), 0, 0)
    self.comm_port = QComboBox()
    for port in range(1, 31):
        self.comm_port.addItems([f'COM{port}'])
    comm_port_str = settings_info.get("comm_port", "")
    comm_portIndex =self.comm_port.findText(comm_port_str)
    self.comm_port.setCurrentIndex(comm_portIndex)

    grid.addWidget(self.comm_port, 0, 1)

    # Baudrate
    grid.addWidget(QLabel("Baudrate"), 1, 0)
    self.baudrate = QComboBox()
    self.baudrate.addItems(["2400"])
    self.baudrate.setEditable(False)
    baudrate_str = settings_info.get("baudrate", "")
    baudrateIndex = self.baudrate.findText(baudrate_str)
    if baudrateIndex != -1:
        self.baudrate.setCurrentIndex(baudrateIndex)
    grid.addWidget(self.baudrate, 1, 1)
    grid.addWidget(QLabel("bps"), 1, 2)

    # Parity
    grid.addWidget(QLabel("Parity"), 2, 0)
    self.parity = QComboBox()
    self.parity.addItems(["Even","None"])
    parity_str = settings_info.get("parity", "")
    parityIndex = self.parity.findText(parity_str)
    self.parity.setCurrentIndex(parityIndex)
    grid.addWidget(self.parity, 2, 1)

    # Retry Counter
    grid.addWidget(QLabel("Retry Counter"), 3, 0)
    self.retry_counter = QSpinBox()
    self.retry_counter.setRange(0, 10)
    self.retry_counter.setValue(3)
    grid.addWidget(self.retry_counter, 3, 1)

    # Timeout
    grid.addWidget(QLabel("Timeout"), 4, 0)
    self.timeout = QSpinBox()
    self.timeout.setRange(100, 10000)
    self.timeout.setValue(3000)
    grid.addWidget(self.timeout, 4, 1)
    grid.addWidget(QLabel("msec"), 4, 2)

    # Language
    grid.addWidget(QLabel("Language"), 5, 0)
    self.lang_combo = QComboBox()
    self.lang_combo.addItems(["English", "Türkçe"])
    lang = settings_info.get("lang")
    if lang == 'en':
        self.lang_combo.setCurrentIndex(0)
    else:
        self.lang_combo.setCurrentIndex(1)
    grid.addWidget(self.lang_combo, 5, 1)

    main_layout.addLayout(grid)

    # --- Buttons ---
    btn_layout = QHBoxLayout()
    self.btn_apply = QPushButton("Apply")
    self.btn_save = QPushButton("Save")
    self.btn_apply.clicked.connect(lambda:applySettings(self))
    self.btn_save.clicked.connect(lambda:saveSettings(self))
    btn_layout.addWidget(self.btn_apply)
    btn_layout.addWidget(self.btn_save)
    main_layout.addLayout(btn_layout)

    # Set layout to the tab
    settings_tab.setLayout(main_layout)
    self.tab_widget.addTab(settings_tab, "Settings")

import json

def applySettings(self):
    # Get values from widgets
    settings = { "comm_port":self.comm_port.currentText(),
    "baudrate" : self.baudrate.currentText(),
    "parity" : self.parity.currentText(),
    "retry_counter_value" : self.retry_counter.value(),
    "timeout_value" : self.timeout.value(),
    "lang" : "tr" if self.lang_combo.currentText() == "Türkçe" else "en" }

    change_language(self, settings["lang"])

    return settings



def saveSettings(self):
    # Make sure settings are up-to-date before saving
    settings = applySettings(self)
    # Save settings to file
    with open("settings.json", "w") as f:
        json.dump({
            "comm_port": settings["comm_port"],
            "baudrate": settings["baudrate"],
            "parity": settings["parity"],
            "retry_counter": settings["retry_counter_value"],
            "timeout": settings["timeout_value"],
            "lang": settings["lang"]

        }, f, indent=4)
    print(settings)

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

def get_settings():
        try:
            with open("settings.json") as f:
                print(f)
                return json.load(f)
        except FileNotFoundError:
             return {}
