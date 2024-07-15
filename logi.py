import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QTextEdit

class LogWorker(QObject):
    append_text_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def write(self, text):
        self.append_text_signal.emit(text)


class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logi Programu Szachy")
        self.setGeometry(100, 100, 600, 400)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.setCentralWidget(self.text_edit)

        self.log_worker = LogWorker()

        # Połączenie sygnału z odpowiednią metodą slotową
        self.log_worker.append_text_signal.connect(self.append_text)

        # Stworzenie i uruchomienie wątku dla log_workera
        self.worker_thread = QThread()
        self.log_worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

    def append_text(self, text):
        # Dodanie tekstu do pola tekstowego
        self.text_edit.insertPlainText(text)

    def write(self, text):
        # Emitowanie sygnału, aby dodać tekst do pola tekstowego
        self.log_worker.append_text_signal.emit(text)


# Funkcja do przekierowania stdout do okna logów
def redirect_stdout(log_window):
    class StdoutRedirect:
        def write(self, text):
            log_window.write(text)

    sys.stdout = StdoutRedirect()
