# gui.py

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from database import get_all_meter_ids, get_all_readings_id, query_readings
from settings.settingsService import translations
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from style.btnStyle import btnStyle


from datetime import datetime


import matplotlib.dates as mdates
from datetime import datetime, timedelta

def get_daily_readings(meter_id, period="7d"):
    now = datetime.now()
    if period == "24h":
        cutoff = now - timedelta(hours=24)
    elif period == "30d":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = now - timedelta(days=7)

   
    params = (meter_id, cutoff.strftime("%Y-%m-%d %H:%M:%S"))

    rows = query_readings(params)

    dates = [datetime.strptime(f"{r[0]} {r[1]}", "%Y-%m-%d %H:%M:%S") for r in rows]
    values = [r[2] for r in rows]

    return dates, values

def create_graphical_chart(self, meter_ids, period="7d"):

    lang = self.current_language
    fig = Figure(figsize=(14, 7))
    ax = fig.add_subplot(111)
    colors = ['#007acc', '#28a745', '#dc3545', '#fd7e14']

    points = []  # store points for hover
    for idx, meter_id in enumerate(meter_ids):
        dates, values = get_daily_readings(meter_id, period=period)
        line, = ax.plot(dates, values, marker='o', linestyle='-', color=colors[idx % len(colors)])
        points.append((line, dates, values))

    ax.set_title(translations[lang]["chart_title"], fontsize=18, fontweight='bold')
    ax.set_xlabel(translations[lang]["x_label"], fontsize=14)
    ax.set_ylabel(translations[lang]["y_label"], fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(fontsize=12, loc='upper left', frameon=False)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate(rotation=30)
    ax.set_facecolor('#f9f9f9')
    fig.patch.set_facecolor('#ffffff')

    canvas = FigureCanvas(fig)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    canvas.updateGeometry()

    # Hover tooltip function
    annot = ax.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(line, xdata, ydata, ind):
        annot.xy = (xdata[ind["ind"][0]], ydata[ind["ind"][0]])
        text = f"{line.get_label()}\n{ydata[ind['ind'][0]]:.2f}"
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor(line.get_color())
        annot.get_bbox_patch().set_alpha(0.6)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            for line, xdata, ydata in points:
                cont, ind = line.contains(event)
                if cont:
                    update_annot(line, xdata, ydata, ind)
                    annot.set_visible(True)
                    canvas.draw_idle()
                    return
        if vis:
            annot.set_visible(False)
            canvas.draw_idle()

    canvas.mpl_connect("motion_notify_event", hover)

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

    # Checkbox meter list
    self.meter_list = QListWidget()
    meter_ids_list = get_all_meter_ids()

    for meter_id in meter_ids_list:
        item = QListWidgetItem(meter_id)
        # Enable checkbox
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        # Start unchecked
        item.setCheckState(Qt.Unchecked)
        self.meter_list.addItem(item)

    self.right_layout.addWidget(self.meter_list)

    checked_items = []
    for i in range(self.meter_list.count()):
        item = self.meter_list.item(i)
        if item.checkState() == Qt.Checked:
            checked_items.append(item.text())

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

    if not hasattr(self, 'graphical_layout'):
        self.graphical_layout = QVBoxLayout()
        self.graphical_visualization.setLayout(self.graphical_layout)

        title = QLabel("Graphical Visualization")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        self.graphical_layout.addWidget(title)

    # Remove old chart if exists
    if hasattr(self, 'graphical_chart') and self.graphical_chart:
        self.graphical_layout.removeWidget(self.graphical_chart)
        self.graphical_chart.setParent(None)

    # ✅ Now using checkboxes instead of selectedItems()
    selected_meter_ids = []
    for i in range(self.meter_list.count()):
        item = self.meter_list.item(i)
        if item.checkState() == Qt.Checked:
            selected_meter_ids.append(item.text())

    range_text = self.date_range_select.currentText()
    if range_text == "Last 24 Hours":
        date_limit = 1   # meaning 1 day
    elif range_text == "Last 7 Days":
        date_limit = 7
    elif range_text == "Last 30 Days":
        date_limit = 30
    else:
        date_limit = None

    # Create and add chart
    self.graphical_chart = create_graphical_chart(self, selected_meter_ids, date_limit)
    self.graphical_layout.addWidget(self.graphical_chart)

    # Create status table if it doesn't exist yet
    # if not hasattr(self, 'status_table'):
    #     self.status_table = create_status_table(self, selected_meter_ids)
    #     self.graphical_layout.addWidget(self.status_table)
    # else:
    #     # Just update existing table
    #     update_status_table(self.status_table, selected_meter_ids)

def get_meter_status(meter_id): #will probably be deleted soon
    readings = get_all_readings_id(meter_id)
    if not readings:
        return "Inactive"

    # Last reading date
    last_date_str = readings[-1][0]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    days_diff = (datetime.now() - last_date).days

    if days_diff <= 1:
        return "Active"
    elif days_diff <= 7:
        return "Idle"
    else:
        return "Inactive"


# def create_status_table(self, meter_ids):
#     table = QTableWidget()
#     table.setColumnCount(2)
#     table.setHorizontalHeaderLabels(["Meter ID", "Status"])
#     table.setRowCount(len(meter_ids))

#     for row, meter_id in enumerate(meter_ids):
#         table.setItem(row, 0, QTableWidgetItem(meter_id))
#         status = get_meter_status(meter_id)
#         status_item = QTableWidgetItem(status)

#         # Optional: color coding
#         if status == "Active":
#             status_item.setForeground(Qt.green)
#         elif status == "Idle":
#             status_item.setForeground(Qt.darkYellow)
#         else:
#             status_item.setForeground(Qt.red)

#         table.setItem(row, 1, status_item)

#     table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#     return table


def update_status_table(table, meter_ids):
    table.setRowCount(len(meter_ids))
    for row, meter_id in enumerate(meter_ids):
        table.setItem(row, 0, QTableWidgetItem(meter_id))
        status = get_meter_status(meter_id)
        status_item = QTableWidgetItem(status)

        if status == "Active":
            status_item.setForeground(Qt.green)
        elif status == "Idle":
            status_item.setForeground(Qt.darkYellow)
        else:
            status_item.setForeground(Qt.red)

        table.setItem(row, 1, status_item)


def on_tab_changed(self, index):
    tab_text = self.tabs.tabText(index)
    print(f"Switched to tab: {tab_text}")

    if tab_text == "Graphical Visualization":
        # Initialize panel if not already
        if not hasattr(self, 'meter_list'):
            self.setup_right_panel_for_GV()

        setup_graphical_visualization_tab(self)
