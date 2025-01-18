import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk
from command_utils import load_commands, save_commands, get_categories, search_commands
import subprocess
import threading
import time
import json
import schedule
from gui_utils import show_message
import base64
from bs4 import BeautifulSoup  # Ensure this line is included
import requests

class CommandStorageTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Command Storage Tool")
        self.geometry("1350x600")  # Adjusted window size to better fit widgets
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # Use a modern theme
        self.commands = load_commands()
        self.categories = get_categories(self.commands)
        self.progress_info = {}
        self.command_history = []

        self.create_widgets()
        threading.Thread(target=self.run_schedule, daemon=True).start()

    def create_widgets(self):
        self.create_sidebar()
        self.create_main_frame()
        self.create_search_frame()
        self.update_category_listbox()

    def create_sidebar(self):
        self.sidebar_frame = ttk.Frame(self, padding="10")
        self.sidebar_frame.pack(side='left', fill='y', expand=False)

        self.category_listbox = tk.Listbox(self.sidebar_frame)
        self.category_listbox.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.category_listbox.bind("<<ListboxSelect>>", self.update_command_listbox)

        sidebar_buttons = [("Add Category", self.add_category),
                           ("Delete Category", self.delete_category),
                           ("Export Config", self.export_config),
                           ("Import Config", self.import_config),
                           ("Command History", self.show_history_window)]
        for i, (text, command) in enumerate(sidebar_buttons, 1):
            ttk.Button(self.sidebar_frame, text=text, command=command).grid(row=i, column=0, padx=10, pady=5, sticky='ew')

        self.sidebar_frame.grid_rowconfigure(0, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(side='left', fill='both', expand=True)

        main_buttons = [("Add Command", self.add_command_window),
                        ("Delete Command", self.delete_command),
                        ("Execute Command", self.start_command_thread),
                        ("Show Progress", self.show_progress_window),
                        ("Clear Output", self.clear_output),
                        ("Exit", self.quit),
                        ("Schedule Command", self.schedule_command_window)]
        for i, (text, command) in enumerate(main_buttons, 1):
            ttk.Button(self.main_frame, text=text, command=command).pack(fill='x', padx=10, pady=5)

        self.output_text = tk.Text(self.main_frame, height=10, wrap='word')
        self.output_text.pack(fill='both', padx=10, pady=10, expand=True)
        self.output_text.config(state=tk.DISABLED)

    def create_search_frame(self):
        self.search_frame = ttk.Frame(self, padding="10")
        self.search_frame.pack(side='right', fill='both', expand=True)

        # Online search frame
        self.online_search_frame = ttk.Frame(self.search_frame, padding="10")
        self.online_search_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.online_search_entry = ttk.Entry(self.online_search_frame)
        self.online_search_entry.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        ttk.Button(self.online_search_frame, text="Search Online", command=self.perform_online_search).grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.online_command_listbox = tk.Listbox(self.online_search_frame)
        self.online_command_listbox.grid(row=1, column=0, padx=10, pady=10, sticky='nsew', columnspan=2)

        self.online_search_frame.grid_rowconfigure(1, weight=1)
        self.online_search_frame.grid_columnconfigure(0, weight=1)
        self.online_search_frame.grid_columnconfigure(1, weight=1)

        # Local search frame
        self.local_search_frame = ttk.Frame(self.search_frame, padding="10")
        self.local_search_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.search_entry = ttk.Entry(self.local_search_frame)
        self.search_entry.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        ttk.Button(self.local_search_frame, text="Search Local", command=self.perform_local_search).grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.local_command_listbox = tk.Listbox(self.local_search_frame)
        self.local_command_listbox.grid(row=1, column=0, padx=10, pady=10, sticky='nsew', columnspan=2)

        self.local_search_frame.grid_rowconfigure(1, weight=1)
        self.local_search_frame.grid_columnconfigure(0, weight=1)
        self.local_search_frame.grid_columnconfigure(1, weight=1)

    def show_progress_window(self):
        self.progress_window = tk.Toplevel(self)
        self.progress_window.title("Command Progress")
        self.progress_window.geometry("600x400")

        self.progress_frame = ttk.Frame(self.progress_window, padding="10")
        self.progress_frame.pack(pady=10, fill='both', expand=True)

        for name, info in self.progress_info.items():
            self.create_progress_bar(name, info)

        self.update_progress_window()

    def create_progress_bar(self, name, info):
        progress_frame = ttk.Frame(self.progress_frame)
        progress_frame.pack(pady=5, fill='x')

        command_label = ttk.Label(progress_frame, text=name, font=("Helvetica", 12, "bold"))
        command_label.pack(anchor='w')

        progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate', length=400)
        progress_bar.pack(side='left', padx=10, fill='x', expand=True)
        percentage_label = ttk.Label(progress_frame, text=f"{int((info['progress'] / info['max']) * 100)}%")
        percentage_label.pack(side='right')

        progress_bar['maximum'] = info['max']
        progress_bar['value'] = info['progress']
        info['progress_bar'] = progress_bar
        info['percentage_label'] = percentage_label

    def update_progress_window(self):
        for info in self.progress_info.values():
            progress_bar = info['progress_bar']
            percentage_label = info['percentage_label']
            progress_bar['value'] = info['progress']
            percentage_label.config(text=f"{int((info['progress'] / info['max']) * 100)}%")

        self.progress_window.after(1000, self.update_progress_window)

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def update_category_listbox(self, event=None):
        self.category_listbox.delete(0, tk.END)
        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

    def update_command_listbox(self, event=None, commands=None):
        self.local_command_listbox.delete(0, tk.END)
        selected_category = self.category_listbox.get(tk.ACTIVE) if commands is None else None
        commands = commands or {name: details for name, details in self.commands.items() if details.get('category', 'Uncategorized') == selected_category}
        for name, details in commands.items():
            command_info = f"Name: {name}, Command: {details['command']}, Description: {details.get('description', 'No description')}"
            self.local_command_listbox.insert(tk.END, command_info)

    def perform_local_search(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            show_message("Error", "Search query cannot be empty.", "error")
            return

        search_results = search_commands(self.commands, query)
        if not search_results:
            show_message("Search Results", "No commands found matching the query.")
        else:
            self.update_local_command_listbox(commands=search_results)

    def update_local_command_listbox(self, commands):
        self.local_command_listbox.delete(0, tk.END)
        for name, details in commands.items():
            command_info = f"Name: {name}, Command: {details['command']}, Description: {details.get('description', 'No description')}"
            self.local_command_listbox.insert(tk.END, command_info)

    def perform_online_search(self):
        query = self.online_search_entry.get().strip().lower()
        if not query:
            show_message("Error", "Search query cannot be empty.", "error")
            return
        
        self.search_online_commands(query)

    def search_online_commands(self, query):
        # Encode the query in base64 format
        base64_query = base64.urlsafe_b64encode(query.encode()).decode()

        api_url = f"https://www.commandlinefu.com/commands/matching/{query}/{base64_query}/json"
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            if 'application/json' in response.headers.get('Content-Type', ''):
                commands = response.json()
                if commands:
                    self.display_online_commands(commands)
                else:
                    show_message("Search Results", "No commands found matching the query on the web.")
            else:
                # Handle HTML response
                soup = BeautifulSoup(response.text, 'html.parser')
                command_elements = soup.find_all('div', class_='command')
                commands = []
                for elem in command_elements:
                    command_text_elem = elem.find('pre', class_='command')
                    summary_text_elem = elem.find('div', class_='description')
                    if command_text_elem and summary_text_elem:
                        command_text = command_text_elem.text.strip()
                        summary_text = summary_text_elem.text.strip()
                        commands.append({'command': command_text, 'summary': summary_text})
                if commands:
                    self.display_online_commands(commands)
                else:
                    show_message("Search Results", "No commands found matching the query on the web.")
        except requests.exceptions.RequestException as e:
            show_message("Error", f"Failed to fetch commands: {e}", "error")
        except ValueError:
            show_message("Error", "Invalid JSON response received.", "error")

    def display_online_commands(self, commands):
        self.online_command_listbox.delete(0, tk.END)
        for cmd in commands:
            command_info = f"Command: {cmd['command']}, Summary: {cmd['summary']}"
            self.online_command_listbox.insert(tk.END, command_info)

    def perform_search(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            show_message("Error", "Search query cannot be empty.", "error")
            return

        local_search_results = search_commands(self.commands, query)
        if local_search_results:
            self.update_command_listbox(commands=local_search_results)
        else:
            self.search_online_commands(query)

    def add_category(self):
        category = simpledialog.askstring("Add Category", "Enter a name for the category:").strip()
        if not category or category in self.categories:
            show_message("Error", "Invalid or duplicate category name.", "error")
            return
        self.categories.append(category)
        self.update_category_listbox()
        show_message("Success", f"Category '{category}' added successfully!")

    def delete_category(self):
        selected_category = self.category_listbox.get(tk.ACTIVE)
        if not selected_category or selected_category == 'Uncategorized':
            show_message("Error", "Invalid category selection.", "error")
            return

        if messagebox.askyesno("Delete Category", f"Are you sure you want to delete the category '{selected_category}' and move its commands to 'Uncategorized'?"):
            for name, details in self.commands.items():
                if details.get('category', 'Uncategorized') == selected_category:
                    self.commands[name]['category'] = 'Uncategorized'
            self.categories.remove(selected_category)
            save_commands(self.commands)
            self.update_category_listbox()
            self.update_command_listbox()
            show_message("Success", f"Category '{selected_category}' deleted successfully!")

    def add_command_window(self):
        self.command_window("Add Command", self.add_command)

    def modify_command_window(self, event):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        if name in self.commands:
            self.command_window("Modify Command", lambda: self.modify_command(name), name)

    def command_window(self, title, save_command, name=""):
        self.add_command_frame = tk.Toplevel(self)
        self.add_command_frame.title(title)
        self.add_command_frame.geometry("300x400")

        tk.Label(self.add_command_frame, text="Name:").pack(pady=5)
        self.command_name_entry = tk.Entry(self.add_command_frame)
        self.command_name_entry.pack(pady=5)
        if name:
            self.command_name_entry.insert(0, name)
            self.command_name_entry.config(state='disabled')

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

        if name:
            details = self.commands[name]
            self.command_entry.insert(0, details['command'])
            self.command_description_entry.insert(0, details.get('description', ''))
            self.command_category_combobox.set(details.get('category', 'Uncategorized'))
            self.command_interval_entry.insert(0, details.get('interval', 0))
            self.command_count_entry.insert(0, details.get('count', 1))

        tk.Button(self.add_command_frame, text="Save", command=save_command).pack(pady=5)
        tk.Button(self.add_command_frame, text="Cancel", command=self.add_command_frame.destroy).pack(pady=5)

    def add_command(self):
        self.save_command()

    def modify_command(self, original_name):
        self.save_command(original_name)

    def save_command(self, original_name=None):
        name = self.command_name_entry.get().strip()
        command = self.command_entry.get().strip()
        description = self.command_description_entry.get().strip()
        category = self.command_category_combobox.get().strip() or 'Uncategorized'
        interval = self.command_interval_entry.get().strip()
        count = self.command_count_entry.get().strip()

        if not name or not command or not interval.isdigit() or not count.isdigit():
            show_message("Error", "Invalid input values.", "error")
            return

        if original_name:
            self.commands.pop(original_name)
        elif name in self.commands:
            show_message("Error", "A command with this name already exists.", "error")
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
        show_message("Success", f"Command '{name}' saved successfully!")

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
            threading.Thread(target=self.execute_command, args=(name,)).start()
        else:
            show_message("Error", "No command found with that name.", "error")

    def execute_command(self, name):
        command = self.commands[name]
        interval, count = command.get("interval", 0), command.get("count", 1)
        self.output_text.config(state=tk.NORMAL)
        self.progress_info[name] = {'progress': 0, 'max': count, 'output': []}

        for i in range(count):
            try:
                result = subprocess.run(command["command"], shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
            except Exception as e:
                output = str(e)
            
            self.output_text.insert(tk.END, f"Execution {i+1}/{count}:\n{output}\n")
            self.output_text.see(tk.END)
            self.progress_info[name]['progress'] = i + 1
            self.progress_info[name]['output'].append(output)
            time.sleep(interval)

        self.progress_info[name]['progress'] = count
        self.output_text.config(state=tk.DISABLED)

        # Store command execution result in history
        self.command_history.append({
            'name': name,
            'command': command['command'],
            'output': self.progress_info[name]['output'],
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        })

    def show_history_window(self):
        self.history_window = tk.Toplevel(self)
        self.history_window.title("Command History")
        self.history_window.geometry("600x400")

        self.history_listbox = tk.Listbox(self.history_window)
        self.history_listbox.pack(fill='both', expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.show_history_details)

        for entry in self.command_history:
            self.history_listbox.insert(tk.END, f"{entry['timestamp']} - {entry['name']}")

    def show_history_details(self, event):
        selected_index = self.history_listbox.curselection()
        if not selected_index:
            return
        selected_entry = self.command_history[selected_index[0]]
        details = f"Name: {selected_entry['name']}\nCommand: {selected_entry['command']}\nTimestamp: {selected_entry['timestamp']}\n\nOutput:\n"
        details += "\n".join(selected_entry['output'])

        self.history_details_window = tk.Toplevel(self.history_window)
        self.history_details_window.title("Command History Details")
        self.history_details_window.geometry("600x400")

        history_details_text = tk.Text(self.history_details_window, wrap='word')
        history_details_text.insert(tk.END, details)
        history_details_text.config(state=tk.DISABLED)
        history_details_text.pack(fill='both', expand=True)

    def schedule_command(self, name, time_str):
        command = self.commands[name]
        schedule.every().day.at(time_str).do(self.execute_command_scheduled, name)
        show_message("Success", f"Command '{name}' scheduled at {time_str}")

    def execute_command_scheduled(self, name):
        threading.Thread(target=self.execute_command, args=(name,)).start()

    def schedule_command_window(self):
        selected_command = self.command_listbox.get(tk.ACTIVE)
        if not selected_command:
            show_message("Error", "Please select a command to schedule.", "error")
            return
        name = selected_command.split(",")[0].split(":")[1].strip()
        if name not in self.commands:
            show_message("Error", "No command found with that name.", "error")
            return

        self.schedule_command_frame = tk.Toplevel(self)
        self.schedule_command_frame.title("Schedule Command")
        self.schedule_command_frame.geometry("300x200")

        tk.Label(self.schedule_command_frame, text="Time (HH:MM):").pack(pady=5)
        self.schedule_time_entry = tk.Entry(self.schedule_command_frame)
        self.schedule_time_entry.pack(pady=5)

        tk.Button(self.schedule_command_frame, text="Schedule", 
                  command=lambda: self.schedule_command(name, self.schedule_time_entry.get())).pack(pady=5)
        tk.Button(self.schedule_command_frame, text="Cancel", 
                  command=self.schedule_command_frame.destroy).pack(pady=5)

    def run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def export_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "w") as file:
                    json.dump(self.commands, file, indent=4)
                show_message("Success", f"Configuration exported to {file_path}")
            except Exception as e:
                show_message("Error", f"Failed to export configuration: {e}", "error")

    def import_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
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