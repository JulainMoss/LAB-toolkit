import sys
from PyQt5.Qsci import QsciScintilla, QsciLexerJavaScript
from app_widgets import *

class JsonViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.json_data = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("JSON Formatter")
        self.resize(1000, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Panel górny ---
        top_panel = QHBoxLayout()

        self.btn_load = QPushButton("Wgraj plik JSON")
        self.btn_load.clicked.connect(self.load_json)
        top_panel.addWidget(self.btn_load)

        self.btn_http_toggle = QPushButton("Pobierz przez HTTP")
        self.btn_http_toggle.setCheckable(True)
        self.btn_http_toggle.clicked.connect(self.toggle_http_panel)
        top_panel.addWidget(self.btn_http_toggle)

        self.btn_save = QPushButton("Zapisz plik JSON")
        self.btn_save.clicked.connect(self.save_json)
        self.btn_save.setEnabled(False) 
        top_panel.addWidget(self.btn_save)

        self.btn_delete = QPushButton("Wyczyść dane")
        self.btn_delete.clicked.connect(self.clear_json_data)
        self.btn_delete.setEnabled(False)
        top_panel.addWidget(self.btn_delete)

        top_panel.addStretch()

        lbl_indent = QLabel("Rozmiar wcięcia (spacje):")
        top_panel.addWidget(lbl_indent)

        # --- WYDZIELONY SPIN INDENT ---
        self.spin_indent = SpinIndent(refresher=self.refresh_display)
        top_panel.addWidget(self.spin_indent)

        main_layout.addLayout(top_panel)

        # --- WYDZIELONY PANEL HTTP ---
        self.http_panel = HTTPPanel(root=self)
        main_layout.addWidget(self.http_panel)

        # --- Edytor ---
        self.editor = QsciScintilla()
        self.editor.setUtf8(True)

        self.lexer = QsciLexerJavaScript()
        self.lexer.setFoldCompact(False) 
        self.editor.setLexer(self.lexer)

        self.editor.setReadOnly(True)
        self.editor.setFolding(QsciScintilla.PlainFoldStyle)
        self.editor.setMarginWidth(2, 15) 
        self.editor.setFoldMarginColors(
            self.palette().color(self.backgroundRole()),
            self.palette().color(self.backgroundRole())
        )

        self.editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.editor.setMarginWidth(0, "0000") 

        main_layout.addWidget(self.editor)

    def toggle_http_panel(self, checked):
        self.http_panel.setVisible(checked)

    def load_json(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik JSON", "", "JSON Files (*.json);;All Files (*)", options=options
        )

        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    self.json_data = json.load(file)

                self.btn_save.setEnabled(True)
                self.btn_delete.setEnabled(True)
                self.refresh_display()

            except json.JSONDecodeError:
                QMessageBox.critical(self, "Błąd", "Wybrany plik nie jest poprawnym plikiem JSON.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać pliku:\n{str(e)}")

    def refresh_display(self):
        if self.json_data is not None:
            indent_size = self.spin_indent.value()
            formatted_text = json.dumps(self.json_data, indent=indent_size, ensure_ascii=False)

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
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(self.json_data, file, indent=indent_size, ensure_ascii=True)

                QMessageBox.information(self, "Sukces", "Plik został pomyślnie zapisany.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{str(e)}")

    def clear_json_data(self):
        self.json_data = None
        self.editor.setReadOnly(False)
        self.editor.clear()
        self.editor.setReadOnly(True)
        self.btn_save.setEnabled(False)
        self.btn_delete.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JsonViewerApp()
    window.show()
    sys.exit(app.exec_())