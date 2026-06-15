from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QSpinBox,
                             QLabel, QMessageBox, QLineEdit, QComboBox, QFrame)
import urllib.request
import urllib.error
import urllib.parse
import json

class SpinIndent(QSpinBox):
    def __init__(self, parent=None, refresher=None):
        super().__init__(parent)
        self.setRange(0, 8)
        self.setValue(4)
        self.valueChanged.connect(refresher)

class HTTPPanel(QFrame):
    def __init__(self, parent=None, root=None):
        super().__init__(parent)
        self.root = root
        self.param_widgets = []  # Lista do przechowywania pól parametrów zapytania
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #fcfcfc; border-radius: 4px;")
        
        main_layout = QVBoxLayout(self)
        url_layout = QHBoxLayout()

        # Wybór metody HTTP
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE"])
        url_layout.addWidget(QLabel("Metoda:"))
        url_layout.addWidget(self.method_combo)

        # Bazowy adres URL
        self.line_url = QLineEdit()
        self.line_url.setPlaceholderText("Wpisz bazowy adres URL (np. https://api.github.com/users)")
        url_layout.addWidget(QLabel("Adres URL:"))
        url_layout.addWidget(self.line_url)
        main_layout.addLayout(url_layout)

        # Parametry zapytania (dynamiczne wiersze)
        self.params_layout = QVBoxLayout()
        main_layout.addLayout(self.params_layout)
        
        buttons_layout = QVBoxLayout()
        
        self.btn_add_param = QPushButton("Dodaj pole parametru zapytania")
        self.btn_add_param.clicked.connect(self.add_param_row)
        buttons_layout.addWidget(self.btn_add_param)
        
        self.btn_send = QPushButton("Wyślij zapytanie")
        self.btn_send.clicked.connect(self.send_http_request)
        buttons_layout.addWidget(self.btn_send)
        
        main_layout.addLayout(buttons_layout)
        
        self.setVisible(False)

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

    def send_http_request(self):
        base_url = self.line_url.text().strip()
        method = self.method_combo.currentText()
        
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
                
            self.root.json_data = json.loads(response_text)
            self.root.btn_save.setEnabled(True)
            self.root.btn_delete.setEnabled(True)
            self.root.refresh_display()
            
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