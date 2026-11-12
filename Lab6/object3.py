import sys
import os

os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtCore import Qt, QPointF


class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points: list[tuple[int, int]] = []

    def set_points(self, points: list[tuple[int, int]]):
        self.points = sorted(points, key=lambda pt: pt[0])
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if len(self.points) < 2:
            painter.setPen(Qt.GlobalColor.gray)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Очікування даних від Lab6 для побудови графіка...")
            painter.end()
            return

        margin_left = 60
        margin_bottom = 50
        margin_top = 40
        margin_right = 40

        w = self.width() - margin_left - margin_right
        h = self.height() - margin_top - margin_bottom

        xs = [pt[0] for pt in self.points]
        ys = [pt[1] for pt in self.points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max(1, max_x - min_x)
        span_y = max(1, max_y - min_y)

        def to_screen(x, y):
            px = margin_left + (x - min_x) / span_x * w
            py = margin_top + h - (y - min_y) / span_y * h
            return QPointF(px, py)


        grid_pen = QPen(QColor(220, 220, 220), 1, Qt.PenStyle.DashLine)
        axis_pen = QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine)
        text_pen = QPen(Qt.GlobalColor.black)

        painter.setFont(QFont("Arial", 9))

        for val in (min_x, (min_x + max_x) // 2, max_x):
            pt = to_screen(val, min_y)
            painter.setPen(grid_pen)
            painter.drawLine(int(pt.x()), margin_top, int(pt.x()), margin_top + h)
            painter.setPen(text_pen)
            painter.drawText(int(pt.x()) - 20, margin_top + h + 20, 40, 20, Qt.AlignmentFlag.AlignCenter, str(val))

        for val in (min_y, (min_y + max_y) // 2, max_y):
            pt = to_screen(min_x, val)
            painter.setPen(grid_pen)
            painter.drawLine(margin_left, int(pt.y()), margin_left + w, int(pt.y()))
            painter.setPen(text_pen)
            painter.drawText(5, int(pt.y()) - 10, 45, 20, Qt.AlignmentFlag.AlignRight, str(val))


        painter.setPen(axis_pen)

        painter.drawLine(margin_left, margin_top + h, margin_left + w + 15, margin_top + h)

        painter.drawLine(margin_left + w + 15, margin_top + h, margin_left + w + 5, margin_top + h - 5)
        painter.drawLine(margin_left + w + 15, margin_top + h, margin_left + w + 5, margin_top + h + 5)
        painter.drawText(margin_left + w + 20, margin_top + h + 5, "X")

       
        painter.drawLine(margin_left, margin_top + h, margin_left, margin_top - 15)

        painter.drawLine(margin_left, margin_top - 15, margin_left - 5, margin_top - 5)
        painter.drawLine(margin_left, margin_top - 15, margin_left + 5, margin_top - 5)
        painter.drawText(margin_left - 15, margin_top - 20, "Y")

        line_pen = QPen(QColor(0, 102, 204), 2, Qt.PenStyle.SolidLine)
        painter.setPen(line_pen)

        screen_points = [to_screen(x, y) for x, y in self.points]
        for i in range(len(screen_points) - 1):
            painter.drawLine(screen_points[i], screen_points[i + 1])


        point_brush = QBrush(Qt.GlobalColor.red)
        painter.setBrush(point_brush)
        painter.setPen(QPen(Qt.GlobalColor.darkRed, 1))
        for pt in screen_points:
            painter.drawEllipse(pt, 4.0, 4.0)

        painter.end()


class Object3Window(QMainWindow):
    SERVER_NAME = "Lab6_Object3_Server"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Object3 — Візуалізатор графіка y=f(x) (Варіант 0)")
        self.resize(550, 480)

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.status_label = QLabel("Стан: Очікування повідомлення від Lab6...")
        self.status_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.status_label)

        self.graph_widget = GraphWidget()
        layout.addWidget(self.graph_widget)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self._init_server()

    def _init_server(self):
        self.server = QLocalServer(self)
        QLocalServer.removeServer(self.SERVER_NAME)
        if not self.server.listen(self.SERVER_NAME):
            self.status_label.setText(f"Помилка IPC: {self.server.errorString()}")
        else:
            self.server.newConnection.connect(self._on_new_connection)

    def _on_new_connection(self):
        socket = self.server.nextPendingConnection()
        socket.readyRead.connect(lambda: self._read_message(socket))

    def _read_message(self, socket: QLocalSocket):
        data = socket.readAll().data().decode("utf-8").strip()

        if data == "DRAW":

            points = self._read_from_clipboard()
            if points:

                self.graph_widget.set_points(points)
                self.status_label.setText(f"Побудовано графік за {len(points)} точками з буфера обміну!")
                socket.write(b"DONE\n")
                socket.flush()
            else:
                self.status_label.setText("Помилка: буфер обміну порожній або містить некоректні дані.")

        elif data == "EXIT":
            self.close()

    def _read_from_clipboard(self) -> list[tuple[int, int]]:
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if not text:
            return []

        points = []
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line or line.startswith("x"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    x = int(parts[0])
                    y = int(parts[1])
                    points.append((x, y))
                except ValueError:
                    continue
        return points


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Object3Window()
    window.show()
    sys.exit(app.exec())