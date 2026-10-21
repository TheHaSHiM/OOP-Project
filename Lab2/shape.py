from abc import ABC, abstractmethod
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt

class Shape(ABC):

    def __init__(self):
        self.xs1: int = 0
        self.ys1: int = 0
        self.xs2: int = 0
        self.ys2: int = 0

    def set(self, x1: int, y1: int, x2: int, y2: int):

        self.xs1 = x1
        self.ys1 = y1
        self.xs2 = x2
        self.ys2 = y2

    @abstractmethod
    def show(self, painter: QPainter):

        pass


class PointShape(Shape):

    def show(self, painter: QPainter):
        
        pen = QPen(Qt.GlobalColor.black, 3, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawPoint(self.xs1, self.ys1)


class LineShape(Shape):

    def show(self, painter: QPainter):
        
        pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.xs1, self.ys1, self.xs2, self.ys2)


class RectShape(Shape):

    def show(self, painter: QPainter):
        pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine)
        brush = QBrush(Qt.GlobalColor.white) 

        painter.setPen(pen)
        painter.setBrush(brush)

        top_left_x = min(self.xs1, self.xs2)
        top_left_y = min(self.ys1, self.ys2)
        width = abs(self.xs2 - self.xs1)
        height = abs(self.ys2 - self.ys1)

        painter.drawRect(top_left_x, top_left_y, width, height)


class EllipseShape(Shape):

    def show(self, painter: QPainter):
        pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)


        rx = abs(self.xs2 - self.xs1)
        ry = abs(self.ys2 - self.ys1)


        top_left_x = self.xs1 - rx
        top_left_y = self.ys1 - ry
        width = rx * 2
        height = ry * 2

        painter.drawEllipse(top_left_x, top_left_y, width, height)