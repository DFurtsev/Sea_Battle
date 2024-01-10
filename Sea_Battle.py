from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Укажите координаты в пределах игрового поля"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Клетка уже была обстреляна ранее"


class BoardWrongShipException(BoardException):
    pass


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point({self.x}, {self.y})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, start_position, ship_size, orientation):
        self.start_position = start_position
        self.ship_size = ship_size
        self.orientation = orientation
        self.hit_points = ship_size

    @property
    def location(self):
        ship_location = []
        for i in range(self.ship_size):
            build_x = self.start_position.x
            build_y = self.start_position.y

            if self.orientation == 0:
                build_x += i

            elif self.orientation == 1:
                build_y += i

            ship_location.append(Point(build_x, build_y))

        return ship_location

    def is_hiten(self, hit):
        return hit in self.location


class WarZone:
    def __init__(self, is_hidden=False, field_size=6):
        self.is_hidden = is_hidden
        self.field_size = field_size
        self.destroyed_ships = 0
        self.field = [["≈"] * field_size for _ in range(field_size)]
        self.busy_points = []
        self.all_ships = []

    def __str__(self):
        start_field = ''
        start_field += '| 1 | 2 | 3 | 4 | 5 | 6 |\n'
        for i, rows in enumerate(self.field):
            start_field += str(i + 1) + '| ' + ' | '.join(rows) + ' | \n'

        if self.is_hidden:
            start_field = start_field.replace('■', '≈')
        return start_field

    def out_of_warzone(self, d):
        return not ((0 <= d.x < self.field_size) and (0 <= d.y < self.field_size))

    def area(self, ship, field_check=False):
        blocked_area = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for p in ship.location:
            for i, j in blocked_area:
                blocked_point = Point(p.x + i, p.y + j)
                if not (self.out_of_warzone(blocked_point)) and blocked_point not in self.busy_points:
                    if field_check:
                        self.field[blocked_point.x][blocked_point.y] = "."
                    self.busy_points.append(blocked_point)

    def create_ship(self, ship):

        for p in ship.location:
            if self.out_of_warzone(p) or p in self.busy_points:
                raise BoardWrongShipException
        for p in ship.location:
            self.field[p.x][p.y] = '■'
            self.busy_points.append(p)

        self.all_ships.append(ship)
        self.area(ship)

    def shot(self, p):
        if self.out_of_warzone(p):
            raise BoardOutException()
        if p in self.busy_points:
            raise BoardUsedException()
        self.busy_points.append(p)

        for ship in self.all_ships:
            if p in ship.location:
                ship.hit_points -= 1
                self.field[p.x][p.y] = "X"
                if ship.hit_points == 0:
                    self.destroyed_ships += 1
                    self.area(ship, field_check=True)
                    print("Корабль уничтожен")
                    return False
                else:
                    print("Попадание")
                    return True
        self.field[p.x][p.y] = '.'
        print('Не попал')
        return False

    def clear_warzone(self):
        self.busy_points = []

    def defeat_check(self):
        return self.destroyed_ships == len(self.all_ships)


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def coordinate_request(self):
        raise NotImplementedError()

    def make_shot(self):
        while True:
            try:
                target = self.coordinate_request()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class Computer(Player):
    def coordinate_request(self):
        p = Point(randint(0, 5), randint(0, 5))
        print(f'Противник стреляет по {p.x + 1}, {p.y + 1}')
        return p


class User(Player):
    def coordinate_request(self):
        while True:
            point_to_shot = input('Введите координаты для выстрела в формате "x y"\n').split()

            if len(point_to_shot) != 2:
                print('Вы ввели неверное количество символов')
                continue
            x, y = point_to_shot

            if not x.isdigit() or not y.isdigit():
                print("Необходимо ввести числовые значения")
                continue
            x, y = int(x), int(y)
            return Point(x - 1, y - 1)


class MainGameClass:
    def __init__(self, size=6):
        self.size = size
        player = self.board_generate()
        computer = self.board_generate()
        computer.is_hidden = True

        self.computer_player = Computer(computer, player)
        self.user_player = User(player, computer)

    def start_message(self):
        header = ("-"*20)
        print(f'Игра "Морской бой".\n{header}\nФормат ввода координат: x y, где x - номер строки, y - номер столбца\n{header}')

    def try_board_generate(self):
        ship_pack = [3, 2, 2, 1, 1, 1]
        board = WarZone(field_size=self.size)
        generate_try = 0
        for i in ship_pack:
            while True:
                generate_try += 1
                if generate_try > 2000:
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.create_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.clear_warzone()
        return board

    def board_generate(self):
        board = None
        while board is None:
            board = self.try_board_generate()
        return board

    def print_boards(self):
        header = ('-' * 20)
        print(header, '\nВаша доска с кораблями\n', self.user_player.board)
        print(header, '\nДоска противника\n', self.computer_player.board)
        print(header)

    def main_cycle(self):
        header = ('-' * 20)
        count = 0
        while True:
            self.print_boards()
            if count % 2 == 0:
                print("Ваш ход")
                repeat= self.user_player.make_shot()
            else:
                print("Ходит противник")
                repeat = self.computer_player.make_shot()
            if repeat:
                count -= 1
            if self.computer_player.board.defeat_check():
                self.print_boards()
                print(header, '\n Вы выиграли')
                break
            if self.user_player.board.defeat_check():
                self.print_boards()
                print(header, '\n Вы проиграли')
                break
            count += 1

    def start_game(self):
        self.start_message()
        self.main_cycle()


g = MainGameClass()
g.start_game()
