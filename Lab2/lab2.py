import sys
import os

os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"


from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtGui import QAction, QActionGroup, QPainter, QMouseEvent, QPaintEvent
from PyQt6.QtCore import Qt

from shape_editor import ShapeObjectsEditor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторна робота №2 — Графічний редактор (Варіант 20)")
        self.resize(800, 600)

        self.editor = ShapeObjectsEditor()

        self._create_menu()

    def _create_menu(self):
        menu_bar = self.menuBar()
        

        file_menu = menu_bar.addMenu("Файл")
        exit_action = QAction("Вихід", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        objects_menu = menu_bar.addMenu("Об'єкти")

        self.tools_group = QActionGroup(self)
        self.tools_group.setExclusive(True)

        self.act_point = QAction("Крапка", self, checkable=True)
        self.act_line = QAction("Лінія", self, checkable=True)
        self.act_rect = QAction("Прямокутник", self, checkable=True)
        self.act_ellipse = QAction("Еліпс", self, checkable=True)

        self.act_point.triggered.connect(self.editor.start_point_editor)
        self.act_line.triggered.connect(self.editor.start_line_editor)
        self.act_rect.triggered.connect(self.editor.start_rect_editor)
        self.act_ellipse.triggered.connect(self.editor.start_ellipse_editor)

        for act in (self.act_point, self.act_line, self.act_rect, self.act_ellipse):
            self.tools_group.addAction(act)
            objects_menu.addAction(act)

        self.act_point.setChecked(True)

        help_menu = menu_bar.addMenu("Довідка")
        about_action = QAction("Про програму", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_about(self):
        QMessageBox.about(
            self,
            "Про програму",
            "Лабораторна робота №2\n"
            "Тема: Розробка графічного редактора об'єктів"
        )

    def mousePressEvent(self, event: QMouseEvent):

        if event.button() == Qt.MouseButton.LeftButton:
            x = int(event.position().x())
            y = int(event.position().y())
            self.editor.on_lb_down(x, y)
            self.update() 

    def mouseMoveEvent(self, event: QMouseEvent):

        x = int(event.position().x())
        y = int(event.position().y())
        self.editor.on_mouse_move(x, y)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):

        if event.button() == Qt.MouseButton.LeftButton:
            x = int(event.position().x())
            y = int(event.position().y())
            self.editor.on_lb_up(x, y)
            self.update()  

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        self.editor.on_paint(painter)  
        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())