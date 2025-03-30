import turtle
import sys
import random
from PIL import Image 
import os
import pygame  

# Initialize pygame for sound
pygame.init()
pygame.mixer.init()

# Set up sounds
sounds_dir = "sounds"
if not os.path.exists(sounds_dir):
    os.makedirs(sounds_dir)

# Sound paths (you'll need to add sound files to this directory)
paddle_hit_sound = "sounds/boing-101318.wav"
wall_hit_sound = "sounds/wall_hit-3-48114.wav"
score_sound = "sounds/score.wav"
button_click_sound = "sounds/click.wav"

# Load sounds with improved error handling
paddle_sound = None
wall_sound = None
score_sound_obj = None
click_sound = None

try:
    if os.path.exists(paddle_hit_sound):
        paddle_sound = pygame.mixer.Sound(paddle_hit_sound)
    if os.path.exists(wall_hit_sound):
        wall_sound = pygame.mixer.Sound(wall_hit_sound)
    if os.path.exists(score_sound):
        score_sound_obj = pygame.mixer.Sound(score_sound)
    if os.path.exists(button_click_sound):
        click_sound = pygame.mixer.Sound(button_click_sound)
except (pygame.error, FileNotFoundError) as e:
    print(f"Error loading sound: {e}")
    print("Game will continue without sound effects.")

# Audio state - set to False if sounds couldn't be loaded
audio_enabled = any([paddle_sound, wall_sound, score_sound_obj, click_sound])

wn = turtle.Screen()
wn.title("Pong Game")
wn.bgcolor("white")
wn.setup(width=1000, height=800)
wn.tracer(0)

def resize_image(image_path, new_size=(80, 60)):
    """Resizes the image to a given size and saves it as a new file."""
    try:
        img = Image.open(image_path)
        img = img.resize(new_size)
        
        new_path = image_path.replace(".gif", "_resized.gif") 
        img.save(new_path)
        return new_path
    except (FileNotFoundError, IOError) as e:
        print(f"Error processing image {image_path}: {e}")
        return None

original_skins = {
    "default": "#FF0000",
    "Basketball": "skins/skin ball.gif",
    "Pingpong Ball": "skins/pingpong.gif",
    "Tennis Ball": "skins/tennis.gif"
}

ball_skins = {}

# Create skins directory if it doesn't exist
if not os.path.exists("skins"):
    os.makedirs("skins")
    print("Created 'skins' directory. Please add skin images to this directory.")

for skin, img in original_skins.items():
    if isinstance(img, str) and img.endswith(".gif"):
        if os.path.exists(img):
            resized_img = resize_image(img)  
            if resized_img:
                ball_skins[skin] = resized_img
                wn.addshape(resized_img)
            else:
                ball_skins[skin] = "#FF0000"  # Fallback to red if resize fails
        else:
            print(f"Skin image not found: {img}")
            ball_skins[skin] = "#FF0000"  # Fallback to red if file missing
    else:
        ball_skins[skin] = img  

selected_skin = "default"

# Initialize scores
score_a = 0
score_b = 0

# Game mode selection
mode_selected = False
one_player = False
game_running = False
game_paused = False

# AI difficulty level (new)
difficulty_level = "medium"  # Default difficulty
ai_accuracy = 0.7  # How accurately AI follows the ball (0.0-1.0)
ai_reaction_delay = 3  # Frames to wait before AI reacts
ai_max_speed = 15  # Maximum AI paddle speed (adjusted per difficulty)
ai_prediction_error = 0.3  # How much error in predicting ball trajectory
ai_edge_weakness = 0.5  # AI is less effective at the edges of the screen
ai_recovery_delay = 0  # Delay after AI misses before returning to normal behavior

# Paddle and ball speed
paddle_speed = 20
ball_speed_x = 0.20
ball_speed_y = 0.20

# List to track menu elements
menu_elements = []

def play_sound(sound):
    """Play a sound if audio is enabled and the sound exists."""
    if audio_enabled and sound is not None:
        try:
            sound.play()
        except (pygame.error, AttributeError):
            pass  # Silently fail if sound playback fails

def toggle_audio():
    """Toggle audio on/off."""
    global audio_enabled
    audio_enabled = not audio_enabled
    play_sound(click_sound)
    # Update the audio button if it's visible
    update_game_ui()

def create_button(shape, position, size=1, onclick=None):
    """Create an interactive button."""
    button = turtle.Turtle()
    button.speed(0)
    button.penup()
    button.shape(shape)
    button.shapesize(size)
    button.goto(position)
    
    # Store button info for click detection
    if onclick:
        menu_elements.append({
            "turtle": button,
            "x": position[0],
            "y": position[1],
            "width": 30 * size,
            "height": 30 * size,
            "onclick": onclick
        })
    else:
        menu_elements.append(button)
    
    return button

def start_game():
    global paddle_a, paddle_b, ball, pen, score_a, score_b, game_running
    hide_menu()
    
    paddle_a = create_paddle(-450, 0)
    paddle_b = create_paddle(450, 0)
    ball = create_ball()
    pen = create_score_display()
    create_game_ui()
    
    game_running = True
    
    wn.listen()
    wn.onkeypress(lambda: move_paddle(paddle_a, paddle_speed), "w")
    wn.onkeypress(lambda: move_paddle(paddle_a, -paddle_speed), "s")
    
    if not one_player:
        wn.onkeypress(lambda: move_paddle(paddle_b, paddle_speed), "Up")
        wn.onkeypress(lambda: move_paddle(paddle_b, -paddle_speed), "Down")
    
    wn.onkeypress(toggle_pause, "p")
    
    main_game_loop()

def main_game_loop():
    """Main game loop separated for pause functionality."""
    global game_running, game_paused, score_a, score_b, ai_recovery_delay
    
    # For AI reaction delay tracking
    ai_frame_counter = 0
    ai_recovery_counter = 0
    
    while game_running:
        wn.update()
        
        if not game_paused:
            ball.setx(ball.xcor() + ball.dx)
            ball.sety(ball.ycor() + ball.dy)

            if one_player:
                # Handle AI recovery delay after player scores
                if ai_recovery_counter > 0:
                    ai_recovery_counter -= 1
                
                # Implement AI delay based on difficulty
                ai_frame_counter += 1
                if ai_frame_counter >= ai_reaction_delay and ai_recovery_counter == 0:
                    ai_move_paddle(paddle_b, ball)
                    ai_frame_counter = 0

            # Ball collision with top and bottom
            if ball.ycor() > 390 or ball.ycor() < -390:
                ball.dy *= -1
                play_sound(wall_sound)

            # Ball collision with left and right walls (scoring)
            if ball.xcor() > 490:
                score_a += 1
                play_sound(score_sound_obj)
                reset_ball(ball)
                update_score(pen)
                # Add recovery delay for AI after player scores
                ai_recovery_counter = 30  # Delay AI response briefly after conceding
            elif ball.xcor() < -490:
                score_b += 1
                play_sound(score_sound_obj)
                reset_ball(ball)
                update_score(pen)

            # Ball collision with paddles
            if check_paddle_collision(ball, paddle_b, 430) or check_paddle_collision(ball, paddle_a, -430):
                ball.dx *= -1
                play_sound(paddle_sound)

def toggle_pause():
    """Pause or unpause the game."""
    global game_paused
    game_paused = not game_paused
    update_game_ui()

def create_game_ui():
    """Create in-game UI elements (settings, audio buttons)."""
    global settings_button, audio_button
    
    # Clear any previous onscreenclick handlers
    wn.onscreenclick(None)
    
    # Try to add gear icon shape, but handle exceptions
    try:
        wn.addshape("gear", turtle.Shape("compound"))
        gear = ((0, 0), (10, 10), (0, 20), (-10, 10))
        wn.addshape("gear", turtle.Shape("polygon", gear))
    except turtle.TurtleGraphicsError:
        print("Could not create custom gear shape")
    
    # Use square as placeholder for settings and audio buttons
    settings_button = create_settings_button()
    audio_button = create_audio_button()
    
    # Set up a new click handler specifically for game UI
    wn.onscreenclick(handle_game_ui_click)
    
    update_game_ui()

def handle_game_ui_click(x, y):
    """Handle clicks on game UI elements during gameplay."""
    # Check if settings button was clicked
    if x < -450 and x > -490 and y > 350 and y < 390:
        return_to_menu()
    # Check if audio button was clicked
    elif x > 450 and x < 490 and y > 350 and y < 390:
        toggle_audio()
        
def create_settings_button():
    """Create the settings button."""
    settings = turtle.Turtle()
    settings.speed(0)
    settings.penup()
    settings.shape("square")
    settings.color("black")
    settings.goto(-470, 370)
    menu_elements.append(settings)
    return settings

def create_audio_button():
    """Create the audio toggle button."""
    audio = turtle.Turtle()
    audio.speed(0)
    audio.penup()
    audio.shape("circle")
    audio.color("black")
    audio.goto(470, 370)
    audio.onclick(lambda x, y: toggle_audio())
    menu_elements.append(audio)
    return audio

def update_game_ui():
    """Update UI elements based on current state."""
    if 'audio_button' in globals():
        if audio_enabled:
            audio_button.color("green")
        else:
            audio_button.color("red")

def return_to_menu():
    """Return to the main menu."""
    global game_running, game_paused, score_a, score_b
    
    play_sound(click_sound)
    game_running = False
    game_paused = False
    score_a = 0
    score_b = 0
    
    # Clean up game objects
    if 'paddle_a' in globals():
        paddle_a.hideturtle()
    if 'paddle_b' in globals():
        paddle_b.hideturtle()
    if 'ball' in globals():
        ball.hideturtle()
    if 'pen' in globals():
        pen.clear()
    
    # Clear any click handlers
    wn.onscreenclick(None)
    
    draw_main_menu()

def move_paddle(paddle, distance):
    """Moves the paddle up or down while staying within screen limits."""
    new_y = paddle.ycor() + distance
    if -350 < new_y < 350:
        paddle.sety(new_y)

def predict_ball_y(ball, paddle):
    """Predict where ball will be when it reaches the paddle's x position."""
    # Calculate time to reach paddle
    if ball.dx == 0:  # Avoid division by zero
        return ball.ycor()
    
    # Distance to paddle
    dist_x = abs(paddle.xcor() - ball.xcor())
    
    # Time to reach paddle (in game steps)
    time_steps = dist_x / abs(ball.dx)
    
    # Calculate Y position
    predicted_y = ball.ycor() + (ball.dy * time_steps)
    
    # Account for bounces off top and bottom
    screen_height = 800
    effective_height = screen_height - 20  # Adjust for ball size
    
    # Simulate bounces to get accurate prediction
    while abs(predicted_y) > effective_height/2:
        if predicted_y > effective_height/2:
            # Bounce off top
            over = predicted_y - effective_height/2
            predicted_y = effective_height/2 - over
        elif predicted_y < -effective_height/2:
            # Bounce off bottom
            under = -predicted_y - effective_height/2
            predicted_y = -effective_height/2 + under
    
    # Add prediction error based on difficulty
    error = random.uniform(-ai_prediction_error * 200, ai_prediction_error * 200)
    predicted_y += error
    
    return predicted_y

def ai_move_paddle(paddle, ball):
    """Moves AI paddle based on difficulty level."""
    # Don't move if ball is moving away from the AI
    if ball.dx < 0:
        # Sometimes make small random movements when ball is moving away
        if random.random() < 0.1:
            random_move = random.uniform(-5, 5)
            move_paddle(paddle, random_move)
        return
    
    # For more human-like behavior: Add weakness near the edges
    edge_factor = 1.0
    if abs(ball.ycor()) > 300:
        # AI is less effective near the edges
        edge_factor = 1.0 - (ai_edge_weakness * (abs(ball.ycor()) - 300) / 100)
        
    # Predict where the ball will be when it reaches the paddle
    predicted_y = predict_ball_y(ball, paddle)
    
    # Calculate perfect position (where AI should move) with limitations
    perfect_y = predicted_y * edge_factor
    
    # Add randomness based on AI accuracy
    if random.random() > ai_accuracy:
        # Add noise to the target position
        noise_factor = (1 - ai_accuracy) * 150  # More noise for lower accuracy
        perfect_y += random.uniform(-noise_factor, noise_factor)
    
    # Limit AI to screen boundaries
    perfect_y = max(-350, min(350, perfect_y))
    
    # Move towards the calculated position (with speed based on difficulty)
    if perfect_y > paddle.ycor() + 10:  # Add deadzone
        move_amount = min(ai_max_speed, abs(perfect_y - paddle.ycor()))
        paddle.sety(paddle.ycor() + move_amount)
    elif perfect_y < paddle.ycor() - 10:  # Add deadzone
        move_amount = min(ai_max_speed, abs(perfect_y - paddle.ycor()))
        paddle.sety(paddle.ycor() - move_amount)

def check_paddle_collision(ball, paddle, x_boundary):
    """Checks if the ball collides with a paddle."""
    return abs(ball.xcor() - x_boundary) < 10 and paddle.ycor() - 50 < ball.ycor() < paddle.ycor() + 50

def create_score_display():
    """Creates the scoreboard display."""
    pen = turtle.Turtle()
    pen.speed(0)
    pen.color("black")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 350)
    pen.write(f"Player A: {score_a}  Player B: {score_b}", align="center", font=("Courier", 24, "normal"))
    return pen

def update_score(pen):
    """Updates the scoreboard."""
    pen.clear()
    pen.write(f"Player A: {score_a}  Player B: {score_b}", align="center", font=("Courier", 24, "normal"))

def create_paddle(x, y):
    """Creates a paddle at the given position."""
    paddle = turtle.Turtle()
    paddle.speed(0)
    paddle.shape("square")
    paddle.color("black")
    paddle.shapesize(stretch_wid=7, stretch_len=2)
    paddle.penup()
    paddle.goto(x, y)
    return paddle

def create_ball():
    """Creates the ball with a selected skin."""
    ball = turtle.Turtle()
    ball.speed(0)

    if selected_skin in ball_skins:
        skin = ball_skins[selected_skin]
        if isinstance(skin, str) and skin.endswith(".gif"):
            ball.shape(skin)  # Apply resized image
        else:
            ball.shape("circle")
            if isinstance(skin, str):
                try:
                    ball.color(skin)
                except turtle.TurtleGraphicsError:
                    ball.color("red")  # Fallback
            else:
                ball.color("red")
    else:
        ball.shape("circle")
        ball.color("red")  # Default fallback

    ball.penup()
    ball.goto(0, 0)
    ball.dx = random.choice([-ball_speed_x, ball_speed_x])
    ball.dy = random.choice([-ball_speed_y, ball_speed_y])
    return ball

def reset_ball(ball):
    """Resets the ball to the center and randomly selects a new direction."""
    ball.goto(0, 0)
    ball.dx = random.choice([-ball_speed_x, ball_speed_x])
    ball.dy = random.choice([-ball_speed_y, ball_speed_y])

def select_game_mode(x, y):
    """Handles game mode selection."""
    global mode_selected, one_player

    play_sound(click_sound)

    if -100 < x < 100 and 40 < y < 80:  # Solo Player
        one_player = True
        mode_selected = True
        select_difficulty()  # Show difficulty selection instead of starting game immediately
    
    elif -100 < x < 100 and -20 < y < 20:  # Two Player
        one_player = False
        mode_selected = True
        start_game()
    
    elif -100 < x < 100 and -80 < y < -40: 
        exit_game()
    
    elif -100 < x < 100 and -140 < y < -100:  # Select Skin
        select_skin()
        
    elif -100 < x < 100 and -200 < y < -160:  # Settings
        open_settings()

def select_difficulty():
    """Shows the difficulty selection screen."""
    play_sound(click_sound)
    hide_menu()
    
    create_text(0, 200, "Select Difficulty", font_size=28)
    
    # Draw difficulty buttons
    draw_border(0, 100, 200, 50)
    create_text(0, 90, "Easy", font_size=20)
    
    draw_border(0, 20, 200, 50)
    create_text(0, 10, "Medium", font_size=20)
    
    draw_border(0, -60, 200, 50)
    create_text(0, -70, "Hard", font_size=20)
    
    # Back button
    draw_border(0, -140, 200, 40)
    create_text(0, -150, "Back", font_size=18)
    
    def on_difficulty_click(x, y):
        global difficulty_level, ai_accuracy, ai_reaction_delay, ai_max_speed, ai_prediction_error, ai_edge_weakness
        
        play_sound(click_sound)
        
        if -100 < x < 100 and 75 < y < 125:  # Easy
            difficulty_level = "easy"
            ai_accuracy = 0.5        # Lower accuracy
            ai_reaction_delay = 10    # Slow reaction time
            ai_max_speed = 10        # Slower paddle movement
            ai_prediction_error = 0.5 # High error in prediction
            ai_edge_weakness = 0.8   # Very weak near edges
            start_game()
            
        elif -100 < x < 100 and -5 < y < 45:  # Medium
            difficulty_level = "medium"
            ai_accuracy = 0.7        # Medium accuracy
            ai_reaction_delay = 6    # Medium reaction time
            ai_max_speed = 15        # Medium paddle speed
            ai_prediction_error = 0.3 # Medium prediction error
            ai_edge_weakness = 0.5   # Somewhat weak near edges
            start_game()
            
        elif -100 < x < 100 and -85 < y < -35:  # Hard
            difficulty_level = "hard"
            ai_accuracy = 0.85       # High accuracy (but not perfect)
            ai_reaction_delay = 2    # Quick reaction time
            ai_max_speed = 18        # Fast paddle movement
            ai_prediction_error = 0.15 # Low prediction error
            ai_edge_weakness = 0.3   # Slightly weak near edges
            start_game()
            
        elif -100 < x < 100 and -160 < y < -120:  # Back
            draw_main_menu()
    
    wn.onscreenclick(on_difficulty_click)
    wn.update()
        
def exit_game():
    play_sound(click_sound)
    wn.bye()
    pygame.quit()
    sys.exit()
    
def select_skin():
    """Displays the skin selection menu."""
    play_sound(click_sound)
    hide_menu()

    create_text(0, 200, "Selecting Ball Skin", font_size=24)
    
    skins = list(ball_skins.keys())
    positions = [-250, -80, 80, 250]

    for i, skin in enumerate(skins):
        draw_border(positions[i], 0, 120, 120)

        if isinstance(ball_skins[skin], str) and ball_skins[skin].endswith(".gif"):
            # Create image turtle for skins
            try:
                img_turtle = turtle.Turtle()
                img_turtle.shape(ball_skins[skin])
                img_turtle.penup()
                img_turtle.goto(positions[i], 0)
                menu_elements.append(img_turtle)
            except (turtle.TurtleGraphicsError, AttributeError) as e:
                print(f"Error displaying skin {skin}: {e}")
                create_text(positions[i], 0, "🔴", font_size=40)
        else:
            create_text(positions[i], 0, "🔴", font_size=40)  

        create_text(positions[i], -80, skin.capitalize())

    def on_click(x, y):
        global selected_skin
        play_sound(click_sound)
        for i, skin in enumerate(skins):
            if positions[i] - 60 < x < positions[i] + 60 and -60 < y < 60:
                selected_skin = skin
                draw_main_menu()

        if -425 < x < -375 and 275 < y < 325:
            draw_main_menu()

    wn.onscreenclick(on_click)
    wn.update()

    # Back button
    draw_border(-400, 300, 50, 50)
    create_text(-400, 300, "←")
    wn.update()

def open_settings():
    """Opens the settings menu."""
    play_sound(click_sound)
    hide_menu()
    
    create_text(0, 200, "Settings", font_size=24)
    
    # Volume slider
    draw_border(0, 100, 300, 40)
    create_text(0, 90, f"Audio: {'On' if audio_enabled else 'Off'}")
    
    # Ball speed
    draw_border(0, 30, 300, 40)
    create_text(0, 20, f"Ball Speed: {ball_speed_x*500:.0f}")
    
    # Paddle speed
    draw_border(0, -40, 300, 40)
    create_text(0, -50, f"Paddle Speed: {paddle_speed}")
    
    # Back button
    draw_border(0, -110, 200, 40)
    create_text(0, -120, "Back to Menu")
    
    def on_settings_click(x, y):
        global audio_enabled, ball_speed_x, ball_speed_y, paddle_speed
        
        play_sound(click_sound)
        
        # Check audio toggle
        if -150 < x < 150 and 80 < y < 120:
            audio_enabled = not audio_enabled
            open_settings()  # Refresh the settings screen
            
        # Check ball speed slider
        elif -150 < x < 150 and 10 < y < 50:
            ball_speed_x = min(0.4, ball_speed_x + 0.05)
            ball_speed_y = ball_speed_x
            open_settings()
            
        # Check paddle speed slider
        elif -150 < x < 150 and -60 < y < -20:
            paddle_speed = min(40, paddle_speed + 5)
            open_settings()
            
        # Check back button
        elif -100 < x < 100 and -130 < y < -90:
            draw_main_menu()
    
    wn.onscreenclick(on_settings_click)
    wn.update()

def draw_main_menu():
    """Draws the main menu."""
    hide_menu()
    
    # Title
    create_text(0, 250, "PONG GAME", font_size=36)
    
    # Menu options
    draw_border(0, 60, 200, 40)
    create_text(0, 50, "Solo Player")
    
    draw_border(0, 0, 200, 40)
    create_text(0, -10, "Two Player")
    
    draw_border(0, -60, 200, 40)
    create_text(0, -70, "Exit Game")
    
    draw_border(0, -120, 200, 40)
    create_text(0, -130, "Select Skin")
    
    draw_border(0, -180, 200, 40)
    create_text(0, -190, "Settings")
    
    wn.onscreenclick(select_game_mode)
    wn.update()

def hide_menu():
    """Hides the menu elements."""
    for element in menu_elements:
        if isinstance(element, dict):
            element["turtle"].clear()
            element["turtle"].hideturtle()
        else:
            element.clear()
            element.hideturtle()
    menu_elements.clear()
    wn.update()

def draw_border(x, y, width, height):
    """Draws a bordered rectangle."""
    border = turtle.Turtle()
    border.speed(0)
    border.penup()
    border.goto(x - width / 2, y - height / 2)
    border.pendown()
    border.pensize(3)
    border.color("black")
    for _ in range(2):
        border.forward(width)
        border.left(90)
        border.forward(height)
        border.left(90)
    border.hideturtle()
    menu_elements.append(border)

def create_text(x, y, text, font_size=16):
    """Creates text for the menu."""
    text_turtle = turtle.Turtle()
    text_turtle.hideturtle()
    text_turtle.penup()
    text_turtle.color("black")
    text_turtle.goto(x, y - 5)
    text_turtle.write(text, align="center", font=("Courier", font_size, "bold"))
    menu_elements.append(text_turtle)

# Create sounds directory if it doesn't exist
if not os.path.exists("sounds"):
    os.makedirs("sounds")
    print("Created 'sounds' directory. Please add sound files to this directory.")
    print("The following sound files are needed:")
    print(f" - {paddle_hit_sound}")
    print(f" - {wall_hit_sound}")
    print(f" - {score_sound}")
    print(f" - {button_click_sound}")

# Initialize main menu
draw_main_menu()

# Main game loop
while True:
    wn.update()
    if game_running:
        continue