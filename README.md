# Command Storage Tool

## Overview

The Command Storage Tool is a Python-based application built using Tkinter that allows users to manage and execute various commands on multiple platforms like Linux, Windows, and more. The tool provides a user-friendly interface for organizing commands into categories, executing them, and tracking their progress.

## Features

- **Add, Modify, and Delete Commands**: Easily manage your collection of commands.
- **Categorization**: Organize commands into different categories.
- **Command Execution**: Execute commands directly from the interface.
- **Progress Tracking**: Track the execution progress of commands with visual indicators.
- **Command Scheduling**: Schedule commands to run at specific times.
- **Command History**: View the history of executed commands and their outputs.
- **Import/Export Configuration**: Save and load your command configurations to/from a JSON file.
- **Search Online Commands**: Search for commands online and add them to your local collection.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lc-wang/command-storage-tool.git
   cd command-storage-tool
2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt

## Usage

1. **Add a Command**:
   - Click on the "Add Command" button.
   - Fill in the command details including name, command, description, category, interval, and count.
   - Click "Save" to add the command to the list.

2. **Modify a Command**:
   - Double-click on a command in the list.
   - Modify the command details as needed.
   - Click "Save" to update the command.

3. **Delete a Command**:
   - Select a command from the list.
   - Click on the "Delete Command" button to remove the command from the list.

4. **Execute a Command**:
   - Select a command from the list.
   - Click on the "Execute Command" button to run the command.
   - View the execution progress and output in the interface.

5. **Schedule a Command**:
   - Select a command from the list.
   - Click on the "Schedule Command" button.
   - Enter the time (HH:MM) to schedule the command.
   - Click "Schedule" to set up the scheduled execution.

6. **View Command History**:
   - Click on the "Command History" button.
   - View the list of executed commands with their timestamps.
   - Select a command from the history to view detailed output.

7. **Import/Export Configuration**:
   - Click on the "Export Config" button to save the current command configuration to a JSON file.
   - Click on the "Import Config" button to load a command configuration from a JSON file.

8. **Search Online Commands**:
   - Click on the "Search Online Commands" button.
   - Enter the search query and view the list of online commands.
   - Select the online command to add it to your local collection.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the repository owner. Thank you for using the Command Storage Tool!
