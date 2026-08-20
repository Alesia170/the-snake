from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_POSITION = (
    (GRID_WIDTH // 2 - 1) * GRID_SIZE,
    (GRID_HEIGHT // 2 - 1) * GRID_SIZE,
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Отсуп между краем клетки и объектом
CELL_PADDING = 2

# Цвет отрисовки сетки
GRID_COLOR = (45, 45, 45)

# Цвет ядовитой еды
POISONOUS_FOOD_COLOR = (138, 43, 226)

# Время жизни ядовитой еды
LIFETIME = 5000

# Время до повторного появления ядовитой еды
RESPAWN_FOOD_TIME = 10000

# Интервал увеличения скорости
SPEED_UP_TIME = 15000

# Скорость движения змейки:
SPEED = 5

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None):
        self.position = CENTER_POSITION
        self.body_color = body_color

    def draw(self):
        """Метод отвечает за отрисовку объектов."""


class Food(GameObject):
    """Базовый класс для игорвых объектов еды."""

    def __init__(self, body_color, snake_positions=None):
        super().__init__(body_color)
        self.randomize_position(snake_positions)

    def randomize_position(self, snake_positions=None):
        """Устанавливает случайную позицию объекта на игровом поле."""
        if snake_positions is None:
            snake_positions = []

        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

            if position not in snake_positions:
                self.position = position
                break

    def draw(self):
        """Метод отвечает за отрисовку объектов еды."""
        rect = pg.Rect(
            (self.position[0] + CELL_PADDING, self.position[1] + CELL_PADDING),
            (GRID_SIZE - CELL_PADDING * 2, GRID_SIZE - CELL_PADDING * 2),
        )
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(Food):
    """Класс описания объекта яблока."""

    def __init__(self, snake_positions=None):
        super().__init__(APPLE_COLOR, snake_positions)


class PoisonousFood(Food):
    """Ядовитая еда для уменьшения длины змейки."""

    def __init__(self, snake_positions):
        super().__init__(POISONOUS_FOOD_COLOR, snake_positions)
        self.spawn_time = pg.time.get_ticks()
        self.active = True
        self.disappear_time = None

    def disappear_food(self, snake_positions):
        """Управляет исчезновением и появлением ядовитой еды."""
        current_time = pg.time.get_ticks()

        if self.active:
            if current_time - self.spawn_time > LIFETIME:
                self.active = False
                self.disappear_time = pg.time.get_ticks()
        else:
            if current_time - self.disappear_time > RESPAWN_FOOD_TIME:
                self.active = True
                self.spawn_time = pg.time.get_ticks()
                self.randomize_position(snake_positions)


class Snake(GameObject):
    """Змейка."""

    def __init__(self):
        super().__init__(SNAKE_COLOR)
        self.reset(RIGHT)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """Осуществляет движение змейки."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_position = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_position)

        while len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Метод отвечает за отрисовку змейки."""
        for position in self.positions:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def reset(self, direction=None):
        """Метод сбрасывает атрибуты змейки до начального."""
        self.length = 1
        self.positions = [self.position]
        self.direction = direction or choice((UP, DOWN, RIGHT, LEFT))
        self.next_direction = None
        self.last = None
        self.score = 1


def draw_board():
    """Метод отвечает за отрисовку сетки."""
    for i in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pg.draw.line(
            screen,
            GRID_COLOR,
            (0, i + GRID_SIZE),
            (SCREEN_WIDTH, i + GRID_SIZE),
        )

    for j in range(0, SCREEN_WIDTH, GRID_SIZE):
        pg.draw.line(
            screen,
            GRID_COLOR,
            (j + GRID_SIZE, 0),
            (j + GRID_SIZE, SCREEN_HEIGHT),
        )


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit


def main():
    """Запускает игру и управляет основным игровым циклом."""
    pg.init()

    # Время последнего увеличения скорости
    last_time = pg.time.get_ticks()

    speed = SPEED

    snake = Snake()
    apple = Apple(snake.positions)
    poison = PoisonousFood(snake.positions)

    while True:

        handle_keys(snake)
        snake.update_direction()
        snake.move()
        poison.disappear_food(snake.positions)

        if snake.get_head_position() == apple.position:
            snake.length += 1
            snake.score += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[4:]:
            speed, last_time = reset_game(snake, apple, poison)
        elif snake.get_head_position() == poison.position:
            if poison.active:
                if snake.length == 1:
                    speed, last_time = reset_game(snake, apple, poison)
                else:
                    snake.length -= 1
                    snake.score -= 1
                    poison.randomize_position(snake.positions)
                    poison.spawn_time = pg.time.get_ticks()

        screen.fill(BOARD_BACKGROUND_COLOR)

        draw_board()
        apple.draw()
        snake.draw()

        if poison.active:
            poison.draw()

        # Заголовок окна игрового поля:
        pg.display.set_caption(f'Змейка | Cчет: {snake.score} | ESC - выход')

        pg.display.update()

        speed, last_time = update_speed(speed, last_time)
        clock.tick(speed)


def update_speed(speed, last_time):
    """Увеличивает скорость игры через заданный интервал времени."""
    current_time = pg.time.get_ticks()

    if current_time - last_time > SPEED_UP_TIME:
        speed += 2
        last_time = current_time

    return speed, last_time


def reset_game(snake, apple, poison):
    """Сбрасывает игру до первоначального состояния."""
    snake.reset()
    apple.randomize_position(snake.positions)
    poison.randomize_position(snake.positions)
    poison.active = True
    poison.spawn_time = pg.time.get_ticks()
    poison.disappear_time = None

    speed = SPEED
    last_time = pg.time.get_ticks()

    return speed, last_time


if __name__ == '__main__':
    main()
