from abc import ABC, abstractmethod
from typing import Optional
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt

from shape import Shape, PointShape, LineShape, RectShape, EllipseShape


class ShapeEditor(ABC):

    def __init__(self):
        self.x1: int = 0
        self.y1: int = 0
        self.x2: int = 0
        self.y2: int = 0
        self.is_drawing: bool = False 

    def on_lb_down(self, x: int, y: int):
        self.x1 = self.x2 = x
        self.y1 = self.y2 = y
        self.is_drawing = True

    def on_mouse_move(self, x: int, y: int):

        if self.is_drawing:
            self.x2 = x
            self.y2 = y

    @abstractmethod
    def on_lb_up(self, x: int, y: int) -> Optional[Shape]:
        pass

    @abstractmethod
    def on_paint(self, painter: QPainter):
        pass

    def _get_rubber_band_pen(self) -> QPen:

        return QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine)


class PointEditor(ShapeEditor):
    
    def on_lb_up(self, x: int, y: int) -> Optional[Shape]:
        if not self.is_drawing:
            return None
        self.is_drawing = False
        shape = PointShape()
        shape.set(x, y, x, y)
        return shape

    def on_paint(self, painter: QPainter):

        pass


class LineEditor(ShapeEditor):
    
    def on_lb_up(self, x: int, y: int) -> Optional[Shape]:
        if not self.is_drawing:
            return None
        self.is_drawing = False
        self.x2, self.y2 = x, y
        shape = LineShape()
        shape.set(self.x1, self.y1, self.x2, self.y2)
        return shape

    def on_paint(self, painter: QPainter):
        if self.is_drawing:
            painter.setPen(self._get_rubber_band_pen())
            painter.drawLine(self.x1, self.y1, self.x2, self.y2)


class RectEditor(ShapeEditor):

    def on_lb_up(self, x: int, y: int) -> Optional[Shape]:
        if not self.is_drawing:
            return None
        self.is_drawing = False
        self.x2, self.y2 = x, y
        shape = RectShape()
        shape.set(self.x1, self.y1, self.x2, self.y2)
        return shape

    def on_paint(self, painter: QPainter):
        if self.is_drawing:
            painter.setPen(self._get_rubber_band_pen())
            painter.setBrush(Qt.BrushStyle.NoBrush) 

            top_left_x = min(self.x1, self.x2)
            top_left_y = min(self.y1, self.y2)
            width = abs(self.x2 - self.x1)
            height = abs(self.y2 - self.y1)
            painter.drawRect(top_left_x, top_left_y, width, height)


class EllipseEditor(ShapeEditor):

    def on_lb_up(self, x: int, y: int) -> Optional[Shape]:
        if not self.is_drawing:
            return None
        self.is_drawing = False
        self.x2, self.y2 = x, y
        shape = EllipseShape()
        shape.set(self.x1, self.y1, self.x2, self.y2)
        return shape

    def on_paint(self, painter: QPainter):
        if self.is_drawing:
            painter.setPen(self._get_rubber_band_pen())
            painter.setBrush(Qt.BrushStyle.NoBrush)


            rx = abs(self.x2 - self.x1)
            ry = abs(self.y2 - self.y1)
            painter.drawEllipse(self.x1 - rx, self.y1 - ry, rx * 2, ry * 2)