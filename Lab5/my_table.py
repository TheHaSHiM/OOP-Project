from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt


class MyTable(QDialog):

    shape_selected = pyqtSignal(int) 
    shape_deleted = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Таблиця графічних об'єктів")
        self.resize(520, 350)

        layout = QVBoxLayout()

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Назва", "x1", "y1", "x2", "y2"])
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_delete = QPushButton("Видалити виділений об'єкт")
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def add(self, name: str, x1: int, y1: int, x2: int, y2: int):

        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)

        values = [name, str(x1), str(y1), str(x2), str(y2)]
        for col, val in enumerate(values):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_pos, col, item)

        self.table.scrollToBottom()

    def clear_table(self):
        self.table.setRowCount(0)

    def remove_row(self, index: int):
        if 0 <= index < self.table.rowCount():
            self.table.removeRow(index)

    def _on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row_idx = selected_rows[0].row()
            self.shape_selected.emit(row_idx)
        else:
            self.shape_selected.emit(-1)

    def _on_delete_clicked(self): 
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row_idx = selected_rows[0].row()
            self.shape_deleted.emit(row_idx)