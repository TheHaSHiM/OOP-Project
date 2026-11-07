import sys
import os

os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QMessageBox, QFileDialog
)
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
from my_table import MyTable


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(850, 600)

        self.editor = MyEditor.get_instance()
        self.current_title_name = "Крапка"

        self.table_window = MyTable(self)

        self.table_window.shape_selected.connect(self._on_shape_selected_in_table)

        self.table_window.shape_deleted.connect(self._on_shape_deleted_in_table)


        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._update_title()


        self.table_window.show()

    def _create_shape_icon(self, shape_type: str) -> QIcon:
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))

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
            painter.drawRect(4, 8, 11, 11)
            painter.drawRect(9, 4, 11, 11)
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
            ("point", "Крапка", PointShape, "Крапка"),
            ("line", "Лінія", LineShape, "Пряма лінія"),
            ("rect", "Прямокутник", RectShape, "Прямокутник (від центру)"),
            ("ellipse", "Еліпс", EllipseShape, "Еліпс (по 2 кутах)"),
            ("line_oo", "Лінія з кружечками", LineOOShape, "Лінія з кружечками"),
            ("cube", "Каркас куба", CubeShape, "Каркас 3D-куба")
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
        self.editor.start(shape_cls())
        self.current_title_name = name
        self._update_title()

    def _update_title(self):
        self.setWindowTitle(f"Графічний редактор (Лаб 5, Singleton) - [{self.current_title_name}]")

    def _create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Файл")

        save_action = QAction("Зберегти у файл...", self)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

        load_action = QAction("Завантажити з файлу...", self)
        load_action.triggered.connect(self._load_file)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        exit_action = QAction("Вихід", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        objects_menu = menu_bar.addMenu("Об'єкти")
        for act in self.actions:
            objects_menu.addAction(act)

        table_menu = menu_bar.addMenu("Таблиця")
        self.act_toggle_table = QAction("Показати/Сховати таблицю", self)
        self.act_toggle_table.triggered.connect(self._toggle_table)
        table_menu.addAction(self.act_toggle_table)

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

    def _toggle_table(self):
        if self.table_window.isVisible():
            self.table_window.hide()
        else:
            self.table_window.show()


    def _on_shape_selected_in_table(self, index: int):
        self.editor.set_selected_index(index)
        self.update()

    def _on_shape_deleted_in_table(self, index: int):
        if self.editor.delete_shape(index):
            self.table_window.remove_row(index)
            self.update()

    def _save_file(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Зберегти фігури", "shapes.txt", "Текстові файли (*.txt);;Всі файли (*)"
        )
        if filepath:
            self.editor.save_to_file(filepath)
            QMessageBox.information(self, "Успіх", "Фігури успішно збережено у файл!")

    def _load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Завантажити фігури", "", "Текстові файли (*.txt);;Всі файли (*)"
        )
        if filepath:
            records = self.editor.load_from_file(filepath)
            self.table_window.clear_table()
            for rec in records:
                self.table_window.add(rec[0], rec[1], rec[2], rec[3], rec[4])
            self.update()
            QMessageBox.information(self, "Успіх", f"Завантажено {len(records)} фігур!")

    def _show_about(self):
        QMessageBox.about(
            self,
            "Про програму",
            "Лабораторна робота №5\n"
            "Тема: Багатовіконний інтерфейс, Таблиця та Singleton\n"
        )

    def closeEvent(self, event: QCloseEvent):
        self.table_window.close()
        self.editor.destroy()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.on_lb_down(int(event.position().x()), int(event.position().y()))
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        self.editor.on_mouse_move(int(event.position().x()), int(event.position().y()))
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:

            new_shape = self.editor.on_lb_up(int(event.position().x()), int(event.position().y()))
            if new_shape is not None:
                name = self.editor._get_shape_display_name(new_shape)
                self.table_window.add(name, new_shape.xs1, new_shape.ys1, new_shape.xs2, new_shape.ys2)
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