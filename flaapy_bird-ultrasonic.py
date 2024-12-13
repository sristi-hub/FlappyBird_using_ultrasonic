import pygame
import serial
import sys
import os
import time
import random

# Stable distance reading function
def get_stable_distance(ser, num_samples=3, threshold=5):
    """
    Takes multiple readings from the ultrasonic sensor, removes outliers,
    and returns the average distance.
    """
    distances = []
    
    for _ in range(num_samples):
        try:
            ser.reset_input_buffer()
            ser.write(b'R')
            time.sleep(0.005)
            
            if ser.in_waiting > 0:
                distance = int(ser.readline().decode('utf-8').strip())
                distances.append(distance)
        except (ValueError, serial.SerialException):
            continue
    
    if not distances:
        return 0
    
    mean_distance = sum(distances) / len(distances)
    
    filtered_distances = [
        d for d in distances 
        if abs(d - mean_distance) < threshold
    ]
    
    return sum(filtered_distances) / len(filtered_distances) if filtered_distances else mean_distance

# Set up the serial communication
try:
    ser = serial.Serial('COM6', 9600, timeout=0.01)     #COM port should be same port where arduino is connected
except serial.SerialException as e:
    print(f"Could not open serial port: {e}")
    sys.exit(1)

time.sleep(1 )  # Allow time for the Arduino to initialize

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BROWN = (92, 64, 51)
RED = (255, 0, 0)

# Screen dimensions
SCREEN_WIDTH =1518      #dimension are taken from the size of the background-pic
SCREEN_HEIGHT =816

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bird - Score: 0")

# High score file
HIGH_SCORE_FILE = "high_score.txt"

# Game settings
GRAVITY = 0.6                            #gravity, which pull bird downwards
FLAP_STRENGTH = -3                       #-ve means it provides upward velocity to the bird
PIPE_SPEED = 3                           #apporaching pipe speed
PIPE_GAP = 150
clock = pygame.time.Clock()

# Load images once
background = pygame.image.load("flappy_bird_background.jpg").convert()
bird_image = pygame.image.load("Flappy-bird.png").convert_alpha()
bird_image = pygame.transform.scale(bird_image, (40, 40))  # Scale to fit

# Bird class
class Bird:
    def __init__(self):
        self.x = 500                      #position of the bird from the left side of the screen
        self.y = SCREEN_HEIGHT // 2       #height at which bird lies initially is the middle of the screen_height
        self.velocity = 0                 #bird is initially at rest
        self.radius = 20

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        bird_width, bird_height = bird_image.get_size()
        screen.blit(bird_image, (self.x - bird_width // 2, self.y - bird_height // 2))

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.width = 50
        self.scored = False

    def move(self):
        self.x -= PIPE_SPEED

    def draw(self):
        pygame.draw.rect(screen, BROWN, (self.x, 0, self.width, self.height))
        pygame.draw.rect(screen, BROWN, (self.x, self.height + PIPE_GAP, self.width, SCREEN_HEIGHT))

    def off_screen(self):
        return self.x < -self.width

    def collision(self, bird):
        if bird.y - bird.radius < self.height and bird.x + bird.radius > self.x and bird.x - bird.radius < self.x + self.width:
            return True
        if bird.y + bird.radius > self.height + PIPE_GAP and bird.x + bird.radius > self.x and bird.x - bird.radius < self.x + self.width:
            return True
        return False

# Function to load the high score
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read().strip())
    return 0

# Function to save the high score
def save_high_score(high_score):
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(high_score))

# Game over screen
def game_over(score):
    bg_x = 0
    running = True
    restart = False
     # Load the high score
    high_score = load_high_score()
    # Update the high score if necessary
    if score > high_score:
        high_score = score
        save_high_score(high_score)
    while running:
        # Scroll the background
        bg_x -= 2
        if abs(bg_x) > SCREEN_WIDTH:
            bg_x = 0

        # Draw scrolling background
        screen.blit(background, (bg_x, 0))
        screen.blit(background, (bg_x + SCREEN_WIDTH, 0))

        # Display Game Over and Score text
        font_large = pygame.font.Font("freesansbold.ttf", 50)
        font_small = pygame.font.Font("freesansbold.ttf", 30)
        restart_font = pygame.font.Font(None, 36)

        text_game_over = font_large.render("GAME OVER", True, (255,255,255))
        text_score = font_small.render(f"Score: {score}", True, (214, 238, 238))
        text_high_score = font_small.render(f"High Score: {high_score}", True, (0,100,0))
        restart_text = restart_font.render("Press R to Restart", True, WHITE)

        # Center the text
        game_over_rect = text_game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        score_rect = text_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        high_score_rect = text_high_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        restart_rect = restart_text.get_rect(bottomright=(SCREEN_WIDTH -30 , SCREEN_HEIGHT - 40))
        screen.blit(text_game_over, game_over_rect)
        screen.blit(text_score, score_rect)
        screen.blit(text_high_score, high_score_rect)
        screen.blit(restart_text, restart_rect)

        pygame.display.flip()
        clock.tick(60)

        # Allow the player to exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                pygame.time.delay(1000)
                restart = True
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
    if restart:
        main()

# Main game loop
def main():
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH)]
    score = 0
    running = True
    distance = 0

    while running:
        screen.blit(background, (0, 0))  # Draw background

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over(score)
                pygame.quit()
                sys.exit()

        # Get stable distance reading
        try:
            distance = get_stable_distance(ser)
            print(f"Stable Distance: {distance} cm")  # Debugging line
        except Exception as e:
            print(f"Error reading distance: {e}")
            distance = 0
        
        font = pygame.font.Font("freesansbold.ttf", 24)
        distance_text = font.render(f"Distance: {distance} cm", True, BLUE)
        screen.blit(distance_text, (10, 40))


        # Flap bird when close to sensor
        last_flap_time = 0
        flap_delay = 0.3  # 300 ms

        if distance < 16 and time.time() - last_flap_time > flap_delay:
            bird.flap()
            last_flap_time = time.time()

        # Move and draw the bird
        bird.move()
        bird.draw()

        # Move and draw the pipes
        for pipe in pipes:
            pipe.move()
            pipe.draw()
            if pipe.collision(bird):
                running = False

        # Add new pipes
        if pipes[-1].x < SCREEN_WIDTH // 2:
            pipes.append(Pipe(SCREEN_WIDTH))

        # Remove off-screen pipes
        pipes = [pipe for pipe in pipes if not pipe.off_screen()]

        # Check for bird collision with top or bottom
        if bird.y - bird.radius < 0 or bird.y + bird.radius > SCREEN_HEIGHT:
            running = False

        # Update score
        for pipe in pipes:
            if pipe.x + pipe.width < bird.x and not pipe.scored:
                score += 1
                pipe.scored = True
                pygame.display.set_caption(f"Flappy Bird - Score: {score}")

        # Draw the score
        font = pygame.font.Font("freesansbold.ttf", 24)
        score_text = font.render(f"Score: {score}", True, RED)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    # Game over handling
    game_over(score)

# Run the game
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        ser.close()
        sys.exit(1)


