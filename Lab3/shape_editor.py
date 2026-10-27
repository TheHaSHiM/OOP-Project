from typing import Optional
from PyQt6.QtGui import QPainter

from shape import Shape
from editor import ShapeEditor, PointEditor, LineEditor, RectEditor, EllipseEditor


class ShapeObjectsEditor:

    MAX_SHAPES = 121

    def __init__(self):

        self.pcshape: list[Shape] = []


        self.current_editor: Optional[ShapeEditor] = None
        self.current_tool_name: str = ""

        self.start_point_editor()



    def start_point_editor(self):
        self.current_editor = PointEditor()
        self.current_tool_name = "point"

    def start_line_editor(self):
        self.current_editor = LineEditor()
        self.current_tool_name = "line"

    def start_rect_editor(self):
        self.current_editor = RectEditor()
        self.current_tool_name = "rect"

    def start_ellipse_editor(self):
        self.current_editor = EllipseEditor()
        self.current_tool_name = "ellipse"



    def on_lb_down(self, x: int, y: int):
        
        if self.current_editor:
            self.current_editor.on_lb_down(x, y)

    def on_mouse_move(self, x: int, y: int):
      
        if self.current_editor:
            self.current_editor.on_mouse_move(x, y)

    def on_lb_up(self, x: int, y: int):
      
        if self.current_editor:
            new_shape = self.current_editor.on_lb_up(x, y)
            if new_shape is not None:
                if len(self.pcshape) < self.MAX_SHAPES:
                   
                    self.pcshape.append(new_shape)
                else:
                    print("Досягнуто ліміту динамічного масиву (121 фігура)!")


    def on_paint(self, painter: QPainter):

        for shape in self.pcshape:
            shape.show(painter)
        if self.current_editor:
            self.current_editor.on_paint(painter)
