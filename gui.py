import tkinter as tk
from tkinter import font
from database import get_all_readings, save_reading
from mbus_reader import read_meter
from config import METER_ADDRESS
def launch_gui():
    root = tk.Tk()
    root.title("Water Meter GUI")
    root.geometry("300x200")
    root.configure(bg="#f0f4f8")

    # Define fonts
    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    label_font = font.Font(family="Helvetica", size=12)
    button_font = font.Font(family="Helvetica", size=12, weight="bold")

    # Title label
    title_label = tk.Label(root, text="Water Meter Reading", font=title_font, bg="#f0f4f8", fg="#333333")
    title_label.pack(pady=(15, 10))

    # Reading label
    label = tk.Label(root, text="Click to load latest reading", font=label_font, bg="#f0f4f8", fg="#555555")
    label.pack(pady=5)

    def update_label():
        readings = get_all_readings()
        if readings:
            text_lines = []
            for row in readings:
                text_lines.append(f"{row[2]} m³ at {row[1]}")
            label.config(text="\n".join(text_lines))
        else:
            label.config(text="No data found")

    def read_new_meter():
        data = read_meter()
        if data:
            timestamp = data.get("timestamp")
            usage = data.get("value")
            if timestamp and usage is not None:
                save_reading(timestamp, usage)
                label.config(text=f"New reading: {usage} m³ at {timestamp}")
            else:
                label.config(text="Invalid data from meter")
        else:
            label.config(text="Failed to read meter")
    def read_all_meters():
        success_count = 0
        for meterId in METER_ADDRESS:
            data = read_meter(meterId)
            if data:
                timestamp = data.get("timestamp")
                usage = data.get("value")
                if timestamp and usage is not None:
                    save_reading(meterId, timestamp, usage)
                    success_count += 1
        label.config(text=f"Read {success_count} meters.")


    # Load button
    btn_load = tk.Button(root, text="Load all Readings", font=button_font, command=update_label, bg="#4a90e2", fg="white", activebackground="#357ABD", activeforeground="white", relief="flat", padx=10, pady=5)
    btn_load.pack(pady=(10, 5))

    # Read new meter button
    btn_read = tk.Button(root, text="Read New Meter", font=button_font, command=read_new_meter, bg="#50C878", fg="white", activebackground="#3AAE5B", activeforeground="white", relief="flat", padx=10, pady=5)
    btn_read.pack(pady=(5, 15))

    btn_read_all = tk.Button(
        root,
        text="Read All Meters",
        font=button_font,
        command=read_all_meters,
        bg="#FFA500",
        fg="white",
        activebackground="#E69500",
        activeforeground="white",
        relief="flat",
        padx=10,
        pady=5
)
    btn_read_all.pack(pady=(5, 15))



    root.mainloop()
    
