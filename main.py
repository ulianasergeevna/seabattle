from random import randint


class InvalidCoordinateException(Exception):
    def __str__(self):
        return "Здесь должна быть ОДНА ЦИФРА!\n"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Поправь прицел, тут уже берег!\n"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Сюда снаряд уже падал\n"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, o):
        self.bow = bow
        self.length = length
        self.o = o
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots


class Board:
    def __init__(self, hidden=False, size=6):
        self.size = size
        self.hidden = hidden

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.occupied = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.occupied:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.occupied.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.occupied:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.occupied.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hidden:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.occupied:
            raise BoardUsedException()

        self.occupied.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Убит!")
                else:
                    print("Ранен!")

                return True

        self.field[d.x][d.y] = "Т"
        print("Мимо!")
        return False

    def begin(self):
        self.occupied = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except (BoardException, InvalidCoordinateException) as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, self.board.size - 1), randint(0, self.board.size - 1))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        try:
            x = int(input("Введи номер строки: ")) - 1
            y = int(input("Введи номер столбца: ")) - 1
        except ValueError:
            raise InvalidCoordinateException

        return Dot(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        player_board = self.random_board()
        comp_board = self.random_board()
        comp_board.hidden = True

        self.ai = AI(comp_board, player_board)
        self.us = User(player_board, comp_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lengths = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for length in lengths:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print("-" * 27)
        print(" Добро пожаловать на борт!")
        print("        Приготовься,")
        print(" мы собираемся вступить в")
        print("        МОРСКОЙ БОЙ!")
        print("-" * 27)

    def loop(self):
        num = 0
        while True:
            print("-" * 27)
            print("    Доска пользователя:")
            print(self.us.board)
            print("-" * 27)
            print("     Доска компьютера:")
            print(self.ai.board)
            print("-" * 27 + "\n")

            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("Компьютер выиграл!")
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
