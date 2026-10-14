from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel
from PyQt6.QtCore import Qt

class _SliderDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle('Вибір числа (Робота 2)')
        self.resize(300, 140)

        self.selected_value = 50

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(self.selected_value)

        self.value_label = QLabel(f'Значення: {self.selected_value}')
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider.valueChanged.connect(self._on_slider_moved)

        self.btn_ok = QPushButton("Так")
        self.btn_cancal = QPushButton("Відміна")

        self.btn_ok.clicked.connect(self._on_ok)
        self.btn_cancal.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancal)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.value_label)
        main_layout.addWidget(self.slider)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def _on_slider_moved(self, val: int):
        self.selected_value = val
        self.value_label.setText(f'Значення: {val}')

    def _on_ok(self):
        self.accept()


def func_mod2(parent=None) -> tuple[int,  int]:
    dialog = _SliderDialog(parent)
    result_code = dialog.exec()

    if result_code == QDialog.DialogCode.Accepted:
        return 1, dialog.selected_value
    return 0, 0