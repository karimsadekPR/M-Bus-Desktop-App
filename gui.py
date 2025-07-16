import tkinter as tk
from tkinter import font
from database import get_latest_reading

def launch_gui():
    root = tk.Tk()
    root.title("Water Meter GUI")
    root.geometry("300x150")
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
        row = get_latest_reading()
        if row:
            label.config(text=f"{row[2]} m³ at {row[1]}")
        else:
            label.config(text="No data found")

    # Load button
    btn = tk.Button(root, text="Load Reading", font=button_font, command=update_label, bg="#4a90e2", fg="white", activebackground="#357ABD", activeforeground="white", relief="flat", padx=10, pady=5)
    btn.pack(pady=(10, 15))

    root.mainloop()
