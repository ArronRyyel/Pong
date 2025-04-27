import turtle
import sys
import random
from PIL import Image 
import os
import pygame
import time
import math

# Constants
MIN_WIDTH = 800
MIN_HEIGHT = 600
DEFAULT_BALL_SPEED = 0.15
DEFAULT_PADDLE_SPEED = 20

class PongGame:
    def __init__(self):
        # Initialize pygame for sound
        pygame.init()
        pygame.mixer.init()
        
        # Game state variables
        self.score_a = 0
        self.score_b = 0
        self.game_running = False
        self.paused = False
        self.mode_selected = False
        self.one_player = False
        self.audio_enabled = True
        self.difficulty_level = "medium"
        self.selected_skin = "default"
        self.version = "1.0.0" 
        
        self.menu_elements = []  # Initialize menu elements list
        
        # Initialize screen
        self.setup_screen()
        
        # Load resources
        self.load_resources()
        
        # Initialize game elements
        self.show_start_screen()

    def setup_screen(self):
        """Set up the game screen with responsive dimensions."""
        self.screen = turtle.Screen()
        screen_width = max(self.screen.window_width(), MIN_WIDTH)
        screen_height = max(self.screen.window_height(), MIN_HEIGHT)
        
        # Calculate game area dimensions
        self.game_width = min(1000, int(screen_width * 0.95))
        self.game_height = min(800, int(screen_height * 0.95))
        
        # Calculate boundaries
        self.boundary_x = int(self.game_width / 2) - 10
        self.boundary_y = int(self.game_height / 2) - 10
        self.paddle_x_position = int(self.boundary_x * 0.9)
        
        # Set up the screen
        self.screen.title("Pong Game")
        self.screen.bgcolor("black")
        self.screen.setup(width=self.game_width, height=self.game_height)
        self.screen.tracer(0)
        
        # Calculate scale factor for responsive design
        self.scale_factor = min(self.game_width / 800, self.game_height / 600)
        
        # Game speeds
        self.ball_speed_x = DEFAULT_BALL_SPEED * self.scale_factor
        self.ball_speed_y = DEFAULT_BALL_SPEED * self.scale_factor
        self.paddle_speed = DEFAULT_PADDLE_SPEED * self.scale_factor

    def load_resources(self):
        """Load game resources (sounds, skins, etc.) with error handling."""
        # Set up sounds directory
        sounds_dir = "sounds"
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
        
        # Sound paths
        sound_files = {
            "paddle_hit": "sounds/boing-101318.wav",
            "wall_hit": "sounds/wall_hit-3-48114.wav",
            "score": "sounds/score.wav",
            "click": "sounds/click.wav"
        }
        
        # Load sounds
        self.sounds = {}
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    self.sounds[name] = None
                    print(f"Sound file not found: {path}")
            except (pygame.error, FileNotFoundError) as e:
                self.sounds[name] = None
                print(f"Error loading sound {path}: {e}")
        
        # Set up skins
        self.setup_skins()
    
    def setup_skins(self):
        """Set up ball skins with fallbacks."""
        self.original_skins = {
            "default": "#FF0000",
            "Basketball": "skins/skin ball.gif",
            "Pingpong Ball": "skins/pingpong.gif",
            "Tennis Ball": "skins/tennis.gif"
        }
        
        self.ball_skins = {}
        
        # Create skins directory if it doesn't exist
        if not os.path.exists("skins"):
            os.makedirs("skins")
            print("Created 'skins' directory. Please add skin images to this directory.")
        
        # Process each skin
        for skin, img in self.original_skins.items():
            if isinstance(img, str) and img.endswith(".gif"):
                if os.path.exists(img):
                    resized_img = self.resize_image(img)  
                    if resized_img:
                        self.ball_skins[skin] = resized_img
                        self.screen.addshape(resized_img)
                    else:
                        self.ball_skins[skin] = "#FF0000"  # Fallback
                else:
                    print(f"Skin image not found: {img}")
                    self.ball_skins[skin] = "#FF0000"  # Fallback
            else:
                self.ball_skins[skin] = img
    
    def resize_image(self, image_path, new_size=(80, 60)):
        """Resizes an image to a given size."""
        try:
            img = Image.open(image_path)
            img = img.resize(new_size)
            
            new_path = image_path.replace(".gif", "_resized.gif") 
            img.save(new_path)
            return new_path
        except (FileNotFoundError, IOError) as e:
            print(f"Error processing image {image_path}: {e}")
            return None
    
    def play_sound(self, sound_name):
        """Play a sound if audio is enabled and the sound exists."""
        if self.audio_enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except (pygame.error, AttributeError):
                pass  # Silently fail if sound playback fails
    
    def toggle_audio(self):
        """Toggle audio on/off."""
        self.audio_enabled = not self.audio_enabled
        self.play_sound("click")
        self.update_game_ui()
    
    def create_button(self, shape, position, size=1, onclick=None):
        """Create an interactive button."""
        button = turtle.Turtle()
        button.speed(0)
        button.penup()
        button.shape(shape)
        button.shapesize(size)
        button.goto(position)
        
        if onclick:
            self.menu_elements.append({
                "turtle": button,
                "x": position[0],
                "y": position[1],
                "width": 30 * size,
                "height": 30 * size,
                "onclick": onclick
            })
        else:
            self.menu_elements.append(button)
        
        return button
    
    def show_start_screen(self):
        """Show an attractive press-to-start screen before the main menu."""
        self.hide_menu()

    # Set background color to black
        self.screen.bgcolor("white")

    # Create decorative border with glowing effect
        self.draw_border(0, 0, self.game_width * 0.9, self.game_height * 0.8)

    # Create title with neon effect
        self.create_text(2, 102, "PONG", 
                font_size=int(60 * self.scale_factor),
                color="darkblue",)
        self.create_text(0, 100, "PONG", 
                font_size=int(60 * self.scale_factor),
                color="orange",)

    # Create pulsing "Press Anywhere" text
        press_text = self.create_text(0, 40, "Press Anywhere to Start", 
                            font_size=int(18 * self.scale_factor),
                            color="black")
        self.menu_elements.append(press_text)
    
    # Add version info
        try:
            version_text = f"Version {self.version}"
        except AttributeError:
            version_text = "Classic Pong"
    
        self.create_text(0, -self.game_height * 0.4 + 20, 
                version_text, 
                font_size=int(12 * self.scale_factor),
                color="gray70")
    
    # Add multiple animated balls without trails (to avoid visual clutter)
        balls = []
        ball_colors = ["red", "blue", "green", "yellow", "purple"]
    
        for i in range(3):
        # Create ball
            ball = turtle.Turtle()
            ball.shape("circle")
            ball.shapesize(0.7)
            ball.color(ball_colors[i % len(ball_colors)])
            ball.penup()  # Keep pen up to avoid drawing trails
        
        # Randomize starting position
            start_x = -200 + i * 100
            start_y = -50 + i * 40
            ball.goto(start_x, start_y)
        
        # Randomize direction and speed
            ball.dx = 2 + i * 0.5
            ball.dy = 1 + i * 0.3
        
            balls.append(ball)
            self.menu_elements.append(ball)
    
    # Variable to control animation state
        self.start_screen_active = True
    
        def animate_elements():
            """Animate all elements on the start screen."""
            if not hasattr(self, 'start_screen_active') or not self.start_screen_active:
                return
            
        # Animate balls
            for ball in balls:
            # Move ball
                ball.setx(ball.xcor() + ball.dx)
                ball.sety(ball.ycor() + ball.dy)
            
            # Bounce off the edges of the border
                border_x = self.game_width * 0.44
                border_y = self.game_height * 0.34
            
                if ball.xcor() > border_x or ball.xcor() < -border_x:
                    ball.dx *= -1
                    try:
                        self.play_sound("bounce")
                    except:
                        pass
                
                if ball.ycor() > border_y or ball.ycor() < -border_y:
                    ball.dy *= -1
                    try:
                        self.play_sound("bounce")
                    except:
                        pass
        
        # Pulse the "Press Anywhere" text - use simpler color changing technique
            try:
                import time
                pulse_colors = ["white", "cyan", "white", "cyan"]
                color_index = int(time.time() * 2) % len(pulse_colors)
                press_text.color(pulse_colors[color_index])
            except:
            # Fallback if time module isn't available
                pass
        
        # Continue animation if still on the start screen
            if hasattr(self, 'start_screen_active') and self.start_screen_active:
                self.screen.ontimer(animate_elements, 50)  # Lower frame rate for better performance
    
    # Start the animation
        animate_elements()
    
    # Set up event handlers
        def start_on_click(x, y):
            self.start_screen_active = False  # Stop animations
            try:
                self.play_sound("click")
            except:
                pass
        
        # Clean up
            self.screen.onscreenclick(None)  # Remove click handler
        
        # Go to main menu
            self.create_main_menu()
    
    # Listen for clicks
        self.screen.onscreenclick(start_on_click)
    
    # Try to add keyboard support
        try:
            self.screen.onkeypress(lambda: start_on_click(0, 0), "Return")
            self.screen.onkeypress(lambda: start_on_click(0, 0), "space")
        except:
            pass
        
        self.screen.listen()
        self.screen.update()
    
    def start_game(self):
        """Start the main game."""
        self.hide_menu()
        self.reset_scores()
        
        # Create game objects
        self.paddle_a = self.create_paddle(-self.paddle_x_position, 0)
        self.paddle_b = self.create_paddle(self.paddle_x_position, 0)
        self.ball = self.create_ball()
        self.pen = self.create_score_display()
        self.create_game_ui()
        
        # Set up key bindings
        self.setup_key_bindings()
        
        # Start game loop
        self.game_running = True
        self.game_loop()
    
    def setup_key_bindings(self):
        """Set up keyboard controls for the game."""
        self.screen.listen()
        self.screen.onkeypress(lambda: self.move_paddle(self.paddle_a, self.paddle_speed), "w")
        self.screen.onkeypress(lambda: self.move_paddle(self.paddle_a, -self.paddle_speed), "s")
        
        if not self.one_player:
            self.screen.onkeypress(lambda: self.move_paddle(self.paddle_b, self.paddle_speed), "Up")
            self.screen.onkeypress(lambda: self.move_paddle(self.paddle_b, -self.paddle_speed), "Down")
        
        self.screen.onkeypress(self.toggle_pause, "p")
        self.screen.onkeypress(self.return_to_menu, "Escape")
    
    def game_loop(self):
        """Main game loop."""
        ai_frame_counter = 0
        ai_recovery_counter = 0
    
        while self.game_running:
            self.screen.update()
        
            if not self.paused:
            # Move ball
                self.ball.setx(self.ball.xcor() + self.ball.dx)
                self.ball.sety(self.ball.ycor() + self.ball.dy)

            # AI player logic
                if self.one_player:
                    if ai_recovery_counter > 0:
                        ai_recovery_counter -= 1
                
                    ai_frame_counter += 1
                    if ai_frame_counter >= self.ai_reaction_delay and ai_recovery_counter == 0:
                        self.ai_move_paddle(self.paddle_b, self.ball)
                        ai_frame_counter = 0

            # Ball collision with top and bottom
                if self.ball.ycor() > self.boundary_y or self.ball.ycor() < -self.boundary_y:
                    self.ball.dy *= -1
                    self.play_sound("wall_hit")

            # Scoring
                if self.ball.xcor() > self.boundary_x:
                    self.score_a += 1
                    self.play_sound("score")
                    self.reset_ball()
                    self.update_score()
                    ai_recovery_counter = 30
                elif self.ball.xcor() < -self.boundary_x:
                    self.score_b += 1
                    self.play_sound("score")
                    self.reset_ball()
                    self.update_score()

            # Paddle collisions with improved bounce logic
                paddle_collision_margin = self.paddle_x_position - 10
                if self.check_paddle_collision(self.ball, self.paddle_b, paddle_collision_margin):
                    self.ball.dx = -abs(self.ball.dx)  # Ensure ball moves left
                    self.play_sound("paddle_hit")
                elif self.check_paddle_collision(self.ball, self.paddle_a, -paddle_collision_margin):
                    self.ball.dx = abs(self.ball.dx)  # Ensure ball moves right
                    self.play_sound("paddle_hit")
        
        # Control game speed
            time.sleep(0.01)
    
    def move_paddle(self, paddle, distance):
        """Move a paddle while staying within boundaries."""
        paddle_boundary = self.boundary_y - 100
        new_y = paddle.ycor() + distance
        if -paddle_boundary < new_y < paddle_boundary:
            paddle.sety(new_y)
    
    def ai_move_paddle(self, paddle, ball):
        """AI logic for moving the paddle."""
        # Don't move if ball is moving away
        if ball.dx < 0:
            if random.random() < 0.1:
                random_move = random.uniform(-5, 5)
                self.move_paddle(paddle, random_move)
            return
        
        # Predict ball position
        predicted_y = self.predict_ball_y(ball, paddle)
        
        # Apply difficulty factors
        edge_factor = 1.0
        if abs(ball.ycor()) > self.boundary_y * 0.75:
            edge_factor = 1.0 - (self.ai_edge_weakness * (abs(ball.ycor()) - self.boundary_y * 0.75) / (self.boundary_y * 0.25))
        
        perfect_y = predicted_y * edge_factor
        
        # Add randomness based on difficulty
        if random.random() > self.ai_accuracy:
            noise_factor = (1 - self.ai_accuracy) * (self.game_height / 5)
            perfect_y += random.uniform(-noise_factor, noise_factor)
        
        # Limit to screen boundaries
        perfect_y = max(-self.boundary_y + 50, min(self.boundary_y - 50, perfect_y))
        
        # Move paddle
        if perfect_y > paddle.ycor() + 10:
            move_amount = min(self.ai_max_speed, abs(perfect_y - paddle.ycor()))
            paddle.sety(paddle.ycor() + move_amount)
        elif perfect_y < paddle.ycor() - 10:
            move_amount = min(self.ai_max_speed, abs(perfect_y - paddle.ycor()))
            paddle.sety(paddle.ycor() - move_amount)
    
    def predict_ball_y(self, ball, paddle):
        """Predict where the ball will be when it reaches the paddle."""
        if ball.dx == 0:
            return ball.ycor()
        
        dist_x = abs(paddle.xcor() - ball.xcor())
        time_steps = dist_x / abs(ball.dx)
        predicted_y = ball.ycor() + (ball.dy * time_steps)
        effective_height = self.game_height - 20
        
        # Simulate bounces
        while abs(predicted_y) > effective_height/2:
            if predicted_y > effective_height/2:
                over = predicted_y - effective_height/2
                predicted_y = effective_height/2 - over
            elif predicted_y < -effective_height/2:
                under = -predicted_y - effective_height/2
                predicted_y = -effective_height/2 + under
        
        # Add prediction error
        error = random.uniform(-self.ai_prediction_error * (self.game_height/4), 
                              self.ai_prediction_error * (self.game_height/4))
        return predicted_y + error
    
    def check_paddle_collision(self, ball, paddle, x_boundary):
        """Check if the ball collides with a paddle."""
        paddle_width = 20
        paddle_height = 70
        # Check if ball is within paddle's vertical range
        if paddle.ycor() - paddle_height < ball.ycor() < paddle.ycor() + paddle_height:
        # For right paddle (positive x_boundary)
            if x_boundary > 0 and ball.xcor() + 10 >= x_boundary - paddle_width and ball.dx > 0:
                return True
        # For left paddle (negative x_boundary)
            elif x_boundary < 0 and ball.xcor() - 10 <= x_boundary + paddle_width and ball.dx < 0:
                return True
        return False
    
    def create_score_display(self):
        """Create the score display."""
        pen = turtle.Turtle()
        pen.speed(0)
        pen.color("black")
        pen.penup()
        pen.hideturtle()
        pen.goto(0, self.boundary_y - 50)
        self.update_score(pen)
        return pen
    
    def update_score(self, pen=None):
        """Update the score display."""
        pen = pen or self.pen
        if not pen:
            return
            
        pen.clear()
        font_size = max(18, min(24, int(self.game_height / 30)))
        scoreboard_y = self.boundary_y - (font_size * .1)
        pen.goto(0, scoreboard_y)
        pen.write(f"Player A: {self.score_a}  Player B: {self.score_b}", 
                 align="center", font=("Courier", font_size, "normal"))
    
    def create_paddle(self, x, y):
        """Create a paddle at the given position."""
        paddle = turtle.Turtle()
        paddle.speed(0)
        paddle.shape("square")
        paddle.color("black")
        paddle.shapesize(stretch_wid=5, stretch_len=1)
        paddle.penup()
        paddle.goto(x, y)
        return paddle
    
    def create_ball(self):
        """Create the game ball with the selected skin."""
        ball = turtle.Turtle()
        ball.speed(0)

        if self.selected_skin in self.ball_skins:
            skin = self.ball_skins[self.selected_skin]
            if isinstance(skin, str) and skin.endswith(".gif"):
                ball.shape(skin)
            else:
                ball.shape("circle")
                ball.color(skin)
        else:
            ball.shape("circle")
            ball.color("red")

        ball.penup()
        ball.goto(0, 0)
        ball.dx = random.choice([-self.ball_speed_x, self.ball_speed_x])
        ball.dy = random.choice([-self.ball_speed_y, self.ball_speed_y])
        return ball
    
    def reset_ball(self):
        """Reset the ball to the center with random direction."""
        self.ball.goto(0, 0)
        self.ball.dx = random.choice([-self.ball_speed_x, self.ball_speed_x])
        self.ball.dy = random.choice([-self.ball_speed_y, self.ball_speed_y])
    
    def reset_scores(self):
        """Reset the game scores."""
        self.score_a = 0
        self.score_b = 0
    
    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
        self.update_game_ui()
    
    def create_game_ui(self):
        """Create in-game UI elements."""
        self.settings_button = self.create_settings_button()
        self.audio_button = self.create_audio_button()
        self.screen.onscreenclick(self.handle_game_ui_click)
        self.update_game_ui()
    
    def handle_game_ui_click(self, x, y):
        """Handle clicks on game UI elements."""
        ui_margin = 40
        settings_x = -self.boundary_x + ui_margin
        audio_x = self.boundary_x - ui_margin
        scoreboard_y = self.boundary_y - (max(18, min(24, int(self.game_height / 30)) * .1))
        
        if (x < settings_x + 20 and x > settings_x - 20 and 
            y > scoreboard_y - 20 and y < scoreboard_y + 20):
            self.return_to_menu()
        elif (x > audio_x - 20 and x < audio_x + 20 and 
              y > scoreboard_y - 20 and y < scoreboard_y + 20):
            self.toggle_audio()
    
    def create_settings_button(self):
        """Create the settings button."""
        ui_margin = 40
        settings_x = -self.boundary_x + ui_margin
        scoreboard_y = self.boundary_y - (max(18, min(24, int(self.game_height / 30)) * .1))
        
        settings = turtle.Turtle()
        settings.speed(0)
        settings.penup()
        settings.shape("square")
        settings.color("black")
        settings.goto(settings_x, scoreboard_y)
        self.menu_elements.append(settings)
        return settings
    
    def create_audio_button(self):
        """Create the audio toggle button."""
        ui_margin = 40
        audio_x = self.boundary_x - ui_margin
        scoreboard_y = self.boundary_y - (max(18, min(24, int(self.game_height / 30)) * .1))
        
        audio = turtle.Turtle()
        audio.speed(0)
        audio.penup()
        audio.shape("circle")
        audio.color("black")
        audio.goto(audio_x, scoreboard_y)
        self.menu_elements.append(audio)
        return audio
    
    def update_game_ui(self):
        """Update the game UI elements."""
        if hasattr(self, 'audio_button'):
            self.audio_button.color("green" if self.audio_enabled else "red")
    
    def return_to_menu(self):
        """Return to the main menu."""
        self.play_sound("click")
        self.game_running = False
    
    # Clean up game objects
        if hasattr(self, 'paddle_a'):
            self.paddle_a.hideturtle()
        if hasattr(self, 'paddle_b'):
            self.paddle_b.hideturtle()
        if hasattr(self, 'ball'):
            self.ball.hideturtle()
        if hasattr(self, 'pen'):
            self.pen.clear()
    
    # Clear any click handlers
        self.screen.onscreenclick(None)
    
        self.create_main_menu()  # Go to main menu
    
    def select_game_mode(self, x, y):
        """Handle game mode selection from the main menu."""
        button_width = 100
        button_height = 20
        button_spacing = 60
        button_y_offset = 60
        
        self.play_sound("click")

        # Solo player button
        if (-button_width < x < button_width and 
            button_y_offset < y < button_y_offset + button_height*2):
            self.one_player = True
            self.mode_selected = True
            self.select_difficulty()
        
        # Two Player button
        elif (-button_width < x < button_width and 
              button_y_offset - button_spacing < y < button_y_offset - button_spacing + button_height*2):
            self.one_player = False
            self.mode_selected = True
            self.start_game()
        
        # Exit button
        elif (-button_width < x < button_width and 
              button_y_offset - button_spacing*2 < y < button_y_offset - button_spacing*2 + button_height*2):
            self.exit_game()
        
        # Select Skin button
        elif (-button_width < x < button_width and 
              button_y_offset - button_spacing*3 < y < button_y_offset - button_spacing*3 + button_height*2):
            self.select_skin()
            
        # Settings button
        elif (-button_width < x < button_width and 
              button_y_offset - button_spacing*4 < y < button_y_offset - button_spacing*4 + button_height*2):
            self.open_settings()
    
    def select_difficulty(self):
        """Show difficulty selection screen."""
        self.play_sound("click")
        self.hide_menu()
        
        button_width = 100
        button_height = 25
        button_spacing = 80
        title_y = self.game_height / 4
        first_button_y = title_y - 100
        
        # Title
        self.create_text(0, title_y, "Select Difficulty", font_size=max(20, int(self.game_height / 30)))
        
        # Difficulty buttons
        self.draw_border(0, first_button_y, button_width*2, button_height*2)
        self.create_text(0, first_button_y - 10, "Easy", font_size=max(16, int(self.game_height / 40)))
        
        self.draw_border(0, first_button_y - button_spacing, button_width*2, button_height*2)
        self.create_text(0, first_button_y - button_spacing - 10, "Medium", font_size=max(16, int(self.game_height / 40)))
        
        self.draw_border(0, first_button_y - button_spacing*2, button_width*2, button_height*2)
        self.create_text(0, first_button_y - button_spacing*2 - 10, "Hard", font_size=max(16, int(self.game_height / 40)))
        
        # Back button
        self.draw_border(0, first_button_y - button_spacing*3, button_width*2, button_height*1.5)
        self.create_text(0, first_button_y - button_spacing*3 - 10, "Back", font_size=max(14, int(self.game_height / 50)))
        
        def on_difficulty_click(x, y):
            self.play_sound("click")
            
            if -button_width < x < button_width and first_button_y - button_height < y < first_button_y + button_height:
                self.set_difficulty("easy")
                self.start_game()
            elif (-button_width < x < button_width and 
                  first_button_y - button_spacing - button_height < y < first_button_y - button_spacing + button_height):
                self.set_difficulty("medium")
                self.start_game()
            elif (-button_width < x < button_width and 
                  first_button_y - button_spacing*2 - button_height < y < first_button_y - button_spacing*2 + button_height):
                self.set_difficulty("hard")
                self.start_game()
            elif (-button_width < x < button_width and 
                  first_button_y - button_spacing*3 - button_height < y < first_button_y - button_spacing*3 + button_height):
                self.create_main_menu()
        
        self.screen.onscreenclick(on_difficulty_click)
        self.screen.update()
    
    def set_difficulty(self, level):
        """Set AI difficulty parameters."""
        self.difficulty_level = level
        
        if level == "easy":
            self.ai_accuracy = 0.5
            self.ai_reaction_delay = 10
            self.ai_max_speed = 10
            self.ai_prediction_error = 0.5
            self.ai_edge_weakness = 0.8
        elif level == "medium":
            self.ai_accuracy = 0.7
            self.ai_reaction_delay = 6
            self.ai_max_speed = 15
            self.ai_prediction_error = 0.3
            self.ai_edge_weakness = 0.5
        elif level == "hard":
            self.ai_accuracy = 0.85
            self.ai_reaction_delay = 2
            self.ai_max_speed = 18
            self.ai_prediction_error = 0.15
            self.ai_edge_weakness = 0.3
    
    def exit_game(self):
        """Cleanly exit the game."""
        self.play_sound("click")
        self.screen.bye()
        pygame.quit()
        sys.exit()
    
    def select_skin(self):
        """Show skin selection menu."""
        self.play_sound("click")
        self.hide_menu()

        title_y = self.game_height / 4
        self.create_text(0, title_y, "Selecting Ball Skin", font_size=max(20, int(self.game_height / 30)))
        
        skins = list(self.ball_skins.keys())
        skin_spacing = min(self.game_width / 6, 160)
        positions = []
        
        # Calculate skin positions
        for i in range(len(skins)):
            if len(skins) <= 4:
                pos_x = -skin_spacing * 1.5 + (i * skin_spacing)
                positions.append(pos_x)
            else:
                row = i // 4
                col = i % 4
                pos_x = -skin_spacing * 1.5 + (col * skin_spacing)
                pos_y = -row * skin_spacing
                positions.append((pos_x, pos_y))

        # Draw skin selection buttons
        for i, skin in enumerate(skins):
            if isinstance(positions[i], tuple):
                pos_x, pos_y = positions[i]
            else:
                pos_x = positions[i]
                pos_y = 0
                
            self.draw_border(pos_x, pos_y, skin_spacing * 0.6, skin_spacing * 0.6)

            if isinstance(self.ball_skins[skin], str) and self.ball_skins[skin].endswith(".gif"):
                try:
                    img_turtle = turtle.Turtle()
                    img_turtle.shape(self.ball_skins[skin])
                    img_turtle.penup()
                    img_turtle.goto(pos_x, pos_y)
                    self.menu_elements.append(img_turtle)
                except (turtle.TurtleGraphicsError, AttributeError) as e:
                    print(f"Error displaying skin {skin}: {e}")
                    self.create_text(pos_x, pos_y, "🔴", font_size=max(30, int(self.game_height / 20)))
            else:
                self.create_text(pos_x, pos_y, "🔴", font_size=max(30, int(self.game_height / 20)))

            self.create_text(pos_x, pos_y - skin_spacing * 0.5, skin.capitalize(), 
                           font_size=max(12, int(self.game_height / 60)))

        # Back button
        back_x = -self.boundary_x + 50
        back_y = self.boundary_y - 50
        self.draw_border(back_x, back_y, 50, 50)
        self.create_text(back_x, back_y, "←", font_size=max(16, int(self.game_height / 40)))
        
        def on_skin_click(x, y):
            self.play_sound("click")
            
            for i, skin in enumerate(skins):
                if isinstance(positions[i], tuple):
                    pos_x, pos_y = positions[i]
                else:
                    pos_x = positions[i]
                    pos_y = 0
                    
                if (pos_x - skin_spacing * 0.3 < x < pos_x + skin_spacing * 0.3 and 
                    pos_y - skin_spacing * 0.3 < y < pos_y + skin_spacing * 0.3):
                    self.selected_skin = skin
                    self.create_main_menu()

            # Back button
            if (back_x - 25 < x < back_x + 25 and 
                back_y - 25 < y < back_y + 25):
                self.create_main_menu()

        self.screen.onscreenclick(on_skin_click)
        self.screen.update()
    
    def open_settings(self):
        """Open settings menu."""
        self.play_sound("click")
        self.hide_menu()
        
        self.create_text(0, self.calc_height(20), "Settings", font_size=int(24 * self.scale_factor))
        
        # Volume setting
        self.draw_border(0, self.calc_height(10), self.calc_width(37.5), self.calc_height(7))
        self.create_text(0, self.calc_height(9), f"Audio: {'On' if self.audio_enabled else 'Off'}", 
                       font_size=int(16 * self.scale_factor))
        
        # Ball speed setting
        self.draw_border(0, self.calc_height(3), self.calc_width(37.5), self.calc_height(7))
        self.create_text(0, self.calc_height(2), f"Ball Speed: {self.ball_speed_x*500:.0f}", 
                       font_size=int(16 * self.scale_factor))
        
        # Paddle speed setting
        self.draw_border(0, self.calc_height(-4), self.calc_width(37.5), self.calc_height(7))
        self.create_text(0, self.calc_height(-5), f"Paddle Speed: {self.paddle_speed}", 
                       font_size=int(16 * self.scale_factor))
        
        # Back button
        self.draw_border(0, self.calc_height(-11), self.calc_width(25), self.calc_height(7))
        self.create_text(0, self.calc_height(-12), "Back to Menu", font_size=int(16 * self.scale_factor))
        
        def on_settings_click(x, y):
            self.play_sound("click")
            
            # Audio toggle
            if (-self.calc_width(18.75) < x < self.calc_width(18.75) and 
                self.calc_height(6.5) < y < self.calc_height(13.5)):
                self.audio_enabled = not self.audio_enabled
                self.open_settings()
                
            # Ball speed adjustment
            elif (-self.calc_width(18.75) < x < self.calc_width(18.75) and 
                  self.calc_height(-0.5) < y < self.calc_height(6.5)):
                self.ball_speed_x = min(0.4, self.ball_speed_x + 0.05)
                self.ball_speed_y = self.ball_speed_x
                self.open_settings()
                
            # Paddle speed adjustment
            elif (-self.calc_width(18.75) < x < self.calc_width(18.75) and 
                  self.calc_height(-7.5) < y < self.calc_height(-0.5)):
                self.paddle_speed = min(40, self.paddle_speed + 5)
                self.open_settings()
                
            # Back button
            elif (-self.calc_width(12.5) < x < self.calc_width(12.5) and 
                  self.calc_height(-14.5) < y < self.calc_height(-7.5)):
                self.create_main_menu()
        
        self.screen.onscreenclick(on_settings_click)
        self.screen.update()
    
    def create_main_menu(self):
        """Create the main menu screen."""
        self.hide_menu()
        
        # Title
        self.create_text(0, self.calc_height(25), "PONG GAME", font_size=int(36 * self.scale_factor))
        
        # Menu options
        menu_items = ["Solo Player", "Two Player", "Exit Game", "Select Skin", "Settings"]
        y_pos = self.calc_height(10)
        
        for item in menu_items:
            self.draw_border(0, y_pos, self.calc_width(25), self.calc_height(7))
            self.create_text(0, y_pos - self.calc_height(1), item, font_size=int(16 * self.scale_factor))
            y_pos -= self.calc_height(10)
        
        self.screen.onscreenclick(self.select_game_mode)
        self.screen.update()
    
    def hide_menu(self):
        """Hide all menu elements."""
        for element in self.menu_elements:
            if isinstance(element, dict):
                element["turtle"].clear()
                element["turtle"].hideturtle()
            else:
                element.clear()
                element.hideturtle()
        self.menu_elements.clear()
        self.screen.update()
    
    def draw_border(self, x, y, width, height, color="black", pen_width=3):
        """Draw a bordered rectangle."""
        border = turtle.Turtle()
        border.speed(0)
        border.penup()
        border.goto(x - width / 2, y - height / 2)
        border.pendown()
        border.pensize(int(3 * self.scale_factor))
        border.color(color)
        for _ in range(2):
            border.forward(width)
            border.left(90)
            border.forward(height)
            border.left(90)
        border.hideturtle()
        self.menu_elements.append(border)
    
    def create_text(self, x, y, text, font_size=16, color="black"):
        """Create text for the menu."""
        text_turtle = turtle.Turtle()
        text_turtle.hideturtle()
        text_turtle.penup()
        text_turtle.color(color)
        text_turtle.goto(x, y)
        text_turtle.write(text, align="center", font=("Courier", font_size, "bold"))
        self.menu_elements.append(text_turtle)
        return text_turtle  # Return the text turtle object
    
    def calc_width(self, percent):
        """Calculate width based on percentage."""
        return self.game_width * percent / 100
    
    def calc_height(self, percent):
        """Calculate height based on percentage."""
        return self.game_height * percent / 100

# Start the game
if __name__ == "__main__":
    game = PongGame()
    game.screen.mainloop()