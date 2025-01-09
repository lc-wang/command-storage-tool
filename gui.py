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
        self.geometry("600x400")
        self.commands = load_commands()

        self.create_widgets()

    def create_widgets(self):
        tk.Button(self, text="Add Command", command=self.add_command).pack(pady=10)
        tk.Button(self, text="Delete Command", command=self.delete_command).pack(pady=10)
        tk.Button(self, text="Execute Command", command=self.execute_command).pack(pady=10)
        tk.Button(self, text="Exit", command=self.quit).pack(pady=10)
        self.command_listbox = tk.Listbox(self, width=80)
        self.command_listbox.pack(pady=10)
        self.update_command_listbox()

    def update_command_listbox(self):
        self.command_listbox.delete(0, tk.END)
        for name, details in self.commands.items():
            self.command_listbox.insert(tk.END, f"Name: {name}, Command: {details['command']}, Description: {details.get('description', 'No description')}")

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
        self.update_command_listbox()
        messagebox.showinfo("Success", f"Command '{name}' added successfully!")

    def delete_command(self):
        name = simpledialog.askstring("Delete Command", "Enter the name of the command to delete:").strip()
        if not name:
            return
        if name in self.commands:
            del self.commands[name]
            save_commands(self.commands)
            self.update_command_listbox()
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