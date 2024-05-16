import curses
import random

# Game constants
SNAKE_CHAR = '#'
FOOD_CHAR = '@'
GROQ_CHAR = 'G'
POWER_UP_CHAR = '*'
INITIAL_SPEED = 100  # Initial snake movement speed in milliseconds

class GroqSnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.score = 0
        self.level = 1
        self.speed = INITIAL_SPEED
        self.snake = [(5, 5)]  # Initial snake position
        self.food = self.generate_food()
        self.groq_chip = self.generate_groq_chip()
        self.power_up = self.generate_power_up()
        self.direction = curses.KEY_RIGHT  # Initial direction
        self.paused = False

        # Set up the screen
        curses.curs_set(0)  # Hide the cursor
        self.stdscr.nodelay(True)  # Non-blocking input
        self.stdscr.timeout(self.speed)  # Timeout for input checking

        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_ORANGE, curses.COLOR_BLACK)  # Orange color for snake
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Red color for food
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Blue color for Groq chip
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Green color for power-up

    def run(self):
        while True:
            if not self.paused:
                self.handle_input()
                self.move_snake()
                self.draw_screen()
                self.check_collisions()

            key = self.stdscr.getch()
            if key == ord('p'):
                self.paused = not self.paused
                if self.paused:
                    self.stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 5, "PAUSED")
                    self.stdscr.refresh()
                else:
                    self.stdscr.timeout(self.speed)
            elif not self.paused:
                self.handle_input()

    def handle_input(self):
        key = self.stdscr.getch()
        if key == curses.KEY_UP and self.direction != curses.KEY_DOWN:
            self.direction = curses.KEY_UP
        elif key == curses.KEY_DOWN and self.direction != curses.KEY_UP:
            self.direction = curses.KEY_DOWN
        elif key == curses.KEY_LEFT and self.direction != curses.KEY_RIGHT:
            self.direction = curses.KEY_LEFT
        elif key == curses.KEY_RIGHT and self.direction != curses.KEY_LEFT:
            self.direction = curses.KEY_RIGHT

    def move_snake(self):
        head_x, head_y = self.snake[0]
        if self.direction == curses.KEY_UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == curses.KEY_DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == curses.KEY_LEFT:
            new_head = (head_x - 1, head_y)
        elif self.direction == curses.KEY_RIGHT:
            new_head = (head_x + 1, head_y)

        self.snake.insert(0, new_head)
        self.snake.pop()

    def draw_screen(self):
        self.stdscr.clear()
        self.draw_borders()
        for y, x in self.snake:
            self.stdscr.addch(x, y, SNAKE_CHAR, curses.color_pair(1))
        self.stdscr.addch(self.food[1], self.food[0], FOOD_CHAR, curses.color_pair(2))
        self.stdscr.addch(self.groq_chip[1], self.groq_chip[0], GROQ_CHAR, curses.color_pair(3))
        if self.power_up:
            self.stdscr.addch(self.power_up[1], self.power_up[0], POWER_UP_CHAR, curses.color_pair(4))
        self.stdscr.addstr(0, 0, f"Score: {self.score} Level: {self.level}")
        self.stdscr.refresh()

    def draw_borders(self):
        for x in range(curses.COLS):
            self.stdscr.addch(0, x, '#')
            self.stdscr.addch(curses.LINES - 1, x, '#')
        for y in range(curses.LINES):
            self.stdscr.addch(y, 0, '#')
            self.stdscr.addch(y, curses.COLS - 1, '#')

    def check_collisions(self):
        # Check for collision with food
        if self.snake[0] == self.food:
            self.score += 1
            self.snake.append(self.snake[-1])  # Increase snake length
            self.food = self.generate_food()
            if self.score % 5 == 0:  # Increase level every 5 points
                self.level += 1
                self.speed = max(50, self.speed - 10)
                self.stdscr.timeout(self.speed)

        # Check for collision with Groq chip
        if self.snake[0] == self.groq_chip:
            self.score += 5  # Higher score for Groq chip
            self.groq_chip = self.generate_groq_chip()

        # Check for collision with power-up
        if self.snake[0] == self.power_up:
            self.score += 2
            self.speed = max(50, self.speed - 20)  # Speed boost
            self.stdscr.timeout(self.speed)
            self.power_up = None

        # Check for collision with walls or self
        head_x, head_y = self.snake[0]
        if (head_x == 0 or head_x == curses.COLS - 1 or
            head_y == 0 or head_y == curses.LINES - 1 or
            self.snake[0] in self.snake[1:]):
            self.stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 5, "GAME OVER")
            self.stdscr.refresh()
            curses.napms(2000)
            curses.endwin()
            quit()

    def generate_food(self):
        while True:
            food = (random.randint(1, curses.COLS - 2), random.randint(1, curses.LINES - 2))
            if food not in self.snake and food != self.groq_chip and (self.power_up is None or food != self.power_up):
                return food

    def generate_groq_chip(self):
        while True:
            chip = (random.randint(1, curses.COLS - 2), random.randint(1, curses.LINES - 2))
            if chip not in self.snake and chip != self.food and (self.power_up is None or chip != self.power_up):
                return chip

    def generate_power_up(self):
        while True:
            power_up = (random.randint(1, curses.COLS - 2), random.randint(1, curses.LINES - 2))
            if power_up not in self.snake and power_up != self.food and power_up != self.groq_chip:
                return power_up

def main(stdscr):
    game = GroqSnakeGame(stdscr)
    game.run()

curses.wrapper(main)
