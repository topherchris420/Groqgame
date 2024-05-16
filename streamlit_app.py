import streamlit as st
import numpy as np
from typing import Generator
from groq import Groq
import os
from typing import Optional, Dict, Union
import time
import random

# Game constants
GRID_SIZE = 20
INITIAL_SPEED = 0.2  # Initial snake movement speed (lower is faster)
SNAKE_CHAR = '<div style="color: orange;">Powered by Groq</div>'
FOOD_CHAR = '<div style="color: green;">Vers3Dynamics</div>'
GROQ_CHAR = '<div style="color: purple;">by christopher■</div>'
POWER_UP_CHAR = '<div style="color: green;">■</div>'

# Streamlit components
st.set_page_config(
    page_title="Byte Vypers by Vers3Dynamics", page_icon=":snake:", layout="centered"
)

# Game state
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "score": 0,
        "level": 1,
        "speed": INITIAL_SPEED,
        "snake": [(5, 5)],
        "direction": "RIGHT",
        "food": (10, 10),
        "groq_chip": (15, 15),
        "power_up": None,
        "game_over": False,
        "paused": False,
        "pending_direction": None,  # Store the new direction from key press
    }
def _get_system_prompt():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "system_prompt.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        prompt = file.read()
        return prompt

system_prompt = _get_system_prompt()




def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


icon("🧓🏼")
st.markdown(f'<a href="https://visualverse.streamlit.app/" style="text-decoration:none; color: #0e76a8;"><h2>Leonardo da Vinci, Reimagined by Vers3Dynamics</h2></a>', unsafe_allow_html=True)
st.subheader("Salve, sono Leonardo da Vinci📐. Iniziamo un viaggio di scoperta, dove i confini dell'immaginazione incontrano la precisione della scienza.", divider="rainbow", anchor=False)

# Add a picture with a caption
st.image("images/Leonardo-legacy.png", caption="Buongiorno", width=200)

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Define model details
models = {
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "llama2-70b-4096": {"name": "LLaMA2-70b-chat", "tokens": 4096, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

# Layout for model selection and max_tokens slider
col1, col2 = st.columns(2)

with col1:
    model_option = st.selectbox(
        "Connect with the perfect AI:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=2  # Default to LLaMA
    )

# Detect model change and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

max_tokens_range = models[model_option]["tokens"]

with col2:
    max_tokens = st.slider(
        "Max Tokens 🎨:",
        min_value=512,
        max_value=max_tokens_range,
        value=min(32768, max_tokens_range),
        step=512,
        help=f"Adjust the maximum number of tokens for the model's response. Max for selected model: {max_tokens_range}"
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = '🧬' if message["role"] == "assistant" else '🧑🏾‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

system_prompt = _get_system_prompt()
prompt = system_prompt
st.session_state.messages.append({"role": "user", "content": prompt})
st.session_state.selected_model = None


if prompt := st.chat_input("Ciao", key="user_input"):
    st.session_state.messages.append({"role": "user", "content": prompt})
   
    # Process the user's input and respond accordingly
    # Use the system_prompt variable to guide the chatbot's responses

    with st.chat_message("user", avatar='🧑🏾‍💻'):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            max_tokens=max_tokens,
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🧬"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(f"Oops! se seguirete i miei insegnamenti berrete un vino eccellente: {e}", icon="🐢🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})



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
    if state["paused"] or state['game_over']:
        return

    if state["pending_direction"]:  # Apply the pending direction change
        if state["pending_direction"] == "UP" and state["direction"] != "DOWN":
            state["direction"] = "UP"
        elif state["pending_direction"] == "DOWN" and state["direction"] != "UP":
            state["direction"] = "DOWN"
        elif state["pending_direction"] == "LEFT" and state["direction"] != "RIGHT":
            state["direction"] = "LEFT"
        elif state["pending_direction"] == "RIGHT" and state["direction"] != "LEFT":
            state["direction"] = "RIGHT"
        state["pending_direction"] = None  # Reset the pending direction

    state["snake"] = move_snake(state["snake"], state["direction"])
    collision = check_collisions(
        state["snake"], state["food"], state["groq_chip"], state["power_up"]
    )

    if collision == "WALL" or collision == "SELF":
        state["game_over"] = True
    elif collision == "FOOD":
        state["score"] += 1
        state["snake"].append(state["snake"][-1])  # Increase snake length
        state["food"] = generate_food(
            state["snake"], state["groq_chip"], state["power_up"]
        )
        if state["score"] % 5 == 0:
            state["level"] += 1
            state["speed"] = max(0.05, state["speed"] - 0.01)
    elif collision == "GROQ":
        state["score"] += 5
        state["groq_chip"] = generate_groq_chip(
            state["snake"], state["food"], state["power_up"]
        )
    elif collision == "POWER_UP":
        state["score"] += 2
        state["speed"] = max(0.05, state["speed"] - 0.05)
        state["power_up"] = None

    st.session_state.game_state = state

   # Schedule a rerun after a short delay
    time.sleep(st.session_state.game_state["speed"])
    st.experimental_rerun()

# Streamlit UI
st.title("Byte Vipers")
st.markdown("Use the arrow keys to control Groq. Press 'P' to pause/resume.")

# Create empty containers for dynamic updates
grid_container = st.empty()
score_container = st.empty()
level_container = st.empty()

# Draw the grid
state = st.session_state.game_state
grid_html = draw_grid(
    state["snake"], state["food"], state["groq_chip"], state["power_up"]
)
grid_container.markdown(grid_html, unsafe_allow_html=True)

# Display score and level
score_container.write(f"Score: {state['score']}")
level_container.write(f"Level: {state['level']}")

# Game controls
if st.button("Start/Resume"):
    st.session_state.game_state["paused"] = False
    game_loop() # Start the game loop

if st.button("Pause"):
    st.session_state.game_state["paused"] = True

if st.session_state.game_state["game_over"]:
    st.write("Game Over!")
    st.write(f"Final Score: {st.session_state.game_state['score']}")
    if st.button("Restart"):
        st.session_state.game_state = {
            "score": 0,
            "level": 1,
            "speed": INITIAL_SPEED,
            "snake": [(5, 5)],
            "direction": "RIGHT",
            "food": (10, 10),
            "groq_chip": (15, 15),
            "power_up": None,
            "game_over": False,
            "paused": False,
            "pending_direction": None,
        }
        st.experimental_rerun()


# JavaScript for capturing key events
st.markdown(
    """
<script>
document.addEventListener('keydown', function(event) {
  var key = event.key;
  var arrow_keys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'p'];
  if (arrow_keys.includes(key)) {
    var direction = '';
    if (key === 'ArrowUp') direction = 'UP';
    if (key === 'ArrowDown') direction = 'DOWN';
    if (key === 'ArrowLeft') direction = 'LEFT';
    if (key === 'ArrowRight') direction = 'RIGHT';
    if (key === 'p') direction = 'PAUSE';

    // Update the hidden input field with the direction
    document.getElementById('direction-input').value = direction;

    // Trigger a change event to notify Streamlit
    const inputEvent = new Event('input');
    document.getElementById('direction-input').dispatchEvent(inputEvent);
  }
});
</script>
""",
    unsafe_allow_html=True,
)

# Hidden input to capture direction changes
direction_input = st.empty()
direction = direction_input.text_input(
    "Direction", key="direction-input", label_visibility="hidden"
)

# Process key events
if direction:
    st.session_state.game_state["pending_direction"] = direction
    st.experimental_rerun()
