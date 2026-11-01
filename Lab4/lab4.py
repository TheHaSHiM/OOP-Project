import sys
import os

os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

from typing import Optional
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QMessageBox
from PyQt6.QtGui import (
    QAction, QActionGroup, QPainter, QPixmap, QIcon, QPen, QBrush, 
    QColor, QMouseEvent, QPaintEvent, QCloseEvent
)
from PyQt6.QtCore import Qt, QSize

from shape import (
    PointShape, LineShape, RectShape, EllipseShape, 
    LineOOShape, CubeShape
)
from my_editor import MyEditor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(900, 650)
        self.editor: Optional[MyEditor] = MyEditor()
        self.current_title_name: str = "Крапка"

        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._update_title()

    def _create_shape_icon(self, shape_type: str) -> QIcon:
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        if shape_type == "point":
            painter.setPen(QPen(Qt.GlobalColor.black, 4, Qt.PenStyle.SolidLine))
            painter.drawPoint(12, 12)

        elif shape_type == "line":
            painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))
            painter.drawLine(4, 20, 20, 4)

        elif shape_type == "rect":
            painter.setBrush(QBrush(QColor(255, 0, 255)))
            painter.drawRect(4, 5, 16, 14)

        elif shape_type == "ellipse":
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            painter.drawEllipse(3, 5, 18, 14)

        elif shape_type == "line_oo":
            painter.drawLine(6, 18, 18, 6)
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            painter.drawEllipse(3, 15, 6, 6)
            painter.drawEllipse(15, 3, 6, 6)

        elif shape_type == "cube":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(4, 8, 11, 11)   # Передня грань
            painter.drawRect(9, 4, 11, 11)   # Задня грань
            painter.drawLine(4, 8, 9, 4)
            painter.drawLine(15, 8, 20, 4)
            painter.drawLine(4, 19, 9, 15)
            painter.drawLine(15, 19, 20, 15)

        painter.end()
        return QIcon(pixmap)

    def _create_actions(self):
        self.tools_group = QActionGroup(self)
        self.tools_group.setExclusive(True)

        tools_data = [
            ("point", "Крапка", PointShape, "Інструмент: Крапка"),
            ("line", "Лінія", LineShape, "Інструмент: Пряма лінія"),
            ("rect", "Прямокутник", RectShape, "Інструмент: Прямокутник (від центру)"),
            ("ellipse", "Еліпс", EllipseShape, "Інструмент: Еліпс (по 2 кутах)"),
            ("line_oo", "Лінія з кружечками", LineOOShape, "Інструмент: Лінія з кружечками на кінцях"),
            ("cube", "Каркас куба", CubeShape, "Інструмент: Каркас 3D-куба")
        ]

        self.actions = []
        for code, name, shape_cls, tooltip in tools_data:
            act = QAction(self._create_shape_icon(code), name, self)
            act.setCheckable(True)
            act.setToolTip(tooltip)
            act.triggered.connect(lambda checked, cls=shape_cls, n=name: self._select_tool(cls, n))
            self.tools_group.addAction(act)
            self.actions.append(act)

        self.actions[0].setChecked(True)

    def _select_tool(self, shape_cls, name: str):
        if self.editor is not None:
            self.editor.start(shape_cls())
            self.current_title_name = name
            self._update_title()

    def _update_title(self):
        self.setWindowTitle(f"Графічний редактор (Лаб 4) - [{self.current_title_name}]")

    def _create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Файл")
        exit_action = QAction("Вихід", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        objects_menu = menu_bar.addMenu("Об'єкти")
        for act in self.actions:
            objects_menu.addAction(act)

        help_menu = menu_bar.addMenu("Довідка")
        about_action = QAction("Про програму", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        toolbar = QToolBar("Панель інструментів", self)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        for act in self.actions:
            toolbar.addAction(act)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

    def _show_about(self):
        QMessageBox.about(
            self,
            "Про програму",
            "Лабораторна робота №4\n"
            "Тема: Вдосконалення структури коду графічного редактора (Рефакторинг)\n"
        )

    def closeEvent(self, event: QCloseEvent):
        if self.editor is not None:
            self.editor.destroy()
            self.editor = None
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.editor is not None:
            self.editor.on_lb_down(int(event.position().x()), int(event.position().y()))
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.editor is not None:
            self.editor.on_mouse_move(int(event.position().x()), int(event.position().y()))
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.editor is not None:
            self.editor.on_lb_up(int(event.position().x()), int(event.position().y()))
            self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        if self.editor is not None:
            self.editor.on_paint(painter)
        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())