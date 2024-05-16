import streamlit as st
import numpy as np
import time
import random

# Game constants
GRID_SIZE = 20
INITIAL_SPEED = 0.2  # Initial snake movement speed (lower is faster)
SNAKE_CHAR = '<div style="color: white;">■</div>'
FOOD_CHAR = '<div style="color: red;">■</div>'
GROQ_CHAR = '<div style="color: orange;">■</div>'
POWER_UP_CHAR = '<div style="color: green;">■</div>'

# Streamlit components
st.set_page_config(page_title="Byte Vipers by Vers3Dynamics", page_icon=":snake:", layout="centered")

# Game state
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        'score': 0,
        'level': 1,
        'speed': INITIAL_SPEED,
        'snake': [(5, 5)],
        'direction': 'RIGHT',
        'food': (10, 10),
        'groq_chip': (15, 15),
        'power_up': None,
        'game_over': False,
        'paused': False
    }

# Helper functions
def generate_food(snake, groq_chip, power_up):
    while True:
        food = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if food not in snake and food != groq_chip and (power_up is None or food != power_up):
            return food

def generate_groq_chip(snake, food, power_up):
    while True:
        chip = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if chip not in snake and chip != food and (power_up is None or chip != power_up):
            return chip

def generate_power_up(snake, food, groq_chip):
    while True:
        power_up = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if power_up not in snake and power_up != food and power_up != groq_chip:
            return power_up

def move_snake(snake, direction):
    head_x, head_y = snake[0]
    if direction == 'UP':
        new_head = (head_x, head_y - 1)
    elif direction == 'DOWN':
        new_head = (head_x, head_y + 1)
    elif direction == 'LEFT':
        new_head = (head_x - 1, head_y)
    elif direction == 'RIGHT':
        new_head = (head_x + 1, head_y)
    snake.insert(0, new_head)
    snake.pop()
    return snake

def check_collisions(snake, food, groq_chip, power_up):
    head_x, head_y = snake[0]
    # Check for collision with walls
    if head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE:
        return 'WALL'
    # Check for collision with self
    if snake[0] in snake[1:]:
        return 'SELF'
    # Check for collision with food
    if snake[0] == food:
        return 'FOOD'
    # Check for collision with Groq chip
    if snake[0] == groq_chip:
        return 'GROQ'
    # Check for collision with power-up
    if power_up and snake[0] == power_up:
        return 'POWER_UP'
    return None

def draw_grid(snake, food, groq_chip, power_up):
    grid = np.full((GRID_SIZE, GRID_SIZE), '', dtype=object)
    for x, y in snake:
        grid[y, x] = SNAKE_CHAR
    grid[food[1], food[0]] = FOOD_CHAR
    grid[groq_chip[1], groq_chip[0]] = GROQ_CHAR
    if power_up:
        grid[power_up[1], power_up[0]] = POWER_UP_CHAR
    grid_html = '<table style="border-spacing: 5px;">'
    for row in grid:
        grid_html += '<tr>'
        for cell in row:
            grid_html += f'<td style="width: 20px; height: 20px; text-align: center;">{cell}</td>'
        grid_html += '</tr>'
    grid_html += '</table>'
    return grid_html

# Game loop
def game_loop():
    state = st.session_state.game_state
    if state['paused']:
        return
    
    state['snake'] = move_snake(state['snake'], state['direction'])
    collision = check_collisions(state['snake'], state['food'], state['groq_chip'], state['power_up'])
    
    if collision == 'WALL' or collision == 'SELF':
        state['game_over'] = True
    elif collision == 'FOOD':
        state['score'] += 1
        state['snake'].append(state['snake'][-1])  # Increase snake length
        state['food'] = generate_food(state['snake'], state['groq_chip'], state['power_up'])
        if state['score'] % 5 == 0:
            state['level'] += 1
            state['speed'] = max(0.05, state['speed'] - 0.01)
    elif collision == 'GROQ':
        state['score'] += 5
        state['groq_chip'] = generate_groq_chip(state['snake'], state['food'], state['power_up'])
    elif collision == 'POWER_UP':
        state['score'] += 2
        state['speed'] = max(0.05, state['speed'] - 0.05)
        state['power_up'] = None
    
    st.session_state.game_state = state

# Streamlit UI
st.title("Byte Vipers")
st.markdown("Use the arrow keys to control the snake. Press 'P' to pause/resume.")

# Draw the grid
state = st.session_state.game_state
grid_html = draw_grid(state['snake'], state['food'], state['groq_chip'], state['power_up'])
st.markdown(grid_html, unsafe_allow_html=True)

# Game controls
if st.button('Start/Resume'):
    st.session_state.game_state['paused'] = False
    while not st.session_state.game_state['game_over']:
        game_loop()
        time.sleep(st.session_state.game_state['speed'])
        st.experimental_rerun()

if st.button('Pause'):
    st.session_state.game_state['paused'] = True

if st.session_state.game_state['game_over']:
    st.write("Game Over!")
    st.write(f"Final Score: {st.session_state.game_state['score']}")
    if st.button('Restart'):
        st.session_state.game_state = {
            'score': 0,
            'level': 1,
            'speed': INITIAL_SPEED,
            'snake': [(5, 5)],
            'direction': 'RIGHT',
            'food': (10, 10),
            'groq_chip': (15, 15),
            'power_up': None,
            'game_over': False,
            'paused': False
        }
        st.experimental_rerun()

# Keyboard controls
def handle_key(key):
    if key == 'up':
        if st.session_state.game_state['direction'] != 'DOWN':
            st.session_state.game_state['direction'] = 'UP'
    elif key == 'down':
        if st.session_state.game_state['direction'] != 'UP':
            st.session_state.game_state['direction'] = 'DOWN'
    elif key == 'left':
        if st.session_state.game_state['direction'] != 'RIGHT':
            st.session_state.game_state['direction'] = 'LEFT'
    elif key == 'right':
        if st.session_state.game_state['direction'] != 'LEFT':
            st.session_state.game_state['direction'] = 'RIGHT'
    elif key == 'p':
        st.session_state.game_state['paused'] = not st.session_state.game_state['paused']

st.text_input('Press arrow keys or P to control the game', on_change=handle_key, key='key_input')

# Run the game loop
while True:
    game_loop()
    time.sleep(st.session_state.game_state['speed'])
    st.experimental_rerun()
