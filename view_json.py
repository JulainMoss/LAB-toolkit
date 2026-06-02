import json
import os
import argparse

parser = argparse.ArgumentParser(description="Format JSON file for better readability")
parser.add_argument("-n", help="Name of the JSON file to display", required=True)
args = parser.parse_args()

def wyswietl_json(filename):
    if not os.path.exists(filename):
        print(f"❌ Error: File with name '{filename}' does not exist.")
        return

    os.makedirs("output", exist_ok=True)
    name, ext = os.path.splitext(filename)
    name = os.path.basename(name)
    print(f"📂 Processing file: {name}")

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        with open(f"output/{name}_formated.json", 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


    except json.JSONDecodeError:
        print("❌ Error: Existing file is not in valid JSON format.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    wyswietl_json(args.n)