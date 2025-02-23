import json

from rapidfuzz import fuzz, process


def load_lookup_table(file_path="backend\core\commands\example.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def search_command(user_input, lookup_table, top_n=5, threshold=30):
    commands = list(lookup_table.keys())
    matches = process.extract(user_input, commands, scorer=fuzz.partial_ratio, limit=top_n)
    results = [match[0] for match in matches if match[1] >= threshold]
    return results if results else [commands[0]] if commands else []

def get_command_flags(command, lookup_table):
    return lookup_table.get(command, {}).get("flags", {})

def main():
    lookup_table = load_lookup_table()

    while True:
        user_input = input("Enter command: ").strip()
        if user_input.lower() == "exit":
            break

        suggestions = search_command(user_input, lookup_table)
        if suggestions:
            print("Did you mean:")
            for cmd in suggestions:
                print(f"  - {cmd}")

            primary_match = suggestions[0]
            flags = get_command_flags(primary_match, lookup_table)
            if flags:
                print(f"\nAvailable flags for {primary_match}:")
                for flag, desc in flags.items():
                    print(f"  {flag}: {desc}")
        else:
            print("No matching commands found.")

if __name__ == "__main__":
    main()
