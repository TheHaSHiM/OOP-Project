import sys
import os

os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QMessageBox
from PyQt6.QtGui import (
    QAction, QActionGroup, QPainter, QPixmap, QIcon, QPen, QBrush, 
    QColor, QMouseEvent, QPaintEvent
)
from PyQt6.QtCore import Qt, QSize

from shape_editor import ShapeObjectsEditor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)

       
        self.editor = ShapeObjectsEditor()

      
        self._create_actions()
        self._create_menu()
        self._create_toolbar()

        self._update_title()

    def _create_shape_icon(self, shape_type: str) -> QIcon:

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if shape_type == "point":
            painter.setPen(QPen(Qt.GlobalColor.black, 4, Qt.PenStyle.SolidLine))
            painter.drawPoint(12, 12)
        elif shape_type == "line":
            painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))
            painter.drawLine(4, 20, 20, 4)
        elif shape_type == "rect":
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            painter.setBrush(QBrush(QColor(255, 0, 255)))  
            painter.drawRect(4, 5, 16, 14)
        elif shape_type == "ellipse":
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
            painter.setBrush(QBrush(Qt.GlobalColor.white))  
            painter.drawEllipse(3, 5, 18, 14)

        painter.end()
        return QIcon(pixmap)

    def _create_actions(self):

        self.tools_group = QActionGroup(self)
        self.tools_group.setExclusive(True)

        self.act_point = QAction(self._create_shape_icon("point"), "Крапка", self)
        self.act_point.setCheckable(True)
        self.act_point.setToolTip("Інструмент: Крапка")
        self.act_point.triggered.connect(lambda: self._select_tool(self.editor.start_point_editor))

        self.act_line = QAction(self._create_shape_icon("line"), "Лінія", self)
        self.act_line.setCheckable(True)
        self.act_line.setToolTip("Інструмент: Пряма лінія")
        self.act_line.triggered.connect(lambda: self._select_tool(self.editor.start_line_editor))

        self.act_rect = QAction(self._create_shape_icon("rect"), "Прямокутник", self)
        self.act_rect.setCheckable(True)
        self.act_rect.setToolTip("Інструмент: Прямокутник (ввід від центру)")
        self.act_rect.triggered.connect(lambda: self._select_tool(self.editor.start_rect_editor))

        self.act_ellipse = QAction(self._create_shape_icon("ellipse"), "Еліпс", self)
        self.act_ellipse.setCheckable(True)
        self.act_ellipse.setToolTip("Інструмент: Еліпс (ввід по 2 кутах)")
        self.act_ellipse.triggered.connect(lambda: self._select_tool(self.editor.start_ellipse_editor))

        self.actions = [self.act_point, self.act_line, self.act_rect, self.act_ellipse]
        for act in self.actions:
            self.tools_group.addAction(act)

        self.act_point.setChecked(True)

    def _select_tool(self, tool_func):
        tool_func()
        self._update_title()

    def _update_title(self):

        self.setWindowTitle(f"Графічний редактор - [{self.editor.current_tool_name}]")

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
            "Лабораторна робота №3\n"
            "Тема: Розробка інтерфейсу користувача (Toolbar та Tooltips)\n"
        )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.on_lb_down(int(event.position().x()), int(event.position().y()))
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        self.editor.on_mouse_move(int(event.position().x()), int(event.position().y()))
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.on_lb_up(int(event.position().x()), int(event.position().y()))
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