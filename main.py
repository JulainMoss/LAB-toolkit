import sys

from JSONFormatter import JsonFormatterApp
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout

class LABToolkitApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LAB Toolkit")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.json_formatter_btn = QPushButton("JSON Formatter")
        self.json_formatter_btn.clicked.connect(self.open_json_formatter)
        main_layout.addWidget(self.json_formatter_btn)

    def open_json_formatter(self):
        # 1. Tworzymy instancję nowego okna (WAŻNE: przypisujemy do self, 
        # aby Python nie usunął okna z pamięci po zakończeniu tej funkcji!)
        self.json_formatter_window = JsonFormatterApp()
        
        # 2. Wyświetlamy nowe okno
        self.json_formatter_window.show()
        
        # 3. Zamykamy obecne okno (LAB Toolkit)
        self.close()

if __name__ == "__main__":
    # Tworzymy aplikację TYLKO RAZ w całym programie
    app = QApplication(sys.argv)
    
    # Tworzymy i pokazujemy okno startowe
    main_window = LABToolkitApp()
    main_window.show()
    
    # Uruchamiamy główną pętlę zdarzeń, która utrzyma przy życiu wszystkie otwarte okna
    sys.exit(app.exec_())