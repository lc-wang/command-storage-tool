import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

# File to store commands
COMMANDS_FILE = "commands.json"

def load_commands():
    """Load commands from the JSON file."""
    if not os.path.exists(COMMANDS_FILE):
        return {}
    with open(COMMANDS_FILE, "r") as file:
        return json.load(file)

def save_commands(commands):
    """Save commands to the JSON file."""
    with open(COMMANDS_FILE, "w") as file:
        json.dump(commands, file, indent=4)

class CommandToolbox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Linux Commands Toolbox")
        self.geometry("500x400")
        self.commands = load_commands()

        self.create_widgets()

    def create_widgets(self):
        tk.Button(self, text="Add Command", command=self.add_command).pack(pady=10)
        tk.Button(self, text="View Commands", command=self.view_commands).pack(pady=10)
        tk.Button(self, text="Delete Command", command=self.delete_command).pack(pady=10)
        tk.Button(self, text="Execute Command", command=self.execute_command).pack(pady=10)
        tk.Button(self, text="Exit", command=self.quit).pack(pady=10)

    def add_command(self):
        name = simpledialog.askstring("Add Command", "Enter a name for the command:").strip()
        if not name:
            return
        if name in self.commands:
            messagebox.showerror("Error", "A command with this name already exists.")
            return
        command = simpledialog.askstring("Add Command", "Enter the Linux command:").strip()
        description = simpledialog.askstring("Add Command", "Enter a description (optional):").strip()
        self.commands[name] = {"command": command, "description": description}
        save_commands(self.commands)
        messagebox.showinfo("Success", f"Command '{name}' added successfully!")

    def view_commands(self):
        if not self.commands:
            messagebox.showinfo("View Commands", "No commands saved yet.")
            return
        commands_str = ""
        for name, details in self.commands.items():
            commands_str += f"\nName: {name}\nCommand: {details['command']}\nDescription: {details.get('description', 'No description')}\n"
        messagebox.showinfo("View Commands", commands_str)

    def delete_command(self):
        name = simpledialog.askstring("Delete Command", "Enter the name of the command to delete:").strip()
        if not name:
            return
        if name in self.commands:
            del self.commands[name]
            save_commands(self.commands)
            messagebox.showinfo("Success", f"Command '{name}' deleted successfully!")
        else:
            messagebox.showerror("Error", "No command found with that name.")

    def execute_command(self):
        name = simpledialog.askstring("Execute Command", "Enter the name of the command to execute:").strip()
        if not name:
            return
        if name in self.commands:
            os.system(self.commands[name]["command"])
        else:
            messagebox.showerror("Error", "No command found with that name.")

if __name__ == "__main__":
    app = CommandToolbox()
    app.mainloop()