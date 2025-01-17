import json

def load_commands():
    try:
        with open('commands.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_commands(commands):
    with open('commands.json', 'w') as file:
        json.dump(commands, file, indent=4)

def get_categories(commands):
    """Get unique categories from commands."""
    categories = set()
    for details in commands.values():
        categories.add(details.get('category', 'Uncategorized'))
    return list(categories)

def search_commands(commands, query):
    """Search for commands matching the query."""
    query = query.strip().lower()
    search_results = {}
    for name, details in commands.items():
        if (query in name.lower() or
            query in details.get('command', '').lower() or
            query in details.get('description', '').lower() or
            query in details.get('category', '').lower()):
            search_results[name] = details
    return search_results