import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt

from module1 import func_mod1
from module2 import func_mod2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторна робота №1")
        self.resize(500,300)


        central_widget = QWidget()
        layout = QVBoxLayout()

        self.info_label = QLabel('Оберіть дію в меню вище')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFont(QFont('Arial', 14))

        layout.addWidget(self.info_label)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self._create_menu()

    def _create_menu(self):

        menu_bar = self.menuBar()

        actions_menu = menu_bar.addMenu("Дії")

        action_work1 = QAction('Робота1', self)
        action_work1.triggered.connect(self._on_work1)
        actions_menu.addAction(action_work1)

        action_work2 = QAction('Робота2', self)
        action_work2.triggered.connect(self._on_work2)
        actions_menu.addAction(action_work2)

    def _on_work1(self):

        status, text = func_mod1(self)
        if status == 1:
            self.info_label.setText(f"Результат Робота1:\n {text} ")
        else:
            self.info_label.setText("Робота1: скасовано користувачем")

    def _on_work2(self):

        status, number = func_mod2(self)
        if status == 1:
            self.info_label.setText(f"Результат Робота2:\nЧисло = {number}")
        else:
            self.info_label.setText('Робота2: скасовано користувачем')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())