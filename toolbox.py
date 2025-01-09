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

def add_command(commands):
    """Add a new command to the toolbox."""
    name = input("Enter a name for the command: ").strip()
    if name in commands:
        print("A command with this name already exists.")
        return
    command = input("Enter the Linux command: ").strip()
    description = input("Enter a description (optional): ").strip()
    commands[name] = {"command": command, "description": description}
    print(f"Command '{name}' added successfully!")

def delete_command(commands):
    """Delete a command by name."""
    name = input("Enter the name of the command to delete: ").strip()
    if name in commands:
        del commands[name]
        print(f"Command '{name}' deleted successfully!")
    else:
        print("No command found with that name.")

def execute_command(commands):
    """Execute a saved command."""
    name = input("Enter the name of the command to execute: ").strip()
    if name in commands:
        os.system(commands[name]["command"])
    else:
        print("No command found with that name.")

def main():
    """Main function to run the toolbox."""
    commands = load_commands()

    while True:
        print("\nLinux Commands Toolbox")
        print("1. Add a new command")
        print("2. View all commands")
        print("3. Delete a command")
        print("4. Execute a command")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_command(commands)
            save_commands(commands)
        elif choice == "2":
            view_commands(commands)
        elif choice == "3":
            delete_command(commands)
            save_commands(commands)
        elif choice == "4":
            execute_command(commands)
        elif choice == "5":
            print("Exiting toolbox. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()