import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QSpinBox,
                             QLabel, QMessageBox)
from PyQt5.Qsci import QsciLexerJavaScript, QsciScintilla

class JsonViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.json_data = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Przeglądarka JSON - Styl VS Code")
        self.resize(900, 700)

        # Główny widget i układ
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Panel górny (przyciski i ustawienia) ---
        top_panel = QHBoxLayout()

        self.btn_load = QPushButton("Wgraj plik JSON")
        self.btn_load.clicked.connect(self.load_json)
        top_panel.addWidget(self.btn_load)

        self.btn_save = QPushButton("Zapisz plik JSON")
        self.btn_save.clicked.connect(self.save_json)
        self.btn_save.setEnabled(False) # Wyłączony, dopóki nie wgramy danych
        top_panel.addWidget(self.btn_save)

        top_panel.addStretch()

        lbl_indent = QLabel("Rozmiar wcięcia (spacje):")
        top_panel.addWidget(lbl_indent)

        self.spin_indent = QSpinBox()
        self.spin_indent.setRange(1, 8)
        self.spin_indent.setValue(4) # Domyślne wcięcie
        self.spin_indent.valueChanged.connect(self.refresh_display)
        top_panel.addWidget(self.spin_indent)

        layout.addLayout(top_panel)

        # --- Edytor (QScintilla) ---
        self.editor = QsciScintilla()
        self.editor.setUtf8(True)

        # Ustawienie Lexera dla kolorowania składni JSON
        self.lexer = QsciLexerJavaScript()
        
        # Wyłączenie "kompaktowego" zwijania
        # Dzięki temu zwijanie zachowuje się przewidywalnie (jak w VS Code)
        # i nie "zjada" pustych linii podczas zwijania bloków.
        self.lexer.setFoldCompact(False)
        self.editor.setLexer(self.lexer)

        # Tryb tylko do odczytu (nieedytowalny)
        self.editor.setReadOnly(True)

        # Konfiguracja marginesu i zwijania kodu (VS Code style)
        self.editor.setFolding(QsciScintilla.PlainFoldStyle)
        self.editor.setMarginWidth(2, 15) # Szerokość marginesu dla zwijania
        self.editor.setFoldMarginColors(
            self.palette().color(self.backgroundRole()),
            self.palette().color(self.backgroundRole())
        )

        # Numery linii na marginesie po lewej stronie
        self.editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.editor.setMarginWidth(0, "0000") # Szerokość dostosowana do 4-cyfrowych numerów

        layout.addWidget(self.editor)

    def load_json(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik JSON", "", "JSON Files (*.json);;All Files (*)", options=options
        )

        if file_name:
            try:
                # Wczytanie i weryfikacja czy plik to poprawny JSON
                with open(file_name, 'r', encoding='utf-8') as file:
                    self.json_data = json.load(file)

                self.btn_save.setEnabled(True)
                self.refresh_display()

            except json.JSONDecodeError:
                QMessageBox.critical(self, "Błąd", "Wybrany plik nie jest poprawnym plikiem JSON.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać pliku:\n{str(e)}")

    def refresh_display(self):
        if self.json_data is not None:
            indent_size = self.spin_indent.value()
            
            # Formatowanie tekstu z aktualnym wcięciem
            formatted_text = json.dumps(self.json_data, indent=indent_size, ensure_ascii=False)

            # Wyłączenie trybu read-only tylko na ułamek sekundy, by zaktualizować tekst
            self.editor.setReadOnly(False)
            self.editor.setText(formatted_text)
            self.editor.setReadOnly(True)

    def save_json(self):
        if self.json_data is None:
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Zapisz jako...", "", "JSON Files (*.json);;All Files (*)", options=options
        )

        if file_name:
            try:
                indent_size = self.spin_indent.value()
                # Zapis do pliku z wybranym w UI wcięciem
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(self.json_data, file, indent=indent_size, ensure_ascii=False)

                QMessageBox.information(self, "Sukces", "Plik został pomyślnie zapisany.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JsonViewerApp()
    window.show()
    sys.exit(app.exec_())