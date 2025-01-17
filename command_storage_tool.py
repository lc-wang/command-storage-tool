import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk
from command_utils import load_commands, save_commands, get_categories, search_commands
import subprocess
import threading
import time
import json
from gui_utils import show_message

class CommandStorageTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Command Storage Tool")
        self.geometry("800x800")
        self.commands = load_commands()
        self.categories = get_categories(self.commands)
        
        # Dictionary to store progress information
        self.progress_info = {}

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
        tk.Button(self.sidebar_frame, text="Export Config", command=self.export_config).pack(pady=10)
        tk.Button(self.sidebar_frame, text="Import Config", command=self.import_config).pack(pady=10)

        self.command_listbox = tk.Listbox(self.main_frame, width=80)
        self.command_listbox.pack(pady=10)
        self.command_listbox.bind("<Double-Button-1>", self.modify_command_window)

        # Add search entry and button
        self.search_entry = tk.Entry(self.main_frame)
        self.search_entry.pack(pady=5)
        tk.Button(self.main_frame, text="Search", command=self.perform_search).pack(pady=5)

        tk.Button(self.main_frame, text="Add Command", command=self.add_command_window).pack(pady=10)
        tk.Button(self.main_frame, text="Delete Command", command=self.delete_command).pack(pady=10)
        tk.Button(self.main_frame, text="Execute Command", command=self.start_command_thread).pack(pady=10)
        tk.Button(self.main_frame, text="Show Progress", command=self.show_progress_window).pack(pady=10)
        tk.Button(self.main_frame, text="Clear Output", command=self.clear_output).pack(pady=10)
        tk.Button(self.main_frame, text="Exit", command=self.quit).pack(pady=10)

        self.output_text = tk.Text(self.main_frame, height=10, wrap='word')
        self.output_text.pack(pady=10, fill='both', expand=True)
        self.output_text.config(state=tk.DISABLED)

        self.update_category_listbox()

    # Define the show_progress_window method
    def show_progress_window(self):
        # Create a new window to display progress bars
        self.progress_window = tk.Toplevel(self)
        self.progress_window.title("Command Progress")
        self.progress_window.geometry("600x400")

        # Create a frame to hold all progress bars
        self.progress_frame = tk.Frame(self.progress_window)
        self.progress_frame.pack(pady=10, fill='both', expand=True)

        # Display progress bars for all commands
        for name, info in self.progress_info.items():
            # Create a frame for the progress bar and percentage label
            progress_frame = tk.Frame(self.progress_frame)
            progress_frame.pack(pady=5, fill='x')

            # Display command name in bold
            command_label = tk.Label(progress_frame, text=name, font=("Helvetica", 12, "bold"))
            command_label.pack(anchor='w')

            progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate', length=400)
            progress_bar.pack(side='left', padx=10, fill='x', expand=True)
            percentage_label = tk.Label(progress_frame, text="0%")
            percentage_label.pack(side='right')

            # Initialize progress bar
            progress_bar['maximum'] = info['max']
            progress_bar['value'] = info['progress']
            percentage = int((info['progress'] / info['max']) * 100)
            percentage_label.config(text=f"{percentage}%")

            # Store the progress bar and label in the progress info for updates
            info['progress_bar'] = progress_bar
            info['percentage_label'] = percentage_label

        # Periodically update the progress window
        self.update_progress_window()

    def update_progress_window(self):
        for name, info in self.progress_info.items():
            progress_bar = info['progress_bar']
            percentage_label = info['percentage_label']
            progress_bar['value'] = info['progress']
            percentage = int((info['progress'] / info['max']) * 100)
            percentage_label.config(text=f"{percentage}%")

        # Schedule next update
        self.progress_window.after(1000, self.update_progress_window)

    def clear_output(self):
        """Clear the content of the output_text widget."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def update_category_listbox(self, event=None):
        self.category_listbox.delete(0, tk.END)
        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

    def update_command_listbox(self, event=None, commands=None):
        self.command_listbox.delete(0, tk.END)
        if commands is None:
            selected_category = self.category_listbox.get(tk.ACTIVE)
            if not selected_category:
                return
            for name, details in self.commands.items():
                if details.get('category', 'Uncategorized') == selected_category:
                    command_info = f"Name: {name}, Command: {details['command']}, Description: {details.get('description', 'No description')}"
                    self.command_listbox.insert(tk.END, command_info)
        else:
            for name, details in commands.items():
                command_info = f"Name: {name}, Command: {details['command']}, Description: {details.get('description', 'No description')}"
                self.command_listbox.insert(tk.END, command_info)

    def perform_search(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            show_message("Error", "Search query cannot be empty.", "error")
            return

        search_results = search_commands(self.commands, query)
        if not search_results:
            show_message("Search Results", "No commands found matching the query.")
        else:
            self.update_command_listbox(commands=search_results)

    def add_category(self):
        category = simpledialog.askstring("Add Category", "Enter a name for the category:").strip()
        if not category:
            return
        if category in self.categories:
            show_message("Error", "A category with this name already exists.", "error")
            return
        self.categories.append(category)
        self.update_category_listbox()
        show_message("Success", f"Category '{category}' added successfully!")

    def delete_category(self):
        selected_category = self.category_listbox.get(tk.ACTIVE)
        if not selected_category:
            return
        if selected_category == 'Uncategorized':
            show_message("Error", "Cannot delete the 'Uncategorized' category.", "error")
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
        show_message("Success", f"Category '{selected_category}' deleted successfully and its commands moved to 'Uncategorized'!")

    def add_command_window(self):
        self.add_command_frame = tk.Toplevel(self)
        self.add_command_frame.title("Add Command")
        self.add_command_frame.geometry("300x400")

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
            show_message("Error", "Command name cannot be empty.", "error")
            return
        if name in self.commands:
            show_message("Error", "A command with this name already exists.", "error")
            return
        command = self.command_entry.get().strip()
        description = self.command_description_entry.get().strip()
        category = self.command_category_combobox.get().strip()
        if not category:
            category = 'Uncategorized'
        interval = self.command_interval_entry.get().strip()
        count = self.command_count_entry.get().strip()
        if not interval.isdigit() or not count.isdigit():
            show_message("Error", "Interval and Count must be valid numbers.", "error")
            return
        self.commands[name] = {
            "command": command, 
            "description": description, 
            "category": category,
            "interval": int(interval) if interval else 0,
            "count": int(count) if count else 1
        }
        save_commands(self.commands)
        self.update_command_listbox()
        self.add_command_frame.destroy()
        show_message("Success", f"Command '{name}' added successfully!")

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
            show_message("Error", "Interval and Count must be valid numbers.", "error")
            return
        self.commands[original_name] = {
            "command": command, 
            "description": description, 
            "category": category,
            "interval": int(interval) if interval else 0,
            "count": int(count) if count else 1
        }
        save_commands(self.commands)
        self.update_command_listbox()
        self.modify_command_frame.destroy()
        show_message("Success", f"Command '{original_name}' modified successfully!")

    def delete_command(self):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        if name in self.commands:
            del self.commands[name]
            save_commands(self.commands)
            self.update_command_listbox()
            show_message("Success", f"Command '{name}' deleted successfully!")
        else:
            show_message("Error", "No command found with that name.", "error")

    def start_command_thread(self):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            show_message("Error", "Please select a command to execute.", "error")
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        if name in self.commands:
            # Start the command execution in a separate thread
            threading.Thread(target=self.execute_command, args=(name,)).start()
        else:
            show_message("Error", "No command found with that name.", "error")

    def execute_command(self, name):
        if name in self.commands:
            command = self.commands[name]["command"]
            interval = self.commands[name].get("interval", 0)
            count = self.commands[name].get("count", 1)
            self.output_text.config(state=tk.NORMAL)
            # Initialize progress info for the command
            self.progress_info[name] = {
                'progress': 0,
                'max': count,
                'output': []
            }
            for i in range(count):
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output = result.stdout if result.stdout else result.stderr
                except Exception as e:
                    output = str(e)
                
                # Display the output in the Text widget immediately
                self.output_text.insert(tk.END, f"Execution {i+1}/{count}:\n{output}\n")
                self.output_text.see(tk.END)

                # Update progress info
                self.progress_info[name]['progress'] = i + 1
                self.progress_info[name]['output'].append(output)
                
                time.sleep(interval)

            # Final update to ensure progress is set to max
            self.progress_info[name]['progress'] = count
        else:
            show_message("Error", "No command found with that name.", "error")

    def export_config(self):
        # Open a file dialog to choose the save location
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            # Write the current command configuration to the chosen file
            try:
                with open(file_path, "w") as file:
                    json.dump(self.commands, file, indent=4)
                show_message("Success", f"Configuration exported to {file_path}")
            except Exception as e:
                show_message("Error", f"Failed to export configuration: {e}", "error")

    def import_config(self):
        # Open a file dialog to choose the JSON file
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            # Load the command configuration from the chosen file
            try:
                with open(file_path, "r") as file:
                    imported_commands = json.load(file)
                self.commands.update(imported_commands)
                self.categories = get_categories(self.commands)
                self.update_category_listbox()
                self.update_command_listbox()
                save_commands(self.commands)
                show_message("Success", f"Configuration imported from {file_path}")
            except Exception as e:
                show_message("Error", f"Failed to import configuration: {e}", "error")

if __name__ == "__main__":
    app = CommandStorageTool()
    app.mainloop()