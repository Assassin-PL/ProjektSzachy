from pionek import ChessPiece


class ChessLogic:
    def __init__(self, pieces):
        self.pieces = pieces
        self.selected_piece_id = None
        self.white_turn = True  # Zmienna przechowująca informację o kolejności ruchu, True oznacza ture białych

    def select_piece(self, piece_id):
        self.selected_piece_id = piece_id

    def move_piece(self, new_position):
        if self.selected_piece_id is not None:
            piece = self.pieces[self.selected_piece_id]
            piece.set_position(new_position[0], new_position[1])
            self.selected_piece_id = None

    def check_collision(self, new_position):
        collision_piece_id = None

        for piece_id, piece in enumerate(self.pieces):
            if piece.actual_position_x == new_position[0] and piece.actual_position_y == new_position[1]:
                collision_piece_id = piece_id
                break
        return collision_piece_id

    def handle_collision(self, piece_id):
        if piece_id is not None:
            print("Handling collision with piece ID:", piece_id)
            piece = self.pieces[piece_id]
            selected_piece = self.pieces[self.selected_piece_id]

            # Sprawdź, czy pionki mają różne kolory
            if piece.color != selected_piece.color and isinstance(selected_piece, ChessPiece):
                # self.pieces[piece_id] = None  # Usuń zbity pionek z planszy
                print("powinno nastapic zbicie pionka")
                self.pieces[piece_id] = None  # Usuń zbity pionek z planszy
                self.remove_empty_pieces()
                # return selected_piece.actual_position_x, selected_piece.actual_position_y  # Tu jest blad bo przy biciu nie aktualizuje sie pozycja
            else:
                print("Invalid move: Cannot move to a square occupied by a piece of the same color.")
                # Przywróć pionek do poprzedniej pozycji
                selected_piece.set_position(selected_piece.previous_position[0], selected_piece.previous_position[1])
                print("Piece returned to previous position:", selected_piece.previous_position)
                return selected_piece.previous_position

    def is_any_piece_in_line(self, piece, new_position):
        x_end, y_end = new_position
        start = []
        if isinstance(piece, ChessPiece):
            x_start, y_start = piece.actual_position_x, piece.actual_position_y
            start.append(x_start)
            start.append(y_start)
            for p in self.pieces:
                if (piece.color == "black") and isinstance(p, ChessPiece) and p.color == 'black':
                    # linia pionowa prosta
                    if isinstance(p, ChessPiece) and p.color == 'black':
                        if x_start == x_end:  # linia pionowa
                            if y_start < p.actual_position_y < y_end and x_start == p.actual_position_x:
                                return True
                        elif y_start == y_end:  # linia pozioma
                            if x_start < p.actual_position_x < x_end and y_start == p.actual_position_y:
                                return True
                        else:  # linia po skosie
                            if self.bity_skos(p, new_position, start):
                                return True
                elif isinstance(p, ChessPiece):  # biale piece
                    if isinstance(p, ChessPiece):
                        if x_end == x_start:
                            if isinstance(p, ChessPiece):
                                if y_start > p.actual_position_y > y_end and x_start == p.actual_position_x:
                                    return True
                        elif y_end == y_start:
                            if isinstance(p, ChessPiece):
                                if x_start > p.actual_position_x > x_end and y_start == p.actual_position_y:
                                    return True
                        else:
                            if isinstance(p, ChessPiece):
                                if self.bity_skos(p, new_position, start):
                                    return True
                else:
                    return False
        else:
            return False

    def is_valid_move(self, piece, new_position, collision=False):
        x, y = new_position
        if isinstance(piece, ChessPiece):
            current_x, current_y = piece.actual_position_x, piece.actual_position_y

        # Sprawdzenie zasad dla króla
        if piece.piece_type == 'king':
            # Król może poruszać się o jedno pole w każdą stronę
            return abs(x - current_x) <= 1 and abs(y - current_y) <= 1

        # Sprawdzenie zasad dla królowej
        if piece.piece_type == 'queen':
            # Królowa może poruszać się w każdym kierunku, zarówno poziomo, pionowo, jak i na skos
            return (x == current_x or y == current_y or abs(x - current_x) == abs(y - current_y))
        #
        # Sprawdzenie zasad dla wieży
        if piece.piece_type == 'rook':
            # Wieża może poruszać się tylko poziomo lub pionowo
            return x == current_x or y == current_y

        # Sprawdzenie zasad dla skoczka
        if piece.piece_type == 'knight':
            # Skoczek porusza się w "L" - jedno pole w pionie i dwa w poziomie lub odwrotnie
            return (abs(x - current_x) == 2 and abs(y - current_y) == 1) or \
                   (abs(x - current_x) == 1 and abs(y - current_y) == 2)

        # Sprawdzenie zasad dla gońca
        if piece.piece_type == 'bishop':
            # Goniec porusza się po skosie
            return abs(x - current_x) == abs(y - current_y)

        if piece.piece_type == 'pawn':
            # Pionek może poruszać się do przodu o jedno pole, ale może wykonać pierwszy ruch o dwa pola
            if piece.color == 'black':
                if collision == False:
                    return (x == current_x and y == current_y + 1) or \
                           (current_y == 1 and x == current_x and y == current_y + 2)
                else:
                    # Bicie na skos do przodu
                    return (abs(x - current_x) == 1 and y == current_y + 1) or \
                           (x == current_x and y == current_y + 1) or \
                           (abs(x - current_x) == 1 and y == current_y)
            else:
                if collision == False:
                    return (x == current_x and y == current_y - 1) or \
                           (current_y == 6 and x == current_x and y == current_y - 2)
                else:
                    # Bicie na skos do przodu
                    return (abs(x - current_x) == 1 and y == current_y - 1) or \
                           (x == current_x and y == current_y - 1) or \
                           (abs(x - current_x) == 1 and y == current_y)

        # W przypadku innych typów pionków zwracamy False, co oznacza niedozwolony ruch
        return False

    def is_valid_move_old(self, piece, new_position, collision=False):
        x, y = new_position
        if isinstance(piece, ChessPiece):
            current_x, current_y = piece.actual_position_x, piece.actual_position_y

        # Sprawdzenie zasad dla króla
        if piece.piece_type == 'king':
            # Król może poruszać się o jedno pole w każdą stronę
            return abs(x - current_x) <= 1 and abs(y - current_y) <= 1

        # Sprawdzenie zasad dla królowej
        if piece.piece_type == 'queen':
            # Królowa może poruszać się w każdym kierunku, zarówno poziomo, pionowo, jak i na skos
            return (x == current_x or y == current_y or abs(x - current_x) == abs(y - current_y))

        # Sprawdzenie zasad dla wieży
        if piece.piece_type == 'rook':
            # Wieża może poruszać się tylko poziomo lub pionowo
            return x == current_x or y == current_y

        # Sprawdzenie zasad dla skoczka
        if piece.piece_type == 'knight':
            # Skoczek porusza się w "L" - jedno pole w pionie i dwa w poziomie lub odwrotnie
            return (abs(x - current_x) == 2 and abs(y - current_y) == 1) or \
                   (abs(x - current_x) == 1 and abs(y - current_y) == 2)

        # Sprawdzenie zasad dla gońca
        if piece.piece_type == 'bishop':
            # Goniec porusza się po skosie
            return abs(x - current_x) == abs(y - current_y)

        # Sprawdzenie zasad dla pionka
        if piece.piece_type == 'pawn':
            # Pionek może poruszać się do przodu o jedno pole, ale może wykonać pierwszy ruch o dwa pola
            if piece.color == 'black':
                if collision == False:
                    return (x == current_x and y == current_y + 1) or \
                           (current_y == 1 and x == current_x and y == current_y + 2)
                else:
                    # Bicie na skos do przodu
                    return (abs(x - current_x) == 1 and y == current_y + 1) or \
                           (x == current_x and y == current_y + 1) or \
                           (abs(x - current_x) == 1 and y == current_y)
            else:
                if collision == False:
                    return (x == current_x and y == current_y - 1) or \
                           (current_y == 6 and x == current_x and y == current_y - 2)
                else:
                    # Bicie na skos do przodu
                    return (abs(x - current_x) == 1 and y == current_y - 1) or \
                           (x == current_x and y == current_y - 1) or \
                           (abs(x - current_x) == 1 and y == current_y)

        # W przypadku innych typów pionków zwracamy False, co oznacza niedozwolony ruch
        return False

    def remove_empty_pieces(self):
        self.pieces = [piece for piece in self.pieces if piece is not None]

    def bity_skos(self, piece, new_position, start):
        x_start, y_start = int(start[0]), int(start[1])
        x_end, y_end = map(int, new_position)
        if isinstance(piece, ChessPiece):
            for i in range(1, abs(x_end - x_start)):
                if y_end > y_start:
                    y = y_start + i
                else:
                    y = y_start - i

                if x_end > x_start:
                    x = x_start + i
                else:
                    x = x_start - i
                if piece.actual_position_x == x and piece.actual_position_y == y:
                    return True
    # sekcja metod do oceny szacha!!!

    def get_possible_moves(self, piece_index):
            piece = self.pieces[piece_index]
            if piece is None:
                return []

            moves = []
            x = piece.actual_position_x
            y = piece.actual_position_y

            # Definiujemy ruchy zależnie od typu figury
            if piece.piece_type == 'pawn':
                direction = 1 if piece.color == 'black' else -1
                start_row = 1 if piece.color == 'black' else 6  # Startowe rzędy dla pionków: 6 dla czarnych, 1 dla białych

                # Prosty ruch do przodu
                if self.is_within_bounds(x, y + direction) and self.is_position_empty(x, y + direction):
                    moves.append((x, y + direction))

                    # Ruch o dwa pola do przodu tylko, gdy jest to pierwszy ruch pionka
                    if (piece.color == 'black' and y == 6) or (piece.color == 'white' and y == 1):
                        if self.is_position_empty(x, y + 2 * direction):
                            moves.append((x, y + 2 * direction))

                # Bicie na ukos
                for dx in [-1, 1]:
                    if self.is_within_bounds(x + dx, y + direction) and self.is_position_occupied_by_opponent(x + dx, y + direction, piece.color):
                        moves.append((x + dx, y + direction))

            elif piece.piece_type == 'rook':
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    for step in range(1, 8):  # Zakładamy, że plansza ma 8x8 pól
                        nx, ny = x + dx*step, y + dy*step
                        if not self.is_within_bounds(nx, ny):
                            break
                        if self.is_position_empty(nx, ny):
                            moves.append((nx, ny))
                        elif self.is_position_occupied_by_opponent(nx, ny, piece.color):
                            moves.append((nx, ny))
                            break
                        else:
                            break
            # Dodajemy analogiczne przypadki dla gońca, króla, hetmana i skoczka

            # Implementacja ruchów dla pozostałych figur
            if piece.piece_type == 'bishop':
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                for dx, dy in directions:
                    for step in range(1, 8):
                        nx, ny = x + dx * step, y + dy * step
                        if not self.is_within_bounds(nx, ny):
                            break
                        if self.is_position_empty(nx, ny):
                            moves.append((nx, ny))
                        elif self.is_position_occupied_by_opponent(nx, ny, piece.color):
                            moves.append((nx, ny))
                            break
                        else:
                            break

            elif piece.piece_type == 'queen':
                # Hetman łączy ruchy wieży i gońca
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    for step in range(1, 8):
                        nx, ny = x + dx * step, y + dy * step
                        if not self.is_within_bounds(nx, ny):
                            break
                        if self.is_position_empty(nx, ny):
                            moves.append((nx, ny))
                        elif self.is_position_occupied_by_opponent(nx, ny, piece.color):
                            moves.append((nx, ny))
                            break
                        else:
                            break

            elif piece.piece_type == 'king':
                # Król może poruszać się o jedno pole w każdym kierunku
                directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if self.is_within_bounds(nx, ny) and (self.is_position_empty(nx, ny) or self.is_position_occupied_by_opponent(nx, ny, piece.color)):
                        moves.append((nx, ny))

            elif piece.piece_type == 'knight':
                # Skoczek wykonuje ruchy w kształcie litery L
                knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
                for dx, dy in knight_moves:
                    nx, ny = x + dx, y + dy
                    if self.is_within_bounds(nx, ny) and (self.is_position_empty(nx, ny) or self.is_position_occupied_by_opponent(nx, ny, piece.color)):
                        moves.append((nx, ny))

            return moves

    def generate_moves(self, color):
        legal_moves = []
        for idx, piece in enumerate(self.pieces):
            if piece is not None and piece.color == color:
                possible_moves = self.get_possible_moves(idx)
                for move in possible_moves:
                    if self.is_move_legal(idx, move):
                        legal_moves.append((idx, move))
        return legal_moves

    def is_move_legal(self, piece_index, new_position):
        # Stary stan
        piece = self.pieces[piece_index]
        old_position = (piece.actual_position_x, piece.actual_position_y)

        # Symulacja ruchu
        piece.actual_position_x, piece.actual_position_y = new_position
        king_is_safe = not self.is_king_in_check(piece.color)

        # Cofnięcie ruchu
        piece.actual_position_x, piece.actual_position_y = old_position

        return king_is_safe

    def is_king_in_check(self, color):
        king_position = None
        for piece in self.pieces:
            if piece and piece.piece_type == 'king' and piece.color == color:
                king_position = (piece.actual_position_x, piece.actual_position_y)
                break

        for piece in self.pieces:
            if piece and piece.color != color:
                if king_position in self.get_possible_moves(self.pieces.index(piece)):
                    return True
        return False

    def is_within_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def is_position_empty(self, x, y):
        return not any(p.actual_position_x == x and p.actual_position_y == y for p in self.pieces if p is not None)

    def is_position_occupied_by_opponent(self, x, y, color):
        return any(p.actual_position_x == x and p.actual_position_y == y and p.color != color for p in self.pieces if p is not None)

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_game_over():
            return self.evaluate_board(), None

        best_move = None
        if maximizing_player:  # Maksymalizacja dla czarnych
            max_eval = float('-inf')
            for move in self.generate_moves('black'):
                # Symulacja wykonania ruchu
                piece_index, new_position = move
                piece = self.pieces[piece_index]
                old_position = (piece.actual_position_x, piece.actual_position_y)
                piece.actual_position_x, piece.actual_position_y = new_position

                eval, _ = self.minimax(depth - 1, alpha, beta, False)

                # Cofnięcie symulowanego ruchu
                piece.actual_position_x, piece.actual_position_y = old_position

                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                    alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:  # Minimizacja dla białych
            min_eval = float('inf')
            for move in self.generate_moves('white'):
                # Analogiczna symulacja i cofnięcie
                piece_index, new_position = move
                piece = self.pieces[piece_index]
                old_position = (piece.actual_position_x, piece.actual_position_y)
                piece.actual_position_x, piece.actual_position_y = new_position

                eval, _ = self.minimax(depth - 1, alpha, beta, True)

                piece.actual_position_x, piece.actual_position_y = old_position

                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                    beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def is_game_over(self):
        # Prosta funkcja sprawdzająca, czy gra się skończyła (np. mat, pat)
        # Ta metoda powinna być zaimplementowana w oparciu o zasady szachów
        return False

    def evaluate_board(self):
        # Prosta funkcja oceny planszy
        score = 0
        for piece in self.pieces:
            if piece is None:
                continue
            value = {'pawn': 1, 'knight': 3, 'bishop': 3, 'rook': 5, 'queen': 9, 'king': 100}[piece.piece_type]
            if piece.color == 'black':
                score += value
            else:
                score -= value
        return score

    def find_best_move(self):
        _, best_move = self.minimax(2, float('-inf'), float('inf'), True)  # Przykładowa głębokość 3, można dostosować
        return best_move

    def give_me_best_black_piece(self):
        _, best_move = self.minimax(3, float('-inf'), float('inf'), True)  # Załóżmy, że używamy głębokości 3
        if best_move:
            piece_index, new_position = best_move
            return self.pieces[piece_index], new_position
        return None, None


    def get_piece(self, pion, poziom):
        for piece in self.pieces:
            if isinstance(piece, ChessPiece) and piece.position_in_chess[0] == pion and piece.position_in_chess[1] == poziom:
                return piece
        return None
