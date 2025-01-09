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
        self.geometry("800x400")
        self.commands = load_commands()
        self.categories = self.get_categories()

        self.create_widgets()

    def create_widgets(self):
        self.sidebar_frame = tk.Frame(self, width=200, bg='lightgrey')
        self.sidebar_frame.pack(expand=False, fill='y', side='left', anchor='nw')

        self.main_frame = tk.Frame(self, width=600)
        self.main_frame.pack(expand=True, fill='both', side='right')

        self.category_listbox = tk.Listbox(self.sidebar_frame, width=30)
        self.category_listbox.pack(pady=10, padx=10)
        self.category_listbox.bind("<<ListboxSelect>>", self.update_command_listbox)

        tk.Button(self.sidebar_frame, text="Add Category", command=self.add_category).pack(pady=10)
        tk.Button(self.sidebar_frame, text="Delete Category", command=self.delete_category).pack(pady=10)

        self.command_listbox = tk.Listbox(self.main_frame, width=80)
        self.command_listbox.pack(pady=10)

        tk.Button(self.main_frame, text="Add Command", command=self.add_command).pack(pady=10)
        tk.Button(self.main_frame, text="Delete Command", command=self.delete_command).pack(pady=10)
        tk.Button(self.main_frame, text="Execute Command", command=self.execute_command).pack(pady=10)
        tk.Button(self.main_frame, text="Exit", command=self.quit).pack(pady=10)

        self.update_category_listbox()

    def get_categories(self):
        """Get unique categories from commands."""
        categories = set()
        for details in self.commands.values():
            categories.add(details.get('category', 'Uncategorized'))
        return list(categories)

    def update_category_listbox(self):
        self.category_listbox.delete(0, tk.END)
        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

    def update_command_listbox(self, event=None):
        selected_category = self.category_listbox.get(tk.ACTIVE)
        self.command_listbox.delete(0, tk.END)
        for name, details in self.commands.items():
            if details.get('category', 'Uncategorized') == selected_category:
                self.command_listbox.insert(tk.END, f"Name: {name}, Command: {details['command']}, Description: {details.get('description', 'No description')}")

    def add_category(self):
        category = simpledialog.askstring("Add Category", "Enter a name for the category:").strip()
        if not category:
            return
        if category in self.categories:
            messagebox.showerror("Error", "A category with this name already exists.")
            return
        self.categories.append(category)
        self.update_category_listbox()
        messagebox.showinfo("Success", f"Category '{category}' added successfully!")

    def delete_category(self):
        selected_category = self.category_listbox.get(tk.ACTIVE)
        if not selected_category:
            return
        if selected_category == 'Uncategorized':
            messagebox.showerror("Error", "Cannot delete the 'Uncategorized' category.")
            return
        confirm = messagebox.askyesno("Delete Category", f"Are you sure you want to delete the category '{selected_category}' and all its commands?")
        if not confirm:
            return
        # Remove all commands in the selected category
        commands_to_delete = [name for name, details in self.commands.items() if details.get('category', 'Uncategorized') == selected_category]
        for name in commands_to_delete:
            del self.commands[name]
        # Remove the category
        self.categories.remove(selected_category)
        save_commands(self.commands)
        self.update_category_listbox()
        self.update_command_listbox()
        messagebox.showinfo("Success", f"Category '{selected_category}' and all its commands deleted successfully!")

    def add_command(self):
        name = simpledialog.askstring("Add Command", "Enter a name for the command:").strip()
        if not name:
            return
        if name in self.commands:
            messagebox.showerror("Error", "A command with this name already exists.")
            return
        command = simpledialog.askstring("Add Command", "Enter the Linux command:").strip()
        description = simpledialog.askstring("Add Command", "Enter a description (optional):").strip()
        category = simpledialog.askstring("Add Command", "Enter a category:").strip()
        if not category:
            category = 'Uncategorized'
        self.commands[name] = {"command": command, "description": description, "category": category}
        save_commands(self.commands)
        self.update_command_listbox()
        messagebox.showinfo("Success", f"Command '{name}' added successfully!")

    def delete_command(self):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        if name in self.commands:
            del self.commands[name]
            save_commands(self.commands)
            self.update_command_listbox()
            messagebox.showinfo("Success", f"Command '{name}' deleted successfully!")
        else:
            messagebox.showerror("Error", "No command found with that name.")

    def execute_command(self):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        if name in self.commands:
            os.system(self.commands[name]["command"])
        else:
            messagebox.showerror("Error", "No command found with that name.")

if __name__ == "__main__":
    app = CommandToolbox()
    app.mainloop()