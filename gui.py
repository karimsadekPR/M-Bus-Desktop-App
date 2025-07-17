import tkinter as tk
from tkinter import font
from database import get_all_readings, save_reading, save_meter
from mbus_reader import read_meter
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap as ttk

def launch_gui():
    root = ttk.Window(themename="flatly")  # Start with a themed window
    root.title("Water Meter GUI")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = int(screen_width * 0.7)
    height = int(screen_height * 0.7)
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.configure(bg="#ffffff")

    # Fonts
    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    button_font = font.Font(family="Helvetica", size=12, weight="bold")

    # Title
    title_label = ttk.Label(root, text="Water Meter Readings", font=title_font, bootstyle="primary")
    title_label.pack(pady=(20, 15))

    # Treeview inside a frame for rounded look
    tree_frame = ttk.Frame(root, bootstyle="secondary", padding=10)
    tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

    columns = ("meter_id", "timestamp", "usage")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", bootstyle="info")

    tree.heading("meter_id", text="Meter ID")
    tree.heading("timestamp", text="Timestamp")
    tree.heading("usage", text="Usage (m³)")

    for col in columns:
        tree.column(col, anchor="center", width=150)

    tree.pack(fill="both", expand=True)

    # Table font styles and striped rows
    style = Style()
    style.configure("Treeview", font=("Helvetica", 12), rowheight=28)
    style.configure("Treeview.Heading", font=("Helvetica", 13, "bold"))
    style.map("Treeview", background=[("selected", "#4a90e2")])
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
    # Enable striped rows
    style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
    style.configure("Treeview", bordercolor="#d9d9d9", borderwidth=0.5, borderradius=4)
    style.configure("Treeview", relief="flat")
    style.configure("Treeview", highlightthickness=0)
    style.configure("Treeview", padding=5)

    def update_table():
        for row in tree.get_children():
            tree.delete(row)
        readings = get_all_readings()
        if readings:
            for row in readings:
                tree.insert("", tk.END, values=(row[1], row[2], row[3]))

    def read_new_meter():
        data = read_meter(3)
        if data:
            timestamp = data.get("timestamp")
            usage = data.get("value")
            meter_id = data.get('id')
            if timestamp and usage is not None:
                save_meter(meter_id)
                save_reading(meter_id, timestamp, usage)
                update_table()

    def read_all_meters():
        meter_ids = [1, 2, 3]
        for meter_id in meter_ids:
            data = read_meter(meter_id)
            if data:
                timestamp = data.get("timestamp")
                usage = data.get("value")
                meter_id = data.get("id")
                if timestamp and usage is not None:
                    save_meter(meter_id)
                    save_reading(meter_id, timestamp, usage)
        update_table()

    # Button frame
    btn_frame = ttk.Frame(root, bootstyle="light")
    btn_frame.pack(pady=(10, 20))

    btn_load = ttk.Button(btn_frame, text="Load All Readings", bootstyle="primary", command=update_table)
    btn_load.pack(side="left", padx=8, ipadx=10, ipady=5)

    btn_read = ttk.Button(btn_frame, text="Read New Meter", bootstyle="success", command=read_new_meter)
    btn_read.pack(side="left", padx=8, ipadx=10, ipady=5)

    btn_read_all = ttk.Button(btn_frame, text="Read All Meters", bootstyle="warning", command=read_all_meters)
    btn_read_all.pack(side="left", padx=8, ipadx=10, ipady=5)

    root.mainloop()
