from abc import ABC, abstractmethod
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt
from typing import Optional

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
    def show(self, painter: QPainter, pen: Optional[QPen] = None, brush: Optional[QBrush] = None):
        pass


class PointShape(Shape):
    def show(self, painter: QPainter, pen: Optional[QPen] = None, brush: Optional[QBrush] = None):
        painter.setPen(pen if pen else QPen(Qt.GlobalColor.black, 4, Qt.PenStyle.SolidLine))
        painter.drawPoint(self.xs1, self.ys1)


class LineShape(Shape):
    def show(self, painter: QPainter, pen: Optional[QPen] = None, brush: Optional[QBrush] = None):
        painter.setPen(pen if pen else QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
        painter.drawLine(self.xs1, self.ys1, self.xs2, self.ys2)


class RectShape(Shape):
    def __init__(self):
        super().__init__()
        self.brush = QBrush(QColor(255, 0, 255))

    def show(self, painter: QPainter, pen: Optional[QPen] = None, brush: Optional[QBrush] = None):
        painter.setPen(pen if pen else QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(brush if brush is not None else self.brush)

        dx = abs(self.xs2 - self.xs1)
        dy = abs(self.ys2 - self.ys1)
        top_left_x = self.xs1 - dx
        top_left_y = self.ys1 - dy
        width = dx * 2
        height = dy * 2

        painter.drawRect(top_left_x, top_left_y, width, height)


class EllipseShape(Shape):
    def __init__(self):
        super().__init__()
        self.brush = QBrush(Qt.GlobalColor.white)

    def show(self, painter: QPainter, pen: Optional[QPen] = None, brush: Optional[QBrush] = None):
        painter.setPen(pen if pen else QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
        painter.setBrush(brush if brush is not None else self.brush)

        top_left_x = min(self.xs1, self.xs2)
        top_left_y = min(self.ys1, self.ys2)
        width = abs(self.xs2 - self.xs1)
        height = abs(self.ys2 - self.ys1)

        painter.drawEllipse(top_left_x, top_left_y, width, height)


class LineOOShape(LineShape, EllipseShape):
    
    def __init__(self):
        super().__init__()
        self.brush = QBrush(Qt.GlobalColor.white)

    def show(self, painter: QPainter, pen: Optional[QPen] = None, brush: Optional[QBrush] = None):
        orig_x1, orig_y1 = self.xs1, self.ys1
        orig_x2, orig_y2 = self.xs2, self.ys2

        LineShape.show(self, painter, pen, brush)
        r = 6

        self.set(orig_x1 - r, orig_y1 - r, orig_x1 + r, orig_y1 + r)
        EllipseShape.show(self, painter, pen, brush)

        self.set(orig_x2 - r, orig_y2 - r, orig_x2 + r, orig_y2 + r)
        EllipseShape.show(self, painter, pen, brush)

        self.set(orig_x1, orig_y1, orig_x2, orig_y2)


class CubeShape(LineShape, RectShape):
    
    def __init__(self):
        super().__init__()
        self.brush = Qt.BrushStyle.NoBrush

    def show(self, painter: QPainter, pen: Optional[QPen] = None, brush: Optional[QBrush] = None):
        orig_x1, orig_y1 = self.xs1, self.ys1
        orig_x2, orig_y2 = self.xs2, self.ys2

        # передня грань
        dx = abs(orig_x2 - orig_x1)
        dy = abs(orig_y2 - orig_y1)

        # зсув
        offset_x = dx // 2
        offset_y = -(dy // 2)

        # задня грань
        self.set(orig_x1 + offset_x, orig_y1 + offset_y, orig_x2 + offset_x, orig_y2 + offset_y)
        RectShape.show(self, painter, pen, brush)

        f_tl = (orig_x1 - dx, orig_y1 - dy) 
        f_tr = (orig_x1 + dx, orig_y1 - dy) 
        f_bl = (orig_x1 - dx, orig_y1 + dy) 
        f_br = (orig_x1 + dx, orig_y1 + dy)  

        corners = [f_tl, f_tr, f_bl, f_br]
        for cx, cy in corners:
            self.set(cx, cy, cx + offset_x, cy + offset_y)
            LineShape.show(self, painter, pen, brush)

        # передня грань
        self.set(orig_x1, orig_y1, orig_x2, orig_y2)
        RectShape.show(self, painter, pen, brush)