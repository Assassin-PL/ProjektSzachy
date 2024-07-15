import json
import os
import sqlite3
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET

from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QColor, QBrush, QPainter, QPen, QTransform
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QLineEdit, QMainWindow, \
    QDockWidget, QHBoxLayout
from PyQt5.QtWidgets import QGraphicsView, QLabel, QPushButton, QVBoxLayout, QWidget

from logi import LogWindow
from logi import redirect_stdout
from logika import ChessLogic  # Import klasy ChessLogic z pliku logika.py
from pionek import ChessPiece
from stale import *

WHITE = Qt.white
BLACK = Qt.black
BROWN = QColor('#FFB266')
GRAY = Qt.darkGray


class Chessboard:
    def __init__(self):
        self.board = self.create_board()

    def create_board(self):
        board = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]

        id = 0

        black_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col, piece in enumerate(black_pieces):
            board[BKING_POS[0]][col] = ChessPiece(piece, 'black', id)
            id = id + 1
            board[BPAWN_POS[0]][col] = ChessPiece('pawn', 'black', id)
            id = id + 1

        white_pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col, piece in enumerate(white_pieces):
            board[WKING_POS[0]][col] = ChessPiece(piece, 'white', id)
            id = id + 1
            board[WPAWN_POS[0]][col] = ChessPiece('pawn', 'white', id)
            id = id + 1

        return board


class ChessScene(QGraphicsScene):
    def __init__(self, View):
        super().__init__(View)
        self.std = None
        self.isAI = False
        self.IPadress = None
        self.gamePort = None
        self.view = View  # Przechowujemy referencję do obiektu ChessView
        self.which_turn = int(0)
        self.logic = None
        self.draw_board()
        self.add_pieces()
        self.selected_piece = None
        self.selected_offset = QPointF()
        self.obiekt_przeciagany = None
        self.roszadaB = False
        self.roszadaW = False
        self.wygranaW = False
        self.wygranaB = False
        self.Inkrement = False
        self.is_Blitz = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer_interval = 1000  # Interwał czasowy w milisekundach (1 sekunda)
        self.time_left = TIME_LEFT  # 5 minut (przykładowy czas na turę w sekundach)
        self.timeBlack = TIME_LEFT
        self.timeWhite = TIME_LEFT
        self.timeInkrement = MAX_TIME
        self.history = []
        self.init_database()

    def wczytaj_ustawienia(self):
        with open("ustawienia.json", 'r') as file:
            ustawienia = json.load(file)
        self.isAI = ustawienia['isAI']
        self.IPadress = ustawienia['IPadress']
        self.gamePort = ustawienia['gamePort']
        self.Inkrement = ustawienia['Inkrement']
        self.is_Blitz = ustawienia['is_Blitz']
        self.blitz()
        self.start_clock()

    def start_clock(self):
        self.time_left = self.timeWhite
        self.start_timer()

    def select_time_clock(self, user_input=1):
        if user_input == '0':
            self.is_Blitz = False
            self.Inkrement = False
        elif user_input == '1':
            self.is_Blitz = True
            self.Inkrement = False
        elif user_input == '2':
            self.Inkrement = False
            self.is_Blitz = True
        elif user_input == '3':
            self.Inkrement = True
            self.is_Blitz = True
        self.blitz()
        self.start_clock()

    def blitz(self):
        blitz = self.is_Blitz
        if blitz:
            self.time_left = BLITZ_TIME
            self.timeBlack = BLITZ_TIME
            self.timeWhite = BLITZ_TIME

    def start_timer(self):
        self.timer.start(self.timer_interval)

    def stop_timer(self):
        self.timer.stop()

    def update_time(self):
        self.time_left -= 1  # Odejmujemy jedną sekundę od pozostałego czasu
        if self.Inkrement: self.timeInkrement -= 1
        if self.time_left <= 0:
            self.stop_timer()  # Jeśli czas się skończył, zatrzymujemy zegar
            print("Koniec gry, przy upuszczeniu pionka nastepuje natychmiastowe zamkniecie!")
            if self.timeBlack <= 0 or self.timeWhite <= 0:
                self.close_game()
        else:
            if self.logic.white_turn:
                kolor = "bialego"
            else:
                kolor = "czarnego"
            print(f"Jest tura koloru {kolor} i  pozystalo czasu:", self.time_left)
            if self.Inkrement: print("Time interval:", self.timer_interval)

    def draw_board(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color = BROWN if (row + col) % 2 == 0 else GRAY
                brush = QBrush(color)
                self.addRect(BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE,
                             SQUARE_SIZE, SQUARE_SIZE, QPen(Qt.NoPen), brush)

    def add_pieces(self):
        chessboard = Chessboard().board
        chess_pieces = []  # Lista przechowująca wszystkie pionki
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                piece = chessboard[row][col]
                if piece:
                    piece.setPos(BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE)
                    piece.set_position(col, row)  # Ustaw aktualną pozycję pionka
                    piece.set_position(col, row)  # Ustaw aktualną pozycję pionka
                    chess_pieces.append(piece)  # Dodaj pionek do listy
                    self.addItem(piece)
        self.logic = ChessLogic(chess_pieces)  # Przekazanie listy pionków do logiki gry

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if isinstance(item, ChessPiece):
            # Sprawdź, czy można chwycić pionka danego koloru podczas tury odpowiedniego gracza
            if (self.logic.white_turn and item.color == 'white') or (
                    not self.logic.white_turn and item.color == 'black'):
                if self.logic.white_turn and False:
                    self.time_left = self.timeWhite
                elif False:
                    self.time_left = self.timeBlack
                # self.start_timer()
                color = 'black' if item.color == 'black' else 'white'
                category = item.piece_type[0].upper()
                print(f"{color}{category} clicked.")
                print(f"Current position before click: ({item.actual_position_x}, {item.actual_position_y})")
                self.selected_piece = item
                self.selected_offset = self.selected_piece.pos() - event.scenePos()
                self.selected_piece.setScale(ENLARGED_SIZE / PIECE_SIZE)
                if self.logic is not None:  # Sprawdź, czy logika jest zainicjalizowana
                    self.logic.select_piece(self.logic.pieces.index(item))  # Zaznacz wybrany pionek w obiekcie logiki
            else:
                print("Cannot select piece of the opposite color during this turn.")

    def mouseMoveEvent(self, event):
        if self.selected_piece:
            # Obliczenie nowej pozycji pionka
            new_pos = event.scenePos() + self.selected_offset
            # Zaokrąglenie pozycji do najbliższego kwadratu o wymiarze 10x10
            new_pos.setX(round(new_pos.x() / 1) * 1)
            new_pos.setY(round(new_pos.y() / 1) * 1)
            # Ograniczenie ruchu pionka do obszaru gry
            new_pos.setX(max(SQUARE_SIZE, min(new_pos.x(), SQUARE_SIZE * GRID_SIZE)))
            new_pos.setY(max(SQUARE_SIZE, min(new_pos.y(), SQUARE_SIZE * GRID_SIZE)))
            # Ustawienie nowej pozycji pionka
            self.selected_piece.setPos(new_pos)
            if self.time_left < 0: print("Koniec czsau")

    # tablica 8 na 8
    def mouseReleaseEvent(self, event):
        if self.selected_piece:
            # item = self.itemAt(event.scenePos(), QTransform())
            # self.selected_piece = item
            if isinstance(self.selected_piece, ChessPiece): print("Kolor trzymanego pionka" + self.selected_piece.color)
            # Zaokrąglenie pozycji do najbliższego kwadratu o wymiarze 100x100
            new_pos = self.selected_piece.pos()
            new_pos.setX(round(new_pos.x() / SQUARE_SIZE) * SQUARE_SIZE)
            new_pos.setY(round(new_pos.y() / SQUARE_SIZE) * SQUARE_SIZE)
            new_position = ((new_pos.x() // SQUARE_SIZE) - 1, (new_pos.y() // SQUARE_SIZE) - 1)
            buffor = new_position
            collision_piece_id = self.logic.check_collision(new_position)  # Sprawdź kolizję z innym pionkiem
            czy_bic = False
            czy_roszada = False
            czy_te_same_kolory = False
            if collision_piece_id is not None:
                collision_piece = self.logic.pieces[collision_piece_id]
                color = 'black' if collision_piece.color == 'black' else 'white'
                category = collision_piece.piece_type[0].upper()
                print(f"Collision with {color}{category} occurred.")
                new_position = self.logic.handle_collision(collision_piece_id)  # Obsłuż kolizję
                if new_position is None:
                    new_position = buffor
                # sprawdzanie i obsluga kolizji
                if isinstance(collision_piece, ChessPiece):
                    print("pozycja piąka bitego")
                    print((collision_piece.actual_position_x))
                    print((collision_piece.actual_position_y))
                    czy_bic = self.selected_piece.color != collision_piece.color  # bug jest taki ze tylko biale pionki moga bic czene ale na odwrot to nie dziala xd
                    print("czy zbic pionka? :" + str(
                        czy_bic))  # Tu pojawia sie dziwny bug zwiazany z pionkami moze jest to cos zwiazane z listami
                    # roszada na razie w debbugu
                    if self.selected_piece.piece_type == 'king' and not czy_bic and collision_piece.piece_type == "rook" and not self.logic.is_any_piece_in_line(
                            self.selected_piece, buffor):
                        if self.selected_piece.actual_position_y == 0 and self.selected_piece.color == "black":
                            print(f"jest roszada z kolorem {self.selected_piece.color}")
                            czy_roszada = not czy_roszada
                        elif self.selected_piece.actual_position_y == 7:
                            czy_roszada = not czy_roszada
                            print(f"jest roszada z kolorem {self.selected_piece.color}")
                    # bicie pionka
                    if czy_bic and self.logic.is_valid_move(self.selected_piece, new_position,
                                                            czy_bic) and not self.logic.is_any_piece_in_line(
                        self.selected_piece, new_position):
                        print("Różne kolory pionków.")
                        self.remove_piece_at_position(collision_piece)
            if isinstance(self.selected_piece, ChessPiece):
                if self.logic.is_any_piece_in_line(self.selected_piece, new_position):
                    print("Jest jakis pionek na drodze w zasiegu ruchu")
                # zmienna mowiaca o biciu tego samego koloru
                if collision_piece_id is not None:
                    if isinstance(collision_piece, ChessPiece):
                        if self.selected_piece.color == collision_piece.color:
                            czy_te_same_kolory = True
                else:
                    czy_te_same_kolory = False
                # Sprawdź czy ruch jest dozwolony
                if self.logic.is_valid_move(self.selected_piece, new_position, czy_bic) \
                        and (not self.logic.is_any_piece_in_line(self.selected_piece,
                                                                 new_position) or self.selected_piece.piece_type == "knight") and not czy_te_same_kolory and self.time_left > 0 \
                        and self.timeInkrement > 0:
                    # Jeśli ruch jest dozwolony, zaktualizuj pozycję pionka
                    self.selected_piece.set_position(new_pos.x() / SQUARE_SIZE - 1, new_pos.y() / SQUARE_SIZE - 1)
                    self.selected_piece.setPos(new_pos)
                    self.selected_piece.setScale(1.0)
                    if not self.logic.white_turn:
                        self.which_turn = self.which_turn + 1
                    self.logic.white_turn = not self.logic.white_turn
                    self.history.append(self.selected_piece.update_history(self.which_turn))
                elif czy_roszada and collision_piece is not None:
                    print("Obsluga roszady")
                    if isinstance(collision_piece, ChessPiece):
                        self.obsluz_roszade(collision_piece)
                        self.logic.white_turn = not self.logic.white_turn
                else:
                    # Jeśli ruch nie jest dozwolony, wyświetl komunikat
                    print("Invalid move: Cannot move to this square.")
                    if self.time_left <= 0:
                        print(
                            "Skonczyl sie czas zostal pionek przeniesiony na pozycje startowa, nastapila tura przeciwnika")
                        self.logic.white_turn = not self.logic.white_turn
                        if self.logic.white_turn:
                            self.timeWhite = self.time_left
                        else:
                            self.timeBlack = self.time_left
                    a = self.selected_piece.actual_position_x * SQUARE_SIZE + SQUARE_SIZE
                    b = self.selected_piece.actual_position_y * SQUARE_SIZE + SQUARE_SIZE
                    new_pos.setX(a)
                    new_pos.setY(b)
                    self.selected_piece.set_position(new_pos.x() / SQUARE_SIZE - 1, new_pos.y() / SQUARE_SIZE - 1)
                    self.selected_piece.setPos(new_pos)
                    self.selected_piece.setScale(1.0)
            self.selected_piece = None
            # self.opposite_turn()
            if not self.logic.white_turn:
                self.timeWhite = self.time_left
                self.time_left = self.timeBlack
            else:
                self.timeBlack = self.time_left
                self.time_left = self.timeWhite
            # self.stop_timer()
            self.timeInkrement = MAX_TIME
            self.is_king_exist()

    def manage_piece_collision(self, new_position, buffor, collision_piece_id, czy_bic=False, czy_roszada=False,
                               czy_te_same_kolory=False):
        if collision_piece_id is not None:
            collision_piece = self.logic.pieces[collision_piece_id]
            color = 'black' if collision_piece.color == 'black' else 'white'
            category = collision_piece.piece_type[0].upper()
            print(f"Collision with {color}{category} occurred.")
            new_position = self.logic.handle_collision(collision_piece_id)  # Obsłuż kolizję
            if new_position is None:
                new_position = buffor
            # sprawdzanie i obsluga kolizji
            if isinstance(collision_piece, ChessPiece):
                print("pozycja piąka bitego")
                print((collision_piece.actual_position_x))
                print((collision_piece.actual_position_y))
                czy_bic = self.selected_piece.color != collision_piece.color  # bug jest taki ze tylko biale pionki moga bic czene ale na odwrot to nie dziala xd
                print("czy zbic pionka? :" + str(
                    czy_bic))  # Tu pojawia sie dziwny bug zwiazany z pionkami moze jest to cos zwiazane z listami
                # roszada na razie w debbugu
                if self.selected_piece.piece_type == 'king' and not czy_bic and collision_piece.piece_type == "rook" and not self.logic.is_any_piece_in_line(
                        self.selected_piece, buffor):
                    if self.selected_piece.actual_position_y == 0 and self.selected_piece.color == "black":
                        print(f"jest roszada z kolorem {self.selected_piece.color}")
                        return not czy_roszada, czy_bic, new_position
                    elif self.selected_piece.actual_position_y == 7:
                        return not czy_roszada, czy_bic, new_position
                        print(f"jest roszada z kolorem {self.selected_piece.color}")
                # bicie pionka
                if czy_bic and self.logic.is_valid_move(self.selected_piece, new_position,
                                                        czy_bic) and not self.logic.is_any_piece_in_line(
                    self.selected_piece, new_position):
                    print("Różne kolory pionków.")
                    self.remove_piece_at_position(collision_piece)

    def manage_piece_collision(self, new_position, collision_piece_id, czy_bic=False, czy_roszada=False,
                               czy_te_same_kolory=False):
        if isinstance(self.selected_piece, ChessPiece):
            if collision_piece_id is not None: collision_piece = self.logic.pieces[collision_piece_id]
            new_pos = self.selected_piece.pos()
            if self.logic.is_any_piece_in_line(self.selected_piece, new_position):
                print("Jest jakis pionek na drodze w zasiegu ruchu")
            # zmienna mowiaca o biciu tego samego koloru
            if collision_piece_id is not None:
                if isinstance(collision_piece, ChessPiece):
                    if self.selected_piece.color == collision_piece.color:
                        czy_te_same_kolory = True
            else:
                czy_te_same_kolory = False
            # Sprawdź czy ruch jest dozwolony
            if self.logic.is_valid_move(self.selected_piece, new_position, czy_bic) \
                    and (not self.logic.is_any_piece_in_line(self.selected_piece,
                                                             new_position) or self.selected_piece.piece_type == "knight") and not czy_te_same_kolory and self.time_left > 0 \
                    and self.timeInkrement > 0:
                # Jeśli ruch jest dozwolony, zaktualizuj pozycję pionka
                self.selected_piece.set_position(new_pos.x() / SQUARE_SIZE - 1, new_pos.y() / SQUARE_SIZE - 1)
                self.selected_piece.setPos(new_pos)
                self.selected_piece.setScale(1.0)
                if not self.logic.white_turn:
                    self.which_turn = self.which_turn + 1
                self.logic.white_turn = not self.logic.white_turn
                self.history.append(self.selected_piece.update_history(self.which_turn))
            elif czy_roszada and collision_piece is not None:
                print("Obsluga roszady")
                if isinstance(collision_piece, ChessPiece):
                    self.obsluz_roszade(collision_piece)
                    self.logic.white_turn = not self.logic.white_turn
            else:
                # Jeśli ruch nie jest dozwolony, wyświetl komunikat
                print("Invalid move: Cannot move to this square.")
                if self.time_left <= 0:
                    print(
                        "Skonczyl sie czas zostal pionek przeniesiony na pozycje startowa, nastapila tura przeciwnika")
                    self.logic.white_turn = not self.logic.white_turn
                    if self.logic.white_turn:
                        self.timeWhite = self.time_left
                    else:
                        self.timeBlack = self.time_left
                a = self.selected_piece.actual_position_x * SQUARE_SIZE + SQUARE_SIZE
                b = self.selected_piece.actual_position_y * SQUARE_SIZE + SQUARE_SIZE
                new_pos.setX(a)
                new_pos.setY(b)
                self.selected_piece.set_position(new_pos.x() / SQUARE_SIZE - 1, new_pos.y() / SQUARE_SIZE - 1)
                self.selected_piece.setPos(new_pos)
                self.selected_piece.setScale(1.0)

    def opposite_turn(self):
        # greacz jest kolorem białym
        print("Test, jest tura przeciwnika")
        pion = input("Podaj wa jakiej kolumnie jest pionek")
        poziom = input("Podaj wa jakim wierszu jest pionek")
        zaznaczony_pionek = self.logic.get_piece(pion, poziom)
        # self.logic.white_turn = not self.logic.white_turn
        print("Test, jest tura przeciwnika")

    def create_or_edit_settings_file(self):
        # Słownik z wartościami atrybutów
        settings_data = {
            'isAI': self.isAI,
            'IPadress': self.IPadress,
            'gamePort': self.gamePort,
            'Inkrement': self.Inkrement,
            'is_Blitz': self.is_Blitz
        }

        # Sprawdzenie istnienia pliku ustawienia.json
        if os.path.exists('ustawienia.json'):
            # Jeśli plik istnieje, wczytaj jego zawartość
            with open('ustawienia.json', 'r') as file:
                existing_data = json.load(file)

            if self.IPadress is None:
                settings_data['IPadress'] = existing_data['IPadress']
            if self.gamePort is None:
                settings_data['gamePort'] = existing_data['gamePort']

            # Zaktualizuj istniejące dane nowymi wartościami
            existing_data.update(settings_data)

            # Zapisz zaktualizowane dane do pliku JSON
            with open('ustawienia.json', 'w') as file:
                json.dump(existing_data, file, indent=4)
        else:
            # Jeśli plik nie istnieje, utwórz nowy plik z danymi
            with open('ustawienia.json', 'w') as file:
                json.dump(settings_data, file, indent=4)

    def save_history_to_xml(self, filename):
        # Utwórz element główny historii
        root = ET.Element("history")

        # Iteracja przez elementy historii
        for piece_history in self.history:
            # Utwórz element dla każdej pozycji w historii
            piece_elem = ET.Element("piece")
            root.append(piece_elem)

            # Ustaw atrybuty elementu piece
            piece_elem.set("turn", str(piece_history.turn))

            # Utwórz podelementy wewnątrz elementu piece i przekonwertuj wartości na stringi
            piece_type_elem = ET.Element("piece_type")
            piece_type_elem.text = str(piece_history.piece_type)
            piece_elem.append(piece_type_elem)

            color_elem = ET.Element("color")
            color_elem.text = str(piece_history.color)
            piece_elem.append(color_elem)

            position_elem = ET.Element("position")
            position_elem.text = str(piece_history.position)
            piece_elem.append(position_elem)

        # Utwórz drzewo XML w formie łańcucha znaków
        xml_str = ET.tostring(root, encoding="utf-8", method="xml")

        # Sformatuj łańcuch XML za pomocą minidom
        xml_str_pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(encoding="utf-8")

        # Zapisz sformatowany XML do pliku
        with open(filename, "wb") as xml_file:
            xml_file.write(xml_str_pretty)

    def init_database(self):
        # Tworzenie lub łączenie z bazą danych
        self.conn = sqlite3.connect('history.db')
        self.cursor = self.conn.cursor()

        # Tworzenie tabeli, jeśli nie istnieje
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history
                                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    turn INTEGER,
                                    piece_type TEXT,
                                    color TEXT,
                                    position TEXT)''')
        self.conn.commit()

    def save_history_to_sqlite(self):
        # Parsowanie pliku XML
        try:
            tree = ET.parse('history.xml')
            xml_root = tree.getroot()

            # Połączenie z bazą danych SQLite
            conn = sqlite3.connect('history.db')
            cursor = conn.cursor()

            # Utworzenie tabeli, jeśli nie istnieje
            cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                                turn INTEGER,
                                piece_type TEXT,
                                color TEXT,
                                position TEXT
                            )''')

            # Wstawienie danych z pliku XML do bazy danych
            for history in xml_root.findall('history'):
                turn = history.find('turn').text
                piece_type = history.find('piece_type').text
                color = history.find('color').text
                position = history.find('position').text
                cursor.execute('''INSERT INTO history (turn, piece_type, color, position)
                                  VALUES (?, ?, ?, ?)''', (turn, piece_type, color, position))

            # Zatwierdzenie zmian i zamknięcie połączenia
            conn.commit()
            conn.close()

        except FileNotFoundError:
            print("Plik 'history.xml' nie istnieje.")
        except Exception as e:
            print(f"Wystąpił błąd podczas przetwarzania danych XML: {e}")

    def save_history_to_json(self):
        history_file = 'history.json'

        # Utwórz listę słowników zawierających dane z self.history
        history_dicts = [history.to_dict() for history in self.history]

        # Zapisz historię do pliku JSON
        with open(history_file, 'w') as file:
            json.dump(history_dicts, file, indent=4)

    def remove_piece_at_position(self, collision_piece):
        self.removeItem(collision_piece)  # po pierwszym zbiciu jest jakis bug z usuwaniem pionka?

    def roszada(self, collision_piece):
        if isinstance(collision_piece, ChessPiece):
            if collision_piece == "rook" and self.selected_piece.color == "black":
                print(f"jest roszada z kolorem {self.selected_piece.color}")
            else:
                print(f"jest roszada z kolorem {self.selected_piece.color}")

    def is_king_exist(self):
        king_white_exist = False
        king_black_exist = False

        for item in self.items():
            if isinstance(item, ChessPiece):
                if item.piece_type == 'king':
                    if item.color == 'white':
                        king_white_exist = True
                    elif item.color == 'black':
                        king_black_exist = True

        if not king_white_exist:
            self.wygranaB = True
            print("Black player wins!")
            self.close_game()
        elif not king_black_exist:
            self.wygranaW = True
            print("White player wins!")
            self.close_game()

    def close_game(self):
        self.create_or_edit_settings_file()
        self.save_history_to_json()
        # Zapis do bazy danych SQLite
        self.save_history_to_xml("history.xml")
        self.save_history_to_sqlite()

        # Zapis do pliku JSON
        QApplication.quit()
        sys.stdout = self.std
        # self.parent_view.hide()

    def obsluz_roszade(self, collision_piece):
        new_pos_king = self.selected_piece.pos()
        if isinstance(collision_piece, ChessPiece):
            new_pos_rook = collision_piece.pos()
            if collision_piece.actual_position_x == 0:
                new_x_king = (self.selected_piece.actual_position_x - 2) * SQUARE_SIZE + SQUARE_SIZE
                new_x_rook = (collision_piece.actual_position_x + 3) * SQUARE_SIZE + SQUARE_SIZE
                new_pos_king.setX(new_x_king)
                new_pos_rook.setX(new_x_rook)
                self.selected_piece.set_position(new_pos_king.x() / SQUARE_SIZE - 1, new_pos_king.y() / SQUARE_SIZE - 1)
                self.selected_piece.setPos(new_pos_king)
                self.selected_piece.setScale(1.0)
                collision_piece.set_position(new_pos_rook.x() / SQUARE_SIZE - 1, new_pos_rook.y() / SQUARE_SIZE - 1)
                collision_piece.setPos(new_pos_rook)
                collision_piece.setScale(1.0)
            else:
                new_x_king = (self.selected_piece.actual_position_x + 2) * SQUARE_SIZE + SQUARE_SIZE
                new_x_rook = (collision_piece.actual_position_x - 2) * SQUARE_SIZE + SQUARE_SIZE
                new_pos_king.setX(new_x_king)
                new_pos_rook.setX(new_x_rook)
                self.selected_piece.set_position(new_pos_king.x() / SQUARE_SIZE - 1, new_pos_king.y() / SQUARE_SIZE - 1)
                self.selected_piece.setPos(new_pos_king)
                self.selected_piece.setScale(1.0)
                collision_piece.set_position(new_pos_rook.x() / SQUARE_SIZE - 1, new_pos_rook.y() / SQUARE_SIZE - 1)
                collision_piece.setPos(new_pos_rook)
                collision_piece.setScale(1.0)


class ChessViewOld(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(ChessScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setWindowTitle('Chess Game')


class ChessView(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inicjalizacja interfejsu
        self.original_stdout = sys.stdout
        self.init_ui()

    def init_ui(self):
        # Ustawienie sceny i renderowania
        self.scene = ChessScene(self)
        self.scene.std = self.original_stdout
        self.view = QGraphicsView(self.scene)
        self.setWindowTitle('Chess Game')

        # Tworzenie etykiet i przycisków
        self.ip_label = QLabel("Adres IP:")
        self.port_label = QLabel("Port:")
        self.ip_input = QLineEdit()
        self.port_input = QLineEdit()
        self.connect_button = QPushButton("Połącz")
        self.enable_ai_button = QPushButton("Włącz AI")
        self.load_settings_button = QPushButton("Wczytaj ustawienia")

        # Przypisanie metody do przycisków
        self.connect_button.clicked.connect(self.on_connect_clicked)
        self.enable_ai_button.clicked.connect(self.on_enable_ai_clicked)
        self.load_settings_button.clicked.connect(self.on_load_settings_clicked)

        # Tworzenie layoutu
        layout = QVBoxLayout()
        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.enable_ai_button)
        layout.addWidget(self.load_settings_button)

        # Tworzenie widgetu i ustawienie layoutu
        widget = QWidget()
        widget.setLayout(layout)

        # Tworzenie obiektu QDockWidget i dodanie do niego okna logów
        dock_widget = QDockWidget()
        dock_widget.setWindowTitle("Logi")
        dock_widget.setWidget(LogWindow())

        # Ustawienie widgetu jako widżet boczny w głównym oknie
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_widget)

        # Przekierowanie stdout do okna logów
        redirect_stdout(dock_widget.widget())

        # Tworzenie layoutu z QGraphicsView i QWidget obok siebie
        main_layout = QHBoxLayout()
        # main_layout.addWidget(self.view)
        main_layout.addWidget(widget)

        # Tworzenie widgetu głównego i ustawienie layoutu
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Atrybut sprawdzający czy włączono AI
        self.ai_enabled = False

        # Dodawanie przycisków do trybów
        self.add_mode_buttons()

        # Zmienna przechowująca informację o wybranym trybie
        self.mode_selected = False

    def add_mode_buttons(self):
        # Lista nazw trybów
        modes = ["Standardowy", "Tryb 1", "Tryb 2", "Tryb 3"]

        # Tworzenie przycisków i dodawanie ich do layoutu
        for i, mode in enumerate(modes):
            button = QPushButton(f"Wybrano tryb {i + 1}")
            button.clicked.connect(lambda state, mode=mode: self.on_mode_button_clicked(mode))
            self.add_right_widget(button)

    def add_right_widget(self, widget):
        right_layout = QVBoxLayout()
        right_layout.addWidget(widget)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        main_layout = self.centralWidget().layout()
        main_layout.addWidget(right_widget)

    def on_mode_button_clicked(self, mode):
        print(f"Wybrano tryb: {mode}")
        # Blokowanie wszystkich przycisków trybów po wybraniu jednego
        self.mode_selected = True
        # Tworzenie layoutu z QGraphicsView i QWidget obok siebie
        self.set_chess_central_scene()
        for widget in self.centralWidget().findChildren(QPushButton):
            if widget.text().startswith("Wczytaj ustawienia"):
                widget.setEnabled(False)
        self.scene.select_time_clock(mode[-1])

    def on_connect_clicked(self):
        if self.mode_selected:
            print("Proszę najpierw wybrać tryb gry!")
            return
        # Pobierz tekst z QLineEdit
        ip_address = self.ip_input.text()
        game_port = self.port_input.text()

        # Przypisz tekst do atrybutów sceny
        self.scene.IPadress = ip_address
        self.scene.gamePort = game_port

    def on_enable_ai_clicked(self):
        if self.mode_selected:
            print("Proszę najpierw wybrać tryb gry!")
            return
        self.ai_enabled = not self.ai_enabled  # Odwrócenie stanu AI
        self.scene.isAI = self.ai_enabled

    def on_load_settings_clicked(self):
        # Tworzenie layoutu z QGraphicsView i QWidget obok siebie
        self.mode_selected = True
        self.set_chess_central_scene()
        for widget in self.centralWidget().findChildren(QPushButton):
            if widget.text().startswith("Wczytaj ustawienia"):
                widget.setEnabled(False)

        self.scene.wczytaj_ustawienia()

    def set_chess_central_scene_old(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.view)

        # Tworzenie widgetu głównego i ustawienie layoutu
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def set_chess_central_scene(self):
        # Tworzenie layoutu z QGraphicsView po lewej stronie
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.view)

        # Tworzenie widgetu dla prawego panelu
        right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout()
        right_panel_widget.setLayout(right_panel_layout)

        # Tworzenie pola tekstowego
        self.text_edit = QLineEdit()
        right_panel_layout.addWidget(self.text_edit)

        # Tworzenie przycisku
        button = QPushButton("Wprowadz tekst")
        button.clicked.connect(self.on_copy_button_clicked)
        right_panel_layout.addWidget(button)

        # Dodanie prawego panelu do głównego layoutu
        main_layout.addWidget(right_panel_widget)

        # Tworzenie widgetu głównego i ustawienie layoutu
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def on_copy_button_clicked(self):
        # Pobierz tekst z pola tekstowego
        text_to_copy = self.text_edit.text()
        print(text_to_copy)

    def closeEvent(self, event):
        # Przywróć sys.stdout do oryginalnej wartości
        sys.stdout = self.original_stdout
        event.accept()  # Akceptuj zamknięcie okna
