import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk  # Import the ttk module for Combobox
from command_utils import load_commands, save_commands  # Import the utility functions
import subprocess
import time
import json

class CommandToolbox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Linux Commands Toolbox")
        self.geometry("800x600")  # Adjusted height to accommodate output frame
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
        tk.Button(self.sidebar_frame, text="Export Config", command=self.export_config).pack(pady=10)  # Export button
        tk.Button(self.sidebar_frame, text="Import Config", command=self.import_config).pack(pady=10)  # Import button

        self.command_listbox = tk.Listbox(self.main_frame, width=80)
        self.command_listbox.pack(pady=10)
        self.command_listbox.bind("<Double-Button-1>", self.modify_command_window)

        tk.Button(self.main_frame, text="Add Command", command=self.add_command_window).pack(pady=10)
        tk.Button(self.main_frame, text="Delete Command", command=self.delete_command).pack(pady=10)
        tk.Button(self.main_frame, text="Execute Command", command=self.execute_command).pack(pady=10)
        tk.Button(self.main_frame, text="Exit", command=self.quit).pack(pady=10)

        # Add a Text widget to display command output
        self.output_text = tk.Text(self.main_frame, height=10, wrap='word')
        self.output_text.pack(pady=10, fill='both', expand=True)
        self.output_text.config(state=tk.DISABLED)

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
        confirm = messagebox.askyesno("Delete Category", f"Are you sure you want to delete the category '{selected_category}' and move its commands to 'Uncategorized'?")
        if not confirm:
            return

        # Move commands in the selected category to 'Uncategorized'
        for name, details in self.commands.items():
            if details.get('category', 'Uncategorized') == selected_category:
                self.commands[name]['category'] = 'Uncategorized'
        
        # Remove the category
        self.categories.remove(selected_category)
        save_commands(self.commands)
        self.update_category_listbox()
        self.update_command_listbox()
        messagebox.showinfo("Success", f"Category '{selected_category}' deleted successfully and its commands moved to 'Uncategorized'!")

    def add_command_window(self):
        self.add_command_frame = tk.Toplevel(self)
        self.add_command_frame.title("Add Command")
        self.add_command_frame.geometry("300x400")  # Adjusted height to accommodate new fields

        tk.Label(self.add_command_frame, text="Name:").pack(pady=5)
        self.command_name_entry = tk.Entry(self.add_command_frame)
        self.command_name_entry.pack(pady=5)

        tk.Label(self.add_command_frame, text="Command:").pack(pady=5)
        self.command_entry = tk.Entry(self.add_command_frame)
        self.command_entry.pack(pady=5)

        tk.Label(self.add_command_frame, text="Description:").pack(pady=5)
        self.command_description_entry = tk.Entry(self.add_command_frame)
        self.command_description_entry.pack(pady=5)

        tk.Label(self.add_command_frame, text="Category:").pack(pady=5)
        self.command_category_combobox = ttk.Combobox(self.add_command_frame, values=self.categories)
        self.command_category_combobox.pack(pady=5)

        tk.Label(self.add_command_frame, text="Interval (seconds):").pack(pady=5)
        self.command_interval_entry = tk.Entry(self.add_command_frame)
        self.command_interval_entry.pack(pady=5)

        tk.Label(self.add_command_frame, text="Count:").pack(pady=5)
        self.command_count_entry = tk.Entry(self.add_command_frame)
        self.command_count_entry.pack(pady=5)

        tk.Button(self.add_command_frame, text="Save", command=self.add_command).pack(pady=5)
        tk.Button(self.add_command_frame, text="Cancel", command=self.add_command_frame.destroy).pack(pady=5)

    def add_command(self):
        name = self.command_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Command name cannot be empty.")
            return
        if name in self.commands:
            messagebox.showerror("Error", "A command with this name already exists.")
            return
        command = self.command_entry.get().strip()
        description = self.command_description_entry.get().strip()
        category = self.command_category_combobox.get().strip()
        if not category:
            category = 'Uncategorized'
        interval = self.command_interval_entry.get().strip()
        count = self.command_count_entry.get().strip()
        if not interval.isdigit() or not count.isdigit():
            messagebox.showerror("Error", "Interval and Count must be valid numbers.")
            return
        self.commands[name] = {
            "command": command, 
            "description": description, 
            "category": category,
            "interval": int(interval),
            "count": int(count)
        }
        save_commands(self.commands)
        self.update_command_listbox()
        self.add_command_frame.destroy()
        messagebox.showinfo("Success", f"Command '{name}' added successfully!")

    def modify_command_window(self, event):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        if name in self.commands:
            details = self.commands[name]
            self.modify_command_frame = tk.Toplevel(self)
            self.modify_command_frame.title("Modify Command")
            self.modify_command_frame.geometry("300x400")

            tk.Label(self.modify_command_frame, text="Name:").pack(pady=5)
            self.modify_command_name_entry = tk.Entry(self.modify_command_frame)
            self.modify_command_name_entry.pack(pady=5)
            self.modify_command_name_entry.insert(0, name)
            self.modify_command_name_entry.config(state='disabled')

            tk.Label(self.modify_command_frame, text="Command:").pack(pady=5)
            self.modify_command_entry = tk.Entry(self.modify_command_frame)
            self.modify_command_entry.pack(pady=5)
            self.modify_command_entry.insert(0, details['command'])

            tk.Label(self.modify_command_frame, text="Description:").pack(pady=5)
            self.modify_command_description_entry = tk.Entry(self.modify_command_frame)
            self.modify_command_description_entry.pack(pady=5)
            self.modify_command_description_entry.insert(0, details.get('description', ''))

            tk.Label(self.modify_command_frame, text="Category:").pack(pady=5)
            self.modify_command_category_combobox = ttk.Combobox(self.modify_command_frame, values=self.categories)
            self.modify_command_category_combobox.pack(pady=5)
            self.modify_command_category_combobox.set(details.get('category', 'Uncategorized'))

            tk.Label(self.modify_command_frame, text="Interval (seconds):").pack(pady=5)
            self.modify_command_interval_entry = tk.Entry(self.modify_command_frame)
            self.modify_command_interval_entry.pack(pady=5)
            self.modify_command_interval_entry.insert(0, details.get('interval', 0))

            tk.Label(self.modify_command_frame, text="Count:").pack(pady=5)
            self.modify_command_count_entry = tk.Entry(self.modify_command_frame)
            self.modify_command_count_entry.pack(pady=5)
            self.modify_command_count_entry.insert(0, details.get('count', 1))

            tk.Button(self.modify_command_frame, text="Save", command=lambda: self.modify_command(name)).pack(pady=5)
            tk.Button(self.modify_command_frame, text="Cancel", command=self.modify_command_frame.destroy).pack(pady=5)

    def modify_command(self, original_name):
        command = self.modify_command_entry.get().strip()
        description = self.modify_command_description_entry.get().strip()
        category = self.modify_command_category_combobox.get().strip()
        if not category:
            category = 'Uncategorized'
        interval = self.modify_command_interval_entry.get().strip()
        count = self.modify_command_count_entry.get().strip()
        if not interval.isdigit() or not count.isdigit():
            messagebox.showerror("Error", "Interval and Count must be valid numbers.")
            return
        self.commands[original_name] = {
            "command": command, 
            "description": description, 
            "category": category,
            "interval": int(interval),
            "count": int(count)
        }
        save_commands(self.commands)
        self.update_command_listbox()
        self.modify_command_frame.destroy()
        messagebox.showinfo("Success", f"Command '{original_name}' modified successfully!")

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
            command = self.commands[name]["command"]
            interval = self.commands[name]["interval"]
            count = self.commands[name]["count"]
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            for i in range(count):
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output = result.stdout if result.stdout else result.stderr
                except Exception as e:
                    output = str(e)
                
                # Display the output in the Text widget immediately
                self.output_text.insert(tk.END, f"Execution {i+1}/{count}:\n{output}\n")
                self.output_text.see(tk.END)
                self.update()
                time.sleep(interval)
            self.output_text.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", "No command found with that name.")

    def export_config(self):
        # Open a file dialog to choose the save location
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            # Write the current command configuration to the chosen file
            try:
                with open(file_path, "w") as file:
                    json.dump(self.commands, file, indent=4)
                messagebox.showinfo("Success", f"Configuration exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export configuration: {e}")

    def import_config(self):
        # Open a file dialog to choose the JSON file
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            # Load the command configuration from the chosen file
            try:
                with open(file_path, "r") as file:
                    imported_commands = json.load(file)
                self.commands.update(imported_commands)
                self.categories = self.get_categories()
                self.update_category_listbox()
                self.update_command_listbox()
                save_commands(self.commands)
                messagebox.showinfo("Success", f"Configuration imported from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import configuration: {e}")

if __name__ == "__main__":
    app = CommandToolbox()
    app.mainloop()