import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class JsonTreeFormatterApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Interaktywna Przeglądarka i Formater JSON")
        self.root.geometry("1000, 600")
        self.root.minsize(800, 500)

        self.loaded_json_data = None
        self.create_widgets()

    def create_widgets(self):
        # --- Panel górny (Przyciski) ---
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack(fill=tk.X)

        self.btn_load = tk.Button(
            button_frame,
            text="Wczytaj plik JSON",
            command=self.load_json,
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5,
        )
        self.btn_load.pack(side=tk.LEFT, padx=10)

        self.btn_save = tk.Button(
            button_frame,
            text="Zapisz sformatowany JSON",
            command=self.save_json,
            bg="#008CBA",
            fg="white",
            padx=10,
            pady=5,
            state=tk.DISABLED,
        )
        self.btn_save.pack(side=tk.LEFT, padx=10)

        # --- Panel główny (Podział na pół) ---
        # PanedWindow pozwala użytkownikowi myszką przesuwać granicę między panelami
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, s创作h=True)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Lewy panel: Drzewo JSON (Zwijane pola)
        left_frame = tk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)

        lbl_tree = tk.Label(
            left_frame, text="Interaktywne drzewo (klikaj strzałki, aby zwijać):", anchor="w"
        )
        lbl_tree.pack(fill=tk.X, pady=(0, 5))

        # Komponent drzewa
        self.tree = ttk.Treeview(left_frame, columns=("Wartość",), selectmode="browse")
        self.tree.heading("#0", text="Klucz / Indeks", anchor="w")
        self.tree.heading("Wartość", text="Wartość", anchor="w")
        self.tree.column("#0", minwidth=200, width=300)
        self.tree.column("Wartość", minwidth=200, width=200)

        # Paski przewijania dla drzewa
        tree_scroll_y = ttk.Scrollbar(
            left_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        tree_scroll_x = ttk.Scrollbar(
            left_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
        )

        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Prawy panel: Podgląd sformatowanego tekstu do zapisu
        right_frame = tk.Frame(main_pane)
        main_pane.add(right_frame, weight=1)

        lbl_text = tk.Label(right_frame, text="Sformatowany tekst (podgląd pliku):", anchor="w")
        lbl_text.pack(fill=tk.X, pady=(0, 5))

        self.text_area = tk.Text(right_frame, wrap=tk.NONE, font=("Consolas", 10))
        text_scroll_y = ttk.Scrollbar(
            right_frame, orient=tk.VERTICAL, command=self.text_area.yview
        )
        text_scroll_x = ttk.Scrollbar(
            right_frame, orient=tk.HORIZONTAL, command=self.text_area.xview
        )
        self.text_area.configure(
            yscrollcommand=text_scroll_y.set, xscrollcommand=text_scroll_x.set
        )

        text_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        text_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def load_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.loaded_json_data = json.load(file)

            # 1. Czyszczenie starych danych
            self.tree.delete(*self.tree.get_children())
            self.text_area.delete("1.0", tk.END)

            # 2. Budowanie interaktywnego drzewa (rekurencyjnie)
            self.build_tree("", self.loaded_json_data)

            # 3. Wypełnianie prawego panelu sformatowanym tekstem
            formatted_json = json.dumps(
                self.loaded_json_data, indent=4, ensure_ascii=False
            )
            self.text_area.insert(tk.END, formatted_json)

            self.btn_save.config(state=tk.NORMAL)
            messagebox.showinfo("Sukces", "JSON załadowany pomyślnie!")

        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Błąd parsing JSON", f"Niepoprawna składnia JSON:\n{e}"
            )
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się otworzyć pliku:\n{e}")

    def build_tree(self, parent, data, key_name=""):
        """Rekurencyjna funkcja parsująca JSON do widoku drzewa ttk.Treeview"""
        if isinstance(data, dict):
            # Jeśli element to słownik (obiekt JSON) -> stwórz węzeł i wejdź głębiej
            node_text = key_name if key_name else "{ }"
            node = self.tree.insert(parent, "end", text=node_text, values=("Object",))
            for k, v in data.items():
                self.build_tree(node, v, key_name=k)

        elif isinstance(data, list):
            # Jeśli element to lista (tablica JSON) -> stwórz węzeł z indeksem i wejdź głębiej
            node_text = f"{key_name} [ ]" if key_name else "[ ]"
            node = self.tree.insert(
                parent, "end", text=node_text, values=(f"Array ({len(data)} items)",)
            )
            for index, item in enumerate(data):
                self.build_tree(node, item, key_name=f"[{index}]")

        else:
            # Jeśli to wartość prosta (tekst, liczba, bool, null) -> wyświetl jako liść drzewa
            # Zabezpieczenie dla wartości typu None / bool w Pythonie
            val_str = "null" if data is None else str(data)
            if isinstance(data, bool):
                val_str = str(data).lower()

            self.tree.insert(parent, "end", text=key_name, values=(val_str,))

    def save_json(self):
        if self.loaded_json_data is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")],
        )
        if not file_path:
            return

        try:
            # Pobieramy bezpośrednio z pola tekstowego po prawej stronie
            text_content = self.text_area.get("1.0", tk.END).strip()
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_content)
            messagebox.showinfo("Sukces", "Plik został zapisany z wcięciami!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać pliku:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = JsonTreeFormatterApp(root)
    root.mainloop()