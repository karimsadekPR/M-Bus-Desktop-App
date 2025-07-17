import tkinter as tk
from tkinter import font, ttk
from database import get_all_readings, save_reading, save_meter
from mbus_reader import read_meter

def launch_gui():
    root = tk.Tk()
    root.title("Water Meter GUI")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    width = int(screen_width * 0.7)
    height = int(screen_height * 0.7)

    # Center the window on the screen
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    root.geometry(f"{width}x{height}+{x}+{y}")
    root.configure(bg="#f0f4f8")

    # Define fonts
    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    button_font = font.Font(family="Helvetica", size=12, weight="bold")

    # Title label
    title_label = tk.Label(root, text="Water Meter Readings", font=title_font, bg="#f0f4f8", fg="#333333")
    title_label.pack(pady=(15, 10))

    # Table (Treeview)
    columns = ("meter_id", "timestamp", "usage")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.heading("meter_id", text="Meter ID")
    tree.heading("timestamp", text="Timestamp")
    tree.heading("usage", text="Usage (m³)")

    for col in columns:
        tree.column(col, anchor="center", width=150)

    tree.pack(padx=10, pady=10, fill="both", expand=True)

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
        # Optionally: handle/display errors

    def read_all_meters():
        meter_ids = [1, 2, 3]  # Replace with actual IDs
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

    # Buttons
    btn_frame = tk.Frame(root, bg="#f0f4f8")
    btn_frame.pack(pady=(5, 15))

    # Load button
    btn_load = tk.Button(btn_frame, text="Load All Readings", font=button_font, command=update_table,
                        bg="#4a90e2", fg="white", activebackground="#357ABD", activeforeground="white",
                        relief="flat", padx=10, pady=5)
    btn_load.pack(side="left", padx=5)

    # Read new meter button
    btn_read = tk.Button(btn_frame, text="Read New Meter", font=button_font, command=read_new_meter,
                        bg="#50C878", fg="white", activebackground="#3AAE5B", activeforeground="white",
                        relief="flat", padx=10, pady=5)
    btn_read.pack(side="left", padx=5)

    # Read all meters button
    btn_read_all = tk.Button(btn_frame, text="Read All Meters", font=button_font, command=read_all_meters,
                            bg="#FFA500", fg="white", activebackground="#E69500", activeforeground="white",
                            relief="flat", padx=10, pady=5)
    btn_read_all.pack(side="left", padx=5)


    root.mainloop()
