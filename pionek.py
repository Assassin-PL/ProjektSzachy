from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from stale import *

class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, piece_type, color, ID=0):
        super().__init__()
        self.piece_type = piece_type
        self.color = color
        self.actual_position_x = 0
        self.actual_position_y = 0
        self.previous_position = (0, 0)  # Dodaj atrybut previous_position i zainicjalizuj go
        self.position_in_chess = ('a', '0')
        self.load_image()
        self.historyOfPiece = []
        self.pieceID = ID

    def load_image(self):
        color_str = 'w' if self.color == 'white' else 'b'
        piece_str = self.piece_type.lower()
        image_path = f'icons/{color_str}{piece_str}.png'
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(PIECE_SIZE, PIECE_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)

    def convert_to_chess_position(self, x, y):
        pion = int(x) + ord('a')
        poziom = GRID_SIZE - int(y) + 48
        return (chr(pion), chr(poziom))

    def convert_to_logic_position(self, x, y):
        pion = ord(x) - ord('a')
        poziom = GRID_SIZE - ord(y) + 48
        return pion, poziom


    def set_position(self, x, y):
        self.previous_position = (self.actual_position_x, self.actual_position_y)  # Zaktualizuj poprzednią pozycję
        self.actual_position_x = x
        self.actual_position_y = y
        self.set_chess_position(int(x), int(y))

    def set_chess_position(self, x, y):
        pion = int(x) + ord('a')
        poziom = GRID_SIZE - int(y) + 48
        self.position_in_chess = (chr(pion), chr(poziom))

    def update_position(self):
        self.actual_position_x = int(self.position_in_chess[0] - 'a')
        self.actual_position_y = GRID_SIZE - int(self.position_in_chess[1]) + 48

    def update_history(self, turn):
        # Tworzymy nowy obiekt PieceHistory na podstawie aktualnego stanu
        actual_state = PieceHistory(turn, self.piece_type, self.color, self.position_in_chess)
        self.historyOfPiece.append(actual_state)
        # Dodajemy ten obiekt do historii
        return actual_state

# Dopisac ID dla kazdego pionka!!!

class PieceHistory:
    def __init__(self, tura, typ_pionka, kolor, pozycja_w_szachach):
        self.turn = tura
        self.piece_type = typ_pionka
        self.color = kolor
        self.position = pozycja_w_szachach

    def to_dict(self):
        return {
            'turn': self.turn,
            'piece_type': self.piece_type,
            'color': self.color,
            'position': self.position
        }
