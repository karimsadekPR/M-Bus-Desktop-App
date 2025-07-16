import tkinter as tk
from database import get_latest_reading

def launch_gui():
    root = tk.Tk()
    root.title("Water Meter")

    label = tk.Label(root, text="Click to load latest reading")
    label.pack(pady=10)

    def update_label():
        row = get_latest_reading()
        if row:
            label.config(text=f"{row[2]} m³ at {row[1]}")
        else:
            label.config(text="No data found")

    btn = tk.Button(root, text="Load Reading", command=update_label)
    btn.pack(pady=5)

    root.mainloop()
