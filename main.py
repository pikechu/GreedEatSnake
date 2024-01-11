import sys
import pygame
import time
import threading
from queue import Queue
from random import choice


WINDOW_SIZE_X = 900
WINDOW_SIZE_Y = 900

WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
ORANGE_COLOR = (255, 97, 0)
GREEN_COLOR = (0, 255, 0)
BROWN_COLOR = (160, 82, 45)
ELE_WHITE_COLOR = (250, 255, 240)

SNAKE_WEIGHT = 30
SNAKE_HEIGHT = 30

BUTTON_COLOR = (100, 200, 100)
BUTTON_HOVER_COLOR = (150, 250, 150)

button_start_rect = pygame.Rect(0, 0, 100, 50)
button_start_rect.center = (WINDOW_SIZE_X // 2, WINDOW_SIZE_Y // 2)
button_quit_rect = pygame.Rect(0, 0, 100, 50)
button_quit_rect.center = (WINDOW_SIZE_X // 2, WINDOW_SIZE_Y // 2 + 100)


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_point(self):
        return self.x, self.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'x:{self.x}, y:{self.y}'

    def copy(self, other):
        self.x = other.x
        self.y = other.y


class Snake(object):
    def __init__(self, snake_head):
        self.snake_head = snake_head
        self.flesh = [self.snake_head]
        self.foods = Queue()
        self.current_food = None
        self.grow_at_next_move = False

    def move(self, move_direction):
        for node in range(len(self.flesh) - 1, 0, -1):
            self.flesh[node].copy(self.flesh[node - 1])
        if move_direction in (Direction.LEFT, Direction.RIGHT):
            self.snake_head.x += SNAKE_WEIGHT if move_direction == Direction.RIGHT else -SNAKE_WEIGHT
        else:
            self.snake_head.y += SNAKE_HEIGHT if move_direction == Direction.DOWN else -SNAKE_HEIGHT
        # grow
        if self.grow_at_next_move is True:
            self.flesh.append(Point(self.current_food.x, self.current_food.y))
            if self.foods.qsize() > 0:
                self.current_food = self.foods.get()
            else:
                self.current_food = None
            self.grow_at_next_move = False
            print('grow')

    def is_bite(self):
        if len(self.flesh) == 1:
            return False
        return self.snake_head in self.flesh[1:]

    def is_over_border(self, x, y):
        return not (0 <= self.snake_head.x < x and 0 <= self.snake_head.y < y)

    def eat_food(self, food):
        self.foods.put(food)
        if not self.current_food:
            self.current_food = self.foods.get()
            print(f'current_food={self.current_food}')

    def is_eating(self, food):
        if self.snake_head == food:
            print('is_eating')
            return True
        return False

    def check_grow(self):
        if self.current_food and self.flesh[-1] == self.current_food:
            self.grow_at_next_move = True


class Direction(object):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

RELATIVE_MAP = {
    Direction.UP: Direction.DOWN,
    Direction.LEFT: Direction.RIGHT,
    Direction.DOWN: Direction.UP,
    Direction.RIGHT: Direction.LEFT
}

class Difficulty(object):
    EASY = 1
    NORMAL = 2
    HARD = 3
    LUNATIC = 4
    INHUMAN = 5


KB_EVENT_MAP = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT
}


def check_event(previous_move_direction):
    move_direction = previous_move_direction
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in KB_EVENT_MAP.keys():
                print(f'get keyboard event:{KB_EVENT_MAP[event.key]}')
                # cannot reverse directly
                if KB_EVENT_MAP[event.key] == RELATIVE_MAP[move_direction]:
                    continue
                move_direction = KB_EVENT_MAP[event.key]

    return move_direction


def generate_food(snake):
    snake_points = [x.get_point() for x in snake.flesh]
    available_points = []
    for x in range(WINDOW_SIZE_X):
        for y in range(WINDOW_SIZE_Y):
            if (x % SNAKE_WEIGHT == 0 and y % SNAKE_HEIGHT == 0) and (x, y) not in snake_points:
                available_points.append(Point(x, y))
    food = choice(available_points)
    print(f'generate food at:{food}')
    return food


def draw_picture(snake, food):
    for node in snake.flesh:
        draw_point(*node.get_point(), GREEN_COLOR)
    draw_point(*snake.snake_head.get_point(), ORANGE_COLOR)
    draw_point(*food.get_point(), BROWN_COLOR)


def draw_point(x, y, color):
    pygame.draw.rect(screen, color=color, rect=[x, y, SNAKE_WEIGHT, SNAKE_HEIGHT], width=1)


def check_game_end(snake):
    return snake.is_bite() or snake.is_over_border(WINDOW_SIZE_X, WINDOW_SIZE_Y)


def deal_game_end():
    print('game over')
    while True:
        time.sleep(10)


def check_eat(snake, food, score):
    if snake.is_eating(food) is True:
        snake.eat_food(food)
        food = generate_food(snake)
        score += 1
    return food, score


def draw_score_text(score_text):
    font_obj = pygame.font.Font(pygame.font.get_default_font(), 15)
    surface = font_obj.render(score_text, True, BLACK_COLOR)
    screen.blit(surface, (0, 0))


def draw_buttons(mouse_pos):
    # 如果鼠标悬停在按钮上，改变按钮颜色
    if button_start_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_start_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_start_rect)
    if button_quit_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_quit_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_quit_rect)

    font_obj = pygame.font.Font(pygame.font.get_default_font(), 15)
    text_surface_start = font_obj.render('start', True, BLACK_COLOR)
    text_surface_quit = font_obj.render('quit', True, BLACK_COLOR)
    text_rect_start = text_surface_start.get_rect(center=button_start_rect.center)
    text_rect_quit = text_surface_start.get_rect(center=button_quit_rect.center)
    screen.blit(text_surface_start, text_rect_start)
    screen.blit(text_surface_quit, text_rect_quit)


def game_init():
    score = 0
    move_direction = Direction.RIGHT
    snake = Snake(Point((WINDOW_SIZE_X / SNAKE_WEIGHT / 2) * SNAKE_WEIGHT, (WINDOW_SIZE_Y / SNAKE_HEIGHT / 2) * SNAKE_HEIGHT))
    food = generate_food(snake)
    return score, move_direction, snake, food


def check_time(last_refresh_time, difficulty):
    if last_refresh_time + difficulty < time.time():
        return True
    return False


def main_title():
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 1代表左键点击
                    if button_start_rect.collidepoint(mouse_pos):
                        starting(difficulty=Difficulty.LUNATIC)
                        print('game start')
                    if button_quit_rect.collidepoint(mouse_pos):
                        running = False
        screen.fill(WHITE_COLOR)
        draw_buttons(mouse_pos)
        pygame.display.flip()
    print('quit game')
    pygame.quit()


def starting(difficulty: float = Difficulty.EASY):
    score, move_direction, snake, food = game_init()
    draw_score_text(f'score:{score}')
    clock = pygame.time.Clock()
    while not check_game_end(snake):
        clock.tick(int(difficulty))
        screen.fill(WHITE_COLOR)
        draw_picture(snake, food)
        draw_score_text(f'score:{score}')
        pygame.display.flip()
        move_direction = check_event(move_direction)
        snake.move(move_direction)
        food, score = check_eat(snake, food, score)
        snake.check_grow()

    deal_game_end()



if __name__ == '__main__':
    pygame.init()
    # WINDOW_SIZE_X = 800
    # WINDOW_SIZE_Y = 800
    screen = pygame.display.set_mode(size=(WINDOW_SIZE_X, WINDOW_SIZE_Y), depth=32)
    pygame.display.set_caption('GreedEatSnake')
    main_title()
    # t = threading.Thread(target=main_title)
    # t.start()

