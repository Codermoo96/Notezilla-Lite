from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton,
    QHBoxLayout, QLabel, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QDate
import sys
import os

AUTOSAVE_PATH = "autosave.txt"

class SimplyNoting(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self._drag_pos = None # Går att dra
        # Frameless + always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMinimumSize(200, 300)

        # === Central widget ===
        central = QWidget()
        central.setStyleSheet("background-color: #ffff99; border: 1px solid #555;")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # === Top bar (hidden until hover) ===
        self.topbar = QWidget()
        self.topbar.setStyleSheet("background-color: #eeee88;")
        topbar_layout = QHBoxLayout(self.topbar)
        topbar_layout.setContentsMargins(5, 2, 5, 2)

        self.title_label = QLabel("SimplyNoting")
        self.date_label = QLabel(QDate.currentDate().toString(Qt.ISODate))
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("background-color: #ff5555; color: white; border: none;")
        self.close_button.clicked.connect(self.close)

        topbar_layout.addWidget(self.title_label)
        topbar_layout.addStretch()
        topbar_layout.addWidget(QLabel("Datum:"))
        topbar_layout.addWidget(self.date_label)
        topbar_layout.addWidget(self.close_button)

        self.topbar.hide()  # start hidden
        main_layout.addWidget(self.topbar)

        # === Text area ===
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("background-color: #ffff99; border: none;")
        self.text_edit.setPlaceholderText("Skriv dagliga to-dos eller tankar här...")
        main_layout.addWidget(self.text_edit)

        # === Button row ===
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # === Autosave timer ===
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(10_000)  # varje 10 sek

        # === Hover detection ===
        self.setMouseTracking(True)
        central.setMouseTracking(True)
        self.text_edit.setMouseTracking(True)

        # === Load previous autosave ===
        self.load_autosave()


        self.topbar.mousePressEvent = self.topbar_mouse_press
        self.topbar.mouseMoveEvent = self.topbar_mouse_move
        self.topbar.mouseReleaseEvent = self.topbar_mouse_release

    def enterEvent(self, event):
        self.topbar.show()

    def leaveEvent(self, event):
        QTimer.singleShot(500, self.hide_topbar_if_needed)

    def hide_topbar_if_needed(self):
        if not self.underMouse():
            self.topbar.hide()

    def autosave(self):
        try:
            with open(AUTOSAVE_PATH, 'w', encoding='utf-8') as f:
                f.write(f"Datum: {self.date_label.text()}\n\n")
                f.write(self.text_edit.toPlainText())
        except Exception as e:
            print(f"[Autosparning] Fel: {e}")

    def load_autosave(self):
        if os.path.exists(AUTOSAVE_PATH):
            try:
                with open(AUTOSAVE_PATH, 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
                    if lines and lines[0].startswith("Datum: "):
                        self.date_label.setText(lines[0][7:])
                    self.text_edit.setPlainText('\n'.join(lines[2:]))
            except Exception as e:
                print(f"[Laddning] Fel: {e}")


    def topbar_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def topbar_mouse_move(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def topbar_mouse_release(self, event):
        self._drag_pos = None
        event.accept()


    def open_note(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Öppna anteckning", "", "Textfiler (*.txt)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
                    if lines and lines[0].startswith("Datum: "):
                        self.date_label.setText(lines[0][7:])
                    self.text_edit.setPlainText('\n'.join(lines[2:]))
            except Exception as e:
                QMessageBox.critical(self, "Fel vid öppning", str(e))
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimplyNoting()
    window.show()
    sys.exit(app.exec())
