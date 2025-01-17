import tkinter as tk
from tkinter import messagebox

def show_message(title, message, type="info"):
    if type == "info":
        messagebox.showinfo(title, message)
    elif type == "error":
        messagebox.showerror(title, message)
    elif type == "warning":
        messagebox.showwarning(title, message)