import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
from command_utils import load_commands, save_commands  # Import the utility functions
import subprocess
import json
import threading
import time  # Import the time module

class CommandToolbox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Linux Commands Toolbox")
        self.geometry("800x800")  # Adjust height to accommodate more widgets
        self.commands = load_commands()
        self.categories = self.get_categories()

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
        self.command_listbox.bind("<<ListboxSelect>>", self.display_selected_command_result)
        self.command_listbox.bind("<Double-Button-1>", self.modify_command_window)

        tk.Button(self.main_frame, text="Add Command", command=self.add_command_window).pack(pady=10)
        tk.Button(self.main_frame, text="Delete Command", command=self.delete_command).pack(pady=10)
        tk.Button(self.main_frame, text="Execute Command", command=self.start_command_thread).pack(pady=10)  # Bind to start_command_thread
        tk.Button(self.main_frame, text="Show Progress", command=self.show_progress_window).pack(pady=10)
        tk.Button(self.main_frame, text="Exit", command=self.quit).pack(pady=10)

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

    def update_category_listbox(self, event=None):
        self.category_listbox.delete(0, tk.END)
        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

    def update_command_listbox(self, event=None):
        selected_category = self.category_listbox.get(tk.ACTIVE)
        if not selected_category:
            return
        self.command_listbox.delete(0, tk.END)
        
        for name, details in self.commands.items():
            if details.get('category', 'Uncategorized') == selected_category:
                command_info = f"Name: {name}, Command: {details['command']}, Description: {details.get('description', 'No description')}"
                self.command_listbox.insert(tk.END, command_info)
        
        # Bind the event to display the command result on selection
        self.command_listbox.bind("<<ListboxSelect>>", self.display_selected_command_result)

    def display_selected_command_result(self, event):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        # This method will now only select the command without executing it

    def display_command_result(self, name):
        details = self.commands.get(name)
        if not details:
            messagebox.showerror("Error", f"No command found with the name '{name}'.")
            return
        command = details["command"]
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Executing command: {command}\n")
        self.output_text.config(state=tk.DISABLED)
        threading.Thread(target=self.run_command, args=(name, command, self.output_text)).start()

    def run_command(self, name, command, output_text):
        # Use default values if 'count' or 'interval' keys are missing
        count = self.commands[name].get("count", 1)
        interval = self.commands[name].get("interval", 0)

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
            
            # Use the after method to update the GUI from the main thread
            self.after(0, self.update_output_text, f"Execution {i+1}/{count}:\n{output}", output_text)
            
            # Update progress info
            self.progress_info[name]['progress'] = i + 1
            self.progress_info[name]['output'].append(output)
            
            time.sleep(interval)

        # Final update to ensure progress is set to max
        self.progress_info[name]['progress'] = count

    def update_output_text(self, output, output_text):
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, f"{output}\n")
        output_text.config(state=tk.DISABLED)

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
        self.add_command_frame.geometry("300x400")  # Adjust height to accommodate new fields

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
            "interval": int(interval) if interval else 0,
            "count": int(count) if count else 1
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
            "interval": int(interval) if interval else 0,
            "count": int(count) if count else 1
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

    def start_command_thread(self):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            messagebox.showerror("Error", "Please select a command to execute.")
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        if name in self.commands:
            # Start the command execution in a separate thread
            threading.Thread(target=self.execute_command, args=(name,)).start()
        else:
            messagebox.showerror("Error", "No command found with that name.")

    def execute_command(self, name):
        if name in self.commands:
            command = self.commands[name]["command"]
            interval = self.commands[name].get("interval", 0)
            count = self.commands[name].get("count", 1)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)  # Clear the output_text widget before displaying new result
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
            self.output_text.config(state=tk.DISABLED)

            # Final update to ensure progress is set to max
            self.progress_info[name]['progress'] = count
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