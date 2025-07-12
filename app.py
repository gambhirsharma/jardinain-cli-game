import pygame
import sys
import random
import math
import numpy

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

# Brick colors for different rows
BRICK_COLORS = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.sounds = {}
            self.load_sounds()
        except pygame.error as e:
            print(f"Sound system not available: {e}")
            self.sounds = {}

    def load_sounds(self):
        # Create simple sound effects programmatically
        try:
            # Ball bounce sound (short beep)
            self.create_beep_sound("bounce", 440, 0.1)

            # Brick break sound (higher pitch)
            self.create_beep_sound("brick_break", 880, 0.15)

            # Ball lost sound (lower pitch, longer)
            self.create_beep_sound("ball_lost", 220, 0.5)

            # Game over sound (very low pitch)
            self.create_beep_sound("game_over", 110, 1.0)

            # Win sound (ascending notes)
            self.create_win_sound()

        except (pygame.error, ValueError) as e:
            print(f"Could not create sounds: {e}")

    def create_beep_sound(self, name, frequency, duration):
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = numpy.zeros((frames, 2), dtype=numpy.int16)  # 16-bit stereo
        
        for i in range(frames):
            wave = int(4096 * math.sin(2 * math.pi * frequency * i / sample_rate))
            # Add fade out to prevent clicking
            fade = 1.0 - (i / frames) * 0.5
            wave_value = int(wave * fade)
            arr[i][0] = wave_value  # Left channel
            arr[i][1] = wave_value  # Right channel

        try:
            sound = pygame.sndarray.make_sound(arr)
            self.sounds[name] = sound
        except (pygame.error, ValueError) as e:
            print(f"Could not create sound '{name}': {e}")

    def create_win_sound(self):
        sample_rate = 22050
        duration = 1.5
        frames = int(duration * sample_rate)
        arr = numpy.zeros((frames, 2), dtype=numpy.int16)  # 16-bit stereo

        # Create ascending melody
        notes = [523, 659, 784, 1047]  # C, E, G, C (octave higher)
        note_duration = frames // len(notes)

        for note_idx, frequency in enumerate(notes):
            start_frame = note_idx * note_duration
            end_frame = min(start_frame + note_duration, frames)
            
            for i in range(start_frame, end_frame):
                local_i = i - start_frame
                wave = int(2048 * math.sin(2 * math.pi * frequency * local_i / sample_rate))
                # Envelope for each note
                envelope = math.sin(math.pi * local_i / note_duration)
                wave_value = int(wave * envelope)
                arr[i][0] = wave_value  # Left channel
                arr[i][1] = wave_value  # Right channel

        try:
            sound = pygame.sndarray.make_sound(arr)
            self.sounds["win"] = sound
        except (pygame.error, ValueError) as e:
            print(f"Could not create win sound: {e}")

    def play(self, sound_name):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass  # Silently ignore if sound can't play


class Paddle:
    def __init__(self, x, y):
        self.width = 100
        self.height = 15
        self.x = x - self.width // 2
        self.y = y
        self.speed = 8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.mouse_control = True  # Toggle for mouse control

    def update(self):
        if self.mouse_control:
            # Mouse/trackpad control
            mouse_x = pygame.mouse.get_pos()[0]
            self.x = mouse_x - self.width // 2
            # Keep paddle within screen bounds
            self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        else:
            # Keyboard control
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.x > 0:
                self.x -= self.speed
            if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
                self.x += self.speed

        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)


class Ball:
    def __init__(self, x, y):
        self.radius = 8
        self.x = x
        self.y = y
        self.speed_x = random.choice([-4, 4])
        self.speed_y = -4
        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2,
        )
        self.sound_manager = None  # Will be set by Game class

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off walls
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.speed_x = -self.speed_x
            if self.sound_manager:
                self.sound_manager.play("bounce")
        if self.y <= self.radius:
            self.speed_y = -self.speed_y
            if self.sound_manager:
                self.sound_manager.play("bounce")

        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def bounce_paddle(self, paddle):
        if self.rect.colliderect(paddle.rect) and self.speed_y > 0:
            # Play bounce sound
            if self.sound_manager:
                self.sound_manager.play("bounce")

            # Calculate bounce angle based on where ball hits paddle
            hit_pos = (self.x - paddle.x) / paddle.width
            angle = (hit_pos - 0.5) * math.pi / 3  # Max 60 degrees
            speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
            self.speed_x = speed * math.sin(angle)
            self.speed_y = -abs(speed * math.cos(angle))

    def draw(self, screen):
        pygame.draw.circle(
            screen, WHITE, (int(self.x), int(self.y)), self.radius
        )
        pygame.draw.circle(
            screen, BLACK, (int(self.x), int(self.y)), self.radius, 2
        )


class Brick:
    def __init__(self, x, y, color):
        self.width = 75
        self.height = 25
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.destroyed = False

    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jardinains! - Retro Brick Breaker")
        self.clock = pygame.time.Clock()

        self.paddle = Paddle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.bricks = []
        self.score = 0
        self.lives = 3
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Sound manager
        self.sound_manager = SoundManager()

        self.create_bricks()

    def create_bricks(self):
        brick_rows = 8
        brick_cols = 10
        brick_width = 75
        brick_height = 25
        padding = 5

        start_x = (
            SCREEN_WIDTH - (brick_cols * (brick_width + padding) - padding)
        ) // 2
        start_y = 50

        for row in range(brick_rows):
            for col in range(brick_cols):
                x = start_x + col * (brick_width + padding)
                y = start_y + row * (brick_height + padding)
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                self.bricks.append(Brick(x, y, color))

    def handle_collisions(self):
        for brick in self.bricks:
            if not brick.destroyed and self.ball.rect.colliderect(brick.rect):
                brick.destroyed = True
                self.score += 10

                # Play brick break sound
                self.sound_manager.play("brick_break")

                # Simple bounce logic
                ball_center_x = self.ball.x
                ball_center_y = self.ball.y
                brick_center_x = brick.x + brick.width // 2
                brick_center_y = brick.y + brick.height // 2

                # Determine which side of brick was hit
                dx = ball_center_x - brick_center_x
                dy = ball_center_y - brick_center_y

                if abs(dx) > abs(dy):
                    self.ball.speed_x = -self.ball.speed_x
                else:
                    self.ball.speed_y = -self.ball.speed_y

                break

    def check_game_over(self):
        # Ball fell off screen
        if self.ball.y > SCREEN_HEIGHT:
            self.lives -= 1
            self.sound_manager.play("ball_lost")  # Play ball lost sound

            if self.lives > 0:
                self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                # Set sound manager reference for new ball
                self.ball.sound_manager = self.sound_manager
            else:
                self.sound_manager.play("game_over")  # Play game over sound
            return self.lives <= 0

        # All bricks destroyed
        active_bricks = [brick for brick in self.bricks if not brick.destroyed]
        if len(active_bricks) == 0:
            self.sound_manager.play("win")  # Play win sound
            return True

        return False

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))

        # Control instructions
        control_text = (
            "Mouse/Trackpad" if self.paddle.mouse_control else "Arrow Keys"
        )
        control_info = self.small_font.render(
            f"Controls: {control_text} | Press 'C' to toggle", True, WHITE
        )
        self.screen.blit(control_info, (10, SCREEN_HEIGHT - 30))

    def run(self):
        running = True
        game_over = False

        # Set sound manager reference for ball
        self.ball.sound_manager = self.sound_manager

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and game_over:
                        # Restart game
                        self.__init__()
                        game_over = False
                    elif event.key == pygame.K_c:
                        # Toggle control method
                        self.paddle.mouse_control = not self.paddle.mouse_control

            if not game_over:
                # Update game objects
                self.paddle.update()
                self.ball.update()
                self.ball.bounce_paddle(self.paddle)
                self.handle_collisions()

                # Check for game over conditions
                game_over = self.check_game_over()

            # Draw everything
            self.screen.fill(BLACK)

            # Draw game objects
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)

            for brick in self.bricks:
                brick.draw(self.screen)

            self.draw_ui()

            # Draw game over screen
            if game_over:
                if self.lives <= 0:
                    game_over_text = self.font.render("GAME OVER!", True, RED)
                else:
                    game_over_text = self.font.render("YOU WIN!", True, GREEN)

                restart_text = self.font.render(
                    "Press SPACE to restart", True, WHITE
                )

                text_rect = game_over_text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                )
                restart_rect = restart_text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
                )

                self.screen.blit(game_over_text, text_rect)
                self.screen.blit(restart_text, restart_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
