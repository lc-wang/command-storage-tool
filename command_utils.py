# command_utils.py
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