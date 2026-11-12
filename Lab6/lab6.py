import sys
import os

os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

import time
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QDialog, QSpinBox, QTextEdit, QMessageBox
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtNetwork import QLocalSocket
from PyQt6.QtCore import Qt


class ParamsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введення параметрів (Варіант 0)")
        self.resize(320, 240)

        layout = QVBoxLayout()

        self.spn_points = self._add_field(layout, "Кількість точок (nPoint):", 2, 500, 20)
        self.spn_xmin = self._add_field(layout, "Мінімум X (xMin):", -1000, 1000, 0)
        self.spn_xmax = self._add_field(layout, "Максимум X (xMax):", -1000, 1000, 100)
        self.spn_ymin = self._add_field(layout, "Мінімум Y (yMin):", -1000, 1000, 10)
        self.spn_ymax = self._add_field(layout, "Максимум Y (yMax):", -1000, 1000, 90)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Виконати")
        self.btn_cancel = QPushButton("Відміна")

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _add_field(self, layout, label_text, min_val, max_val, default_val) -> QSpinBox:
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        spn = QSpinBox()
        spn.setRange(min_val, max_val)
        spn.setValue(default_val)
        row.addWidget(lbl)
        row.addWidget(spn)
        layout.addLayout(row)
        return spn

    def get_params(self) -> tuple[int, int, int, int, int]:
        return (
            self.spn_points.value(),
            self.spn_xmin.value(),
            self.spn_xmax.value(),
            self.spn_ymin.value(),
            self.spn_ymax.value()
        )
    

class Lab6MainWindow(QMainWindow):
    SERVER_OBJ2 = "Lab6_Object2_Server"
    SERVER_OBJ3 = "Lab6_Object3_Server"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab6 — Головний Менеджер (Варіант 0)")
        self.resize(360, 480)

        central_widget = QWidget()
        layout = QVBoxLayout()

        lbl_title = QLabel("Керування компонентами системи")
        lbl_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        self.btn_start = QPushButton("Ввести параметри та Запустити")
        self.btn_start.setFixedHeight(40)
        self.btn_start.clicked.connect(self._start_workflow)
        layout.addWidget(self.btn_start)


        layout.addWidget(QLabel("Журнал обміну повідомленнями:"))
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        layout.addWidget(self.log_edit)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self._create_menu()
        self._log("Програма Lab6 готова до роботи.")

    def _create_menu(self):
        menu_bar = self.menuBar()
        action_menu = menu_bar.addMenu("Дії")

        act_run = QAction("Запустити обчислення...", self)
        act_run.triggered.connect(self._start_workflow)
        action_menu.addAction(act_run)

        act_exit = QAction("Вихід", self)
        act_exit.triggered.connect(self.close)
        action_menu.addAction(act_exit)

    def _log(self, text: str):
        self.log_edit.append(f"[{time.strftime('%H:%M:%S')}] {text}")

    def _start_workflow(self):
        dialog = ParamsDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            self._log("Введення параметрів скасовано.")
            return

        n_pts, x_min, x_max, y_min, y_max = dialog.get_params()
        self._log(f"Параметри: N={n_pts}, X=[{x_min}..{x_max}], Y=[{y_min}..{y_max}]")

        self._log("Перевірка та виклик програм Object2 та Object3...")
        self._ensure_running(self.SERVER_OBJ2, "Object2.py")
        self._ensure_running(self.SERVER_OBJ3, "Object3.py")

        self._arrange_windows()

        self._log("Надсилаємо параметри в Object2...")
        cmd_obj2 = f"GENERATE {n_pts} {x_min} {x_max} {y_min} {y_max}"
        resp2 = self._send_ipc_message(self.SERVER_OBJ2, cmd_obj2)

        if resp2 != "DONE":
            self._log(f"Помилка зв'язку з Object2: {resp2}")
            return
        self._log("Object2: числа згенеровано та записано в буфер обміну!")

        self._log("Надсилаємо команду 'DRAW' у програму Object3...")
        resp3 = self._send_ipc_message(self.SERVER_OBJ3, "DRAW")

        if resp3 != "DONE":
            self._log(f"Помилка зв'язку з Object3: {resp3}")
            return
        self._log("Object3: графік y=f(x) успішно побудовано!")
        self._log(">>> Роботу сеансу успішно завершено! <<<\n")

    def _send_ipc_message(self, server_name: str, message: str) -> str:
        socket = QLocalSocket()
        socket.connectToServer(server_name)
        if not socket.waitForConnected(1500):
            return "ERROR_CONNECT"

        socket.write(message.encode("utf-8"))
        socket.flush()

        if not socket.waitForReadyRead(3000):
            socket.disconnectFromServer()
            return "TIMEOUT"

        response = socket.readAll().data().decode("utf-8").strip()
        socket.disconnectFromServer()
        return response

    def _ensure_running(self, server_name: str, script_name: str):
        socket = QLocalSocket()
        socket.connectToServer(server_name)
        if socket.waitForConnected(300):
            socket.disconnectFromServer()
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, script_name)
        subprocess.Popen([sys.executable, script_path])

        for _ in range(20):
            QApplication.processEvents()
            time.sleep(0.1)
            socket.connectToServer(server_name)
            if socket.waitForConnected(300):
                socket.disconnectFromServer()
                break

    def _arrange_windows(self):
        self.move(50, 150)

        try:
            import ctypes
            hwnd_obj2 = ctypes.windll.user32.FindWindowW(None, "Object2 — Генератор даних (Варіант 0)")
            if hwnd_obj2:
                ctypes.windll.user32.MoveWindow(hwnd_obj2, 530, 150, 480, 480, True)

            hwnd_obj3 = ctypes.windll.user32.FindWindowW(None, "Object3 — Візуалізатор графіка y=f(x) (Варіант 0)")
            if hwnd_obj3:
                ctypes.windll.user32.MoveWindow(hwnd_obj3, 1030, 150, 780, 480, True)
        except Exception:
            pass

    def closeEvent(self, event):
        self._send_ipc_message(self.SERVER_OBJ2, "EXIT")
        self._send_ipc_message(self.SERVER_OBJ3, "EXIT")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Lab6MainWindow()
    window.show()
    sys.exit(app.exec())