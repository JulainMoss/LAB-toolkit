import json
import os
import argparse

parser = argparse.ArgumentParser(description="Wyświetl zawartość pliku JSON w sformatowany sposób.")
parser.add_argument("-n", help="Nazwa pliku JSON do wyświetlenia")
args = parser.parse_args()

def wyswietl_json(nazwa_pliku):
    if not os.path.exists(nazwa_pliku):
        print(f"❌ Error: File with name '{nazwa_pliku}' does not exist.")
        return

    try:
        with open(nazwa_pliku, 'r', encoding='utf-8') as plik:
            dane = json.load(plik)

        with open(f"{nazwa_pliku}_formated.json", 'w', encoding='utf-8') as plik:
            json.dump(dane, plik, indent=4, ensure_ascii=False)


    except json.JSONDecodeError:
        print("❌ Error: Existing file is not in valid JSON format.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    wyswietl_json(args.n)