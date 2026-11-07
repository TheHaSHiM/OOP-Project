from typing import Optional
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt

from shape import (
    Shape, PointShape, LineShape, RectShape, 
    EllipseShape, LineOOShape, CubeShape
)

class MyEditor:
    _instance: Optional['MyEditor'] = None
    MAX_SHAPES: int = 121

    SHAPE_FACTORY = {
        "Крапка": PointShape,
        "Лінія": LineShape,
        "Прямокутник": RectShape,
        "Еліпс": EllipseShape,
        "Лінія з кружечками": LineOOShape,
        "Куб": CubeShape,
        
        "PointShape": PointShape,
        "LineShape": LineShape,
        "RectShape": RectShape,
        "EllipseShape": EllipseShape,
        "LineOOShape": LineOOShape,
        "CubeShape": CubeShape
    }

    @classmethod
    def get_instance(cls) -> 'MyEditor':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if MyEditor._instance is not None:
            raise RuntimeError("Помилка! Це клас Singleton. Використовуйте MyEditor.get_instance()")

        self.pcshape: list[Shape] = []
        self.current_shape: Optional[Shape] = None

        self.x1: int = 0
        self.y1: int = 0
        self.x2: int = 0
        self.y2: int = 0
        self.is_drawing: bool = False

        self.rubber_pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine)

        self.selected_index: int = -1
        self.highlight_pen = QPen(QColor(0, 120, 255), 3, Qt.PenStyle.DashDotLine)

        self.start(PointShape())

    def start(self, shape_prototype: Shape):
        self.current_shape = shape_prototype

    def on_lb_down(self, x: int, y: int):
        self.x1 = self.x2 = x
        self.y1 = self.y2 = y
        self.is_drawing = True
        if self.current_shape:
            self.current_shape.set(x, y, x, y)

    def on_mouse_move(self, x: int, y: int):
        if self.is_drawing:
            self.x2 = x
            self.y2 = y
            if self.current_shape:
                self.current_shape.set(self.x1, self.y1, self.x2, self.y2)

    def on_lb_up(self, x: int, y: int) -> Optional[Shape]:
        if not self.is_drawing:
            return None
        self.is_drawing = False
        self.x2 = x
        self.y2 = y

        created_shape = None
        if self.current_shape is not None:
            self.current_shape.set(self.x1, self.y1, self.x2, self.y2)

            if len(self.pcshape) < self.MAX_SHAPES:
                self.pcshape.append(self.current_shape)
                created_shape = self.current_shape

            self.current_shape = self.current_shape.__class__()

        return created_shape

    def on_paint(self, painter: QPainter):
        for idx, shape in enumerate(self.pcshape):
            if idx == self.selected_index:
                shape.show(painter, pen=self.highlight_pen)
            else:
                shape.show(painter)

        if self.is_drawing and self.current_shape is not None:
            self.current_shape.show(painter, pen=self.rubber_pen, brush=Qt.BrushStyle.NoBrush)

    def set_selected_index(self, index: int):
        self.selected_index = index

    def delete_shape(self, index: int) -> bool:
        if 0 <= index < len(self.pcshape):
            del self.pcshape[index]
            self.selected_index = -1
            return True
        return False

    def save_to_file(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            for shape in self.pcshape:
                name = self._get_shape_display_name(shape)
                line = f"{name}\t{shape.xs1}\t{shape.ys1}\t{shape.xs2}\t{shape.ys2}\n"
                f.write(line)

    def load_from_file(self, filepath: str) -> list[tuple[str, int, int, int, int]]:
        self.pcshape.clear()
        self.selected_index = -1
        loaded_records = []

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 5:
                    name, x1, y1, x2, y2 = parts[0], int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                    shape_class = self.SHAPE_FACTORY.get(name)
                    if shape_class:
                        shape = shape_class()
                        shape.set(x1, y1, x2, y2)
                        self.pcshape.append(shape)
                        loaded_records.append((name, x1, y1, x2, y2))

        return loaded_records

    def _get_shape_display_name(self, shape: Shape) -> str:
        name_map = {
            "PointShape": "Крапка",
            "LineShape": "Лінія",
            "RectShape": "Прямокутник",
            "EllipseShape": "Еліпс",
            "LineOOShape": "Лінія з кружечками",
            "CubeShape": "Куб"
        }
        return name_map.get(shape.__class__.__name__, shape.__class__.__name__)

    def destroy(self):
        self.pcshape.clear()
        self.current_shape = None
        MyEditor._instance = None