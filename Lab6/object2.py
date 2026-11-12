import sys
import os

os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtCore import Qt


class Object2Window(QMainWindow):
    SERVER_NAME = "Lab6_Object2_Server"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Object2 — Генератор даних (Варіант 0)")
        self.resize(360, 480)

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.status_label = QLabel("Стан: Очікування команди від Lab6...")
        self.status_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.status_label)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["№", "X", "Y"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self._init_server()

    def _init_server(self):
        self.server = QLocalServer(self)
        QLocalServer.removeServer(self.SERVER_NAME)

        if not self.server.listen(self.SERVER_NAME):
            self.status_label.setText(f"Помилка запуску IPC сервера: {self.server.errorString()}")
        else:
            self.server.newConnection.connect(self._on_new_connection)

    def _on_new_connection(self):
        socket = self.server.nextPendingConnection()
        socket.readyRead.connect(lambda: self._read_message(socket))

    def _read_message(self, socket: QLocalSocket):
        data = socket.readAll().data().decode("utf-8").strip()
        parts = data.split()

        if not parts:
            return

        command = parts[0]

        if command == "GENERATE":

            try:
                n_points = int(parts[1])
                x_min = int(parts[2])
                x_max = int(parts[3])
                y_min = int(parts[4])
                y_max = int(parts[5])

                points = self._generate_points(n_points, x_min, x_max, y_min, y_max)
                
                self._display_points(points)

                self._copy_to_clipboard(points)

                socket.write(b"DONE\n")
                socket.flush()

                self.status_label.setText(f"Згенеровано {n_points} точок. Дані в буфері обміну")
            except Exception as e:
                self.status_label.setText(f"Помилка даних: {e}")

        elif command == "EXIT":
            self.close()

    def _generate_points(self, n: int, x_min: int, x_max: int, y_min: int, y_max: int) -> list[tuple[int, int]]:
        points = []
        for _ in range(n):
            x = random.randint(min(x_min, x_max), max(x_min, x_max))
            y = random.randint(min(y_min, y_max), max(y_min, y_max))
            points.append((x, y))
        return points

    def _display_points(self, points: list[tuple[int, int]]):
        self.table.setRowCount(0)
        for idx, (x, y) in enumerate(points):
            self.table.insertRow(idx)

            item_idx = QTableWidgetItem(str(idx + 1))
            item_x = QTableWidgetItem(str(x))
            item_y = QTableWidgetItem(str(y))

            for item in (item_idx, item_x, item_y):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(idx, 0, item_idx)
            self.table.setItem(idx, 1, item_x)
            self.table.setItem(idx, 2, item_y)

    def _copy_to_clipboard(self, points: list[tuple[int, int]]):

        clipboard = QApplication.clipboard()
        lines = ["x\ty"]
        for x, y in points:
            lines.append(f"{x}\t{y}")
        
        text_data = "\n".join(lines)
        clipboard.setText(text_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Object2Window()
    window.show()
    sys.exit(app.exec())