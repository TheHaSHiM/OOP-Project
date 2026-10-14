from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel

class _TextDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Введення тексту (Робота 1)")
        self.resize(300, 120)

        self.result_text = ''

        self.label = QLabel("Введіть рядок тексту")
        self.edit_control = QLineEdit()

        self.btn_ok = QPushButton('Так')
        self.btn_cancel = QPushButton('Відміна')

        self.btn_ok.clicked.connect(self._on_ok)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.edit_control)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def _on_ok(self):
        self.result_text = self.edit_control.text()
        self.accept()

def func_mod1(parent=None) -> tuple[int, str]:

    dialog = _TextDialog(parent)
    result_code = dialog.exec()

    if result_code == QDialog.DialogCode.Accepted:
        return 1, dialog.result_text
    return 0, ''