import pygame
import sys
import random
import math

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

class Paddle:
    def __init__(self, x, y):
        self.width = 100
        self.height = 15
        self.x = x - self.width // 2
        self.y = y
        self.speed = 8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
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
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                               self.radius * 2, self.radius * 2)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off walls
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.speed_x = -self.speed_x
        if self.y <= self.radius:
            self.speed_y = -self.speed_y
        
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius
    
    def bounce_paddle(self, paddle):
        if self.rect.colliderect(paddle.rect) and self.speed_y > 0:
            # Calculate bounce angle based on where ball hits paddle
            hit_pos = (self.x - paddle.x) / paddle.width
            angle = (hit_pos - 0.5) * math.pi / 3  # Max 60 degrees
            speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
            self.speed_x = speed * math.sin(angle)
            self.speed_y = -abs(speed * math.cos(angle))
    
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)

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
        
        self.create_bricks()
    
    def create_bricks(self):
        brick_rows = 8
        brick_cols = 10
        brick_width = 75
        brick_height = 25
        padding = 5
        
        start_x = (SCREEN_WIDTH - (brick_cols * (brick_width + padding) - padding)) // 2
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
            if self.lives > 0:
                self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            return self.lives <= 0
        
        # All bricks destroyed
        active_bricks = [brick for brick in self.bricks if not brick.destroyed]
        return len(active_bricks) == 0
    
    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
    
    def run(self):
        running = True
        game_over = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and game_over:
                        # Restart game
                        self.__init__()
                        game_over = False
            
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
                
                restart_text = self.font.render("Press SPACE to restart", True, WHITE)
                
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                
                self.screen.blit(game_over_text, text_rect)
                self.screen.blit(restart_text, restart_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
