import tkinter as tk
from tkinter import filedialog

def open_file():
    filepath = filedialog.askopenfilename()
    print(f"Đã mở tệp: {filepath}")

root = tk.Tk()
button = tk.Button(root, text="Mở tệp", command=open_file)
button.pack()

root.mainloop()