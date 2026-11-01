from typing import Optional
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt

from shape import Shape, PointShape


class MyEditor:

    MAX_SHAPES: int = 121

    def __init__(self):
        self.pcshape: list[Shape] = []

        self.current_shape: Optional[Shape] = None

        self.x1: int = 0
        self.y1: int = 0
        self.x2: int = 0
        self.y2: int = 0
        self.is_drawing: bool = False

        self.rubber_pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine)

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

    def on_lb_up(self, x: int, y: int):
        if not self.is_drawing:
            return
        self.is_drawing = False
        self.x2 = x
        self.y2 = y

        if self.current_shape is not None:
            self.current_shape.set(self.x1, self.y1, self.x2, self.y2)

            if len(self.pcshape) < self.MAX_SHAPES:
                self.pcshape.append(self.current_shape)

            self.current_shape = self.current_shape.__class__()


    def on_paint(self, painter: QPainter):
        for shape in self.pcshape:
            shape.show(painter)

        if self.is_drawing and self.current_shape is not None:
            self.current_shape.show(painter, pen=self.rubber_pen, brush=Qt.BrushStyle.NoBrush)


    def destroy(self):
        self.pcshape.clear()
        self.current_shape = None
        print("MyEditor: динамічний об'єкт коректно знищено")