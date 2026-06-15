import sys
import json
import urllib.request
import urllib.error
import urllib.parse  # Dodane do kodowania parametrów URL
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QSpinBox,
                             QLabel, QMessageBox, QLineEdit, QComboBox, QFrame)
from PyQt5.Qsci import QsciScintilla, QsciLexerJavaScript

class JsonViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.json_data = None
        self.param_widgets = []  # Lista do przechowywania pól parametrów zapytania
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Przeglądarka JSON - Parametry zapytania i HTTP")
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

        top_panel.addStretch()

        lbl_indent = QLabel("Rozmiar wcięcia (spacje):")
        top_panel.addWidget(lbl_indent)

        self.spin_indent = QSpinBox()
        self.spin_indent.setRange(1, 8)
        self.spin_indent.setValue(4) 
        self.spin_indent.valueChanged.connect(self.refresh_display)
        top_panel.addWidget(self.spin_indent)

        main_layout.addLayout(top_panel)

        # --- ZMODYFIKOWANY PANEL HTTP ---
        self.http_panel = QFrame()
        self.http_panel.setFrameShape(QFrame.StyledPanel)
        self.http_panel.setStyleSheet("background-color: #fcfcfc; border-radius: 4px;")
        
        # Główny układ panelu to teraz układ pionowy
        http_main_layout = QVBoxLayout(self.http_panel)
        
        # 1. Wiersz: Metoda i URL
        url_layout = QHBoxLayout()
        self.combo_method = QComboBox()
        self.combo_method.addItems(["GET", "POST", "PUT", "DELETE"])
        url_layout.addWidget(QLabel("Metoda:"))
        url_layout.addWidget(self.combo_method)
        
        self.line_url = QLineEdit()
        self.line_url.setPlaceholderText("Wpisz bazowy adres URL (np. https://api.github.com/users)")
        url_layout.addWidget(QLabel("Adres URL:"))
        url_layout.addWidget(self.line_url)
        http_main_layout.addLayout(url_layout)
        
        # 2. Miejsce na parametry zapytania (dynamiczne wiersze)
        self.params_layout = QVBoxLayout()
        http_main_layout.addLayout(self.params_layout)
        
        # 3. Przyciski dolne panelu HTTP
        buttons_layout = QVBoxLayout()
        
        self.btn_add_param = QPushButton("Dodaj pole parametru zapytania")
        self.btn_add_param.clicked.connect(self.add_param_row)
        buttons_layout.addWidget(self.btn_add_param)
        
        self.btn_send = QPushButton("Wyślij zapytanie")
        self.btn_send.clicked.connect(self.send_http_request)
        buttons_layout.addWidget(self.btn_send)
        
        http_main_layout.addLayout(buttons_layout)
        
        self.http_panel.setVisible(False)
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

    def add_param_row(self):
        """Dodaje nowy wiersz dla parametru zapytania (klucz = wartość)."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        # Edytowalna etykieta - klucz parametru
        key_edit = QLineEdit()
        key_edit.setPlaceholderText("Nazwa parametru (np. id)")
        
        # Wartość parametru
        val_edit = QLineEdit()
        val_edit.setPlaceholderText("Wartość parametru")
        
        # Przycisk usuwania danego wiersza
        btn_remove = QPushButton("Usuń")
        btn_remove.setFixedWidth(50)
        btn_remove.setStyleSheet("color: red;")
        btn_remove.clicked.connect(lambda: self.remove_param_row(row_widget))
        
        row_layout.addWidget(key_edit)
        row_layout.addWidget(QLabel("="))
        row_layout.addWidget(val_edit)
        row_layout.addWidget(btn_remove)
        
        self.params_layout.addWidget(row_widget)
        # Zapisujemy referencje, aby później zebrać z nich dane
        self.param_widgets.append((key_edit, val_edit, row_widget))

    def remove_param_row(self, row_widget):
        """Usuwa wskazany wiersz parametru z układu i listy."""
        self.params_layout.removeWidget(row_widget)
        row_widget.deleteLater()
        # Aktualizacja listy odniesień
        self.param_widgets = [pw for pw in self.param_widgets if pw[2] != row_widget]

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
                self.refresh_display()

            except json.JSONDecodeError:
                QMessageBox.critical(self, "Błąd", "Wybrany plik nie jest poprawnym plikiem JSON.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać pliku:\n{str(e)}")

    def send_http_request(self):
        base_url = self.line_url.text().strip()
        method = self.combo_method.currentText()
        
        if not base_url:
            QMessageBox.warning(self, "Ostrzeżenie", "Proszę wprowadzić adres URL.")
            return
            
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            base_url = "http://" + base_url
            self.line_url.setText(base_url)

        # Zbieranie i kodowanie parametrów
        query_params = {}
        for key_edit, val_edit, _ in self.param_widgets:
            key = key_edit.text().strip()
            val = val_edit.text().strip()
            if key:  # Dodajemy tylko, jeśli nazwa parametru nie jest pusta
                query_params[key] = val

        # Jeśli wprowadzono parametry, budujemy pełny URL
        final_url = base_url
        if query_params:
            encoded_params = urllib.parse.urlencode(query_params)
            # Sprawdzamy czy w bazowym URL jest już jakiś znak '?' by uniknąć błędów (np. https://api.com?key=1)
            separator = '&' if '?' in final_url else '?'
            final_url = f"{final_url}{separator}{encoded_params}"

        self.btn_send.setEnabled(False)
        self.btn_send.setText("Wysyłanie...")
        QApplication.processEvents()

        response_text = ""
        try:
            req = urllib.request.Request(final_url, method=method)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            req.add_header('Accept', 'application/json')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                response_bytes = response.read()
                charset = response.headers.get_content_charset() or 'utf-8'
                response_text = response_bytes.decode(charset, errors='replace')
                
            self.json_data = json.loads(response_text)
            self.btn_save.setEnabled(True)
            self.refresh_display()
            
        except json.JSONDecodeError:
            snippet = response_text[:250].strip() if response_text else "Brak danych."
            if len(response_text) > 250:
                snippet += "\n[... ciąg dalszy ucięty ...]"
                
            QMessageBox.critical(
                self, 
                "Błąd formatu JSON", 
                f"Adres:\n{final_url}\n\nOdebrana treść to nie JSON!\n\nPoczątek odpowiedzi:\n\n{snippet}"
            )
        except urllib.error.HTTPError as e:
            try:
                err_text = e.read().decode('utf-8', errors='replace')
                snippet = err_text[:250].strip()
                if len(err_text) > 250:
                    snippet += "\n[... ucięte ...]"
            except:
                snippet = "Brak czytelnej treści."
                
            QMessageBox.critical(
                self, 
                "Błąd HTTP", 
                f"Serwer zwrócił kod {e.code} ({e.reason}).\n\nPoczątek odpowiedzi:\n\n{snippet}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił nieoczekiwany błąd:\n{str(e)}")
            
        finally:
            self.btn_send.setEnabled(True)
            self.btn_send.setText("Wyślij zapytanie")

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
                    json.dump(self.json_data, file, indent=indent_size, ensure_ascii=False)

                QMessageBox.information(self, "Sukces", "Plik został pomyślnie zapisany.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JsonViewerApp()
    window.show()
    sys.exit(app.exec_())