
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QLabel, QHeaderView, QPushButton, QComboBox,
    QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QLineEdit,
    QTabWidget, QFileDialog, QSizePolicy, QAbstractButton
)
from PyQt5.QtCore import Qt
from database import get_last_7_days

# ⬇️ New matplotlib imports for embedding charts
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def create_graphical_chart(self):
            last_7_days = get_last_7_days()
            print(last_7_days)

            days = [row[0] for row in last_7_days]
            usage = [row[1] for row in last_7_days]

            #print(last_7_days, days, usage)

            fig = Figure(figsize=(12, 6))
            ax = fig.add_subplot(111)

            ax.plot(days, usage, marker='o', linestyle='-', color='blue', label='Usage (m³)')

            # Add value labels on the points
            for i, value in enumerate(usage):
                ax.text(days[i], value, f"{value:.2f}", fontsize=9, ha='center', va='bottom')

            ax.set_title("Water Usage Over Last 7 Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Usage (m³)")

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

        self.graphical_chart = create_graphical_chart(self)
        self.graphical_layout.addWidget(self.graphical_chart)