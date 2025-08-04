
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from database import get_last_7_days, get_Readings_ById
from settings.settingsService import translations
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from style.btnStyle import btnStyle

def create_graphical_chart(self, meter_ids, date_limit=None):
    lang = self.current_language
    fig = Figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'cyan', 'magenta']

    for idx, meter_id in enumerate(meter_ids):
        readings = get_Readings_ById(meter_id)

        if date_limit:
            readings = readings[-date_limit:]

        if not readings:
            continue

        days = [row[0] for row in readings]
        usage = [row[1] for row in readings]

        color = colors[idx % len(colors)]
        ax.plot(days, usage, marker='o', linestyle='-', color=color, label=f"Meter {meter_id}")

        for i, value in enumerate(usage):
            ax.text(days[i], value, f"{value:.2f}", fontsize=8, ha='center', va='bottom')

    ax.set_title(translations[lang]["chart_title"])
    ax.set_xlabel(translations[lang]["x_label"])
    ax.set_ylabel(translations[lang]["y_label"])
    ax.set_yscale('log')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    canvas = FigureCanvas(fig)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    canvas.updateGeometry()

    return canvas


def setup_graphical_visualization_tab(self):
    if not hasattr(self, 'graphical_layout'):
        self.graphical_layout = QVBoxLayout()
        self.graphical_visualization.setLayout(self.graphical_layout)

        title = QLabel("Graphical Visualization")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        self.graphical_layout.addWidget(title)

    if hasattr(self, 'graphical_chart') and self.graphical_chart:
        self.graphical_layout.removeWidget(self.graphical_chart)
        self.graphical_chart.setParent(None)

    # Get selected meters
    selected_items = self.meter_list.selectedItems()
    selected_meter_ids = [item.text() for item in selected_items]

    # Get date filter
    range_text = self.date_range_select.currentText()
    if range_text == "Last 7 Days":
        date_limit = 7
    elif range_text == "Last 30 Days":
        date_limit = 30
    else:
        date_limit = None

    self.graphical_chart = self.create_graphical_chart(selected_meter_ids, date_limit)
    self.graphical_layout.addWidget(self.graphical_chart)


def setup_right_panel_for_GV(self):
        self.right_layout.addStretch()

        self.ShowMeterlable = QLabel("Show Meter Usage")
        self.right_layout.addWidget(self.ShowMeterlable)

        # Multi-select meter list
        self.meter_list = QListWidget()
        self.meter_list.setSelectionMode(QListWidget.MultiSelection)
        for meter_id in ["1", "2", "3"]:
            self.meter_list.addItem(QListWidgetItem(meter_id))
        self.right_layout.addWidget(self.meter_list)

        # Date range dropdown
        self.date_range_select = QComboBox()
        self.date_range_select.addItems(["Last 7 Days", "Last 30 Days", "All Time"])
        self.right_layout.addWidget(self.date_range_select)

        # Button to generate chart
        self.filter_button = QPushButton("Show Chart")
        self.filter_button.setStyleSheet(btnStyle)
        self.filter_button.clicked.connect(self.setup_graphical_visualization_tab)
        self.right_layout.addWidget(self.filter_button)


def get_meter(meterId):
    readings = get_Readings_ById(meterId)
    print(readings)