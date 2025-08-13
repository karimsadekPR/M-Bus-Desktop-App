# gui.py

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from database import get_last_7_days, get_all_readings_id
from settings.settingsService import translations
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from style.btnStyle import btnStyle

from datetime import datetime
import matplotlib.dates as mdates


from datetime import datetime
import matplotlib.dates as mdates

def create_graphical_chart(self, meter_ids, date_limit=None):
    lang = self.current_language
    fig = Figure(figsize=(14, 7))  # Wider chart
    ax = fig.add_subplot(111)
    
    # Better color palette
    colors = ['#007acc', '#28a745', '#dc3545', '#fd7e14', '#6f42c1', '#20c997', '#6610f2', '#17a2b8']

    for idx, meter_id in enumerate(meter_ids):
        readings = get_all_readings_id(meter_id)
        if date_limit:
            readings = readings[-date_limit:]

        if not readings:
            continue

        days = [datetime.strptime(row[0], "%Y-%m-%d") for row in readings]
        usage = [row[1] for row in readings]

        color = colors[idx % len(colors)]
        ax.plot(
            days, usage, marker='o', linestyle='-', linewidth=2.5,
            color=color, label=f"Meter {meter_id}"
        )

        for i, value in enumerate(usage):
            ax.text(
                days[i], value + max(usage)*0.02,  # place above points
                f"{value:.2f}", fontsize=9, ha='center', va='bottom', color=color
            )

    # ✨ Stylish axes
    ax.set_title(translations[lang]["chart_title"], fontsize=18, fontweight='bold')
    ax.set_xlabel(translations[lang]["x_label"], fontsize=14)
    ax.set_ylabel(translations[lang]["y_label"], fontsize=14)

    # ✅ Date formatting
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate(rotation=30)

    # ✨ Grid and tick style
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.tick_params(axis='both', labelsize=12)

    # ✨ Legend styling
    legend = ax.legend(fontsize=12, loc='upper left', frameon=False)

    # ✨ Background color
    ax.set_facecolor('#f9f9f9')
    fig.patch.set_facecolor('#ffffff')

    canvas = FigureCanvas(fig)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    canvas.updateGeometry()

    return canvas


def setup_right_panel_for_GV(self):
    # Ensure right_layout is initialized
    if not hasattr(self, 'right_layout'):
        self.right_layout = QVBoxLayout()
        self.right_panel_widget = QWidget()
        self.right_panel_widget.setLayout(self.right_layout)
        self.main_layout.addWidget(self.right_panel_widget)  # main_layout should be your outer layout

    self.right_layout.addStretch()

    self.ShowMeterLabel = QLabel("Show Meter Usage")
    self.right_layout.addWidget(self.ShowMeterLabel)

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
    self.filter_button.clicked.connect(lambda: setup_graphical_visualization_tab(self))
    self.right_layout.addWidget(self.filter_button)


def setup_graphical_visualization_tab(self):
    # Ensure required components are initialized
    if not hasattr(self, 'meter_list') or not hasattr(self, 'date_range_select'):
        QMessageBox.warning(self, "Error", "Graphical Visualization panel is not initialized.")
        return
    
    if not hasattr(self, 'meter_list'):
        QMessageBox.warning(self, "Error", "Meter list not initialized. Please try again.")
        return

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

    selected_items = self.meter_list.selectedItems()
    selected_meter_ids = [item.text() for item in selected_items]

    range_text = self.date_range_select.currentText()
    if range_text == "Last 7 Days":
        date_limit = 7
    elif range_text == "Last 30 Days":
        date_limit = 30
    else:
        date_limit = None

    self.graphical_chart = create_graphical_chart(self, selected_meter_ids, date_limit)
    self.graphical_layout.addWidget(self.graphical_chart)


def on_tab_changed(self, index):
    tab_text = self.tabs.tabText(index)
    print(f"Switched to tab: {tab_text}")

    if tab_text == "Graphical Visualization":
        # Initialize panel if not already
        if not hasattr(self, 'meter_list'):
            self.setup_right_panel_for_GV()

        setup_graphical_visualization_tab(self)
