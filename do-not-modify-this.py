import pygame
import sys
import random


# Game settings
FPS = 60
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galactic Gatekeepers")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.laser = None
        self.enemy_hits = 0
        self.can_lose_life = True

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += 5
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= 5
        if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += 5

    def kill_enemy(self, enemies):
        if not self.can_lose_life:
            return False
       
        enemy_collision = pygame.sprite.spritecollide(self, enemies, True)
        if not enemy_collision:
            self.can_lose_life = True
            return False

        for enemy in enemy_collision:
            self.enemy_hits += 1
            if self.enemy_hits >= 5:
                return True

        self.can_lose_life = False
        return True

    def shoot_laser(self):
        if not self.laser:
            self.laser = Laser(self.rect.centerx, self.rect.top)
            all_sprites.add(self.laser)
            lasers.add(self.laser)

    def update_laser(self):
        if self.laser:
            self.laser.update()
            if self.laser.rect.bottom < 0:
                self.laser.kill()
                lasers.remove(self.laser)
                self.laser = None

    def check_laser_collision(self, enemies):
        if self.laser:
            enemy_collision = pygame.sprite.spritecollide(self.laser, enemies, True)
            if enemy_collision:
                self.laser.kill()
                lasers.remove(self.laser)
                self.laser = None
                return True
        return False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((24, 24))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y += 3
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()  # Remove enemy if it moves off the screen


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 16))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y -= 10  # Increase the speed of the laser


class Scoreboard:
    def __init__(self):
        self.score = 0

    def update(self, killed):
        if killed:
            self.score += 1

    def draw(self, screen):
        score_text = font.render("Score: " + str(self.score), True, WHITE)
        screen.blit(score_text, (10, 10))


class Lives:
    def __init__(self):
        self.lives = 3

    def lose_life(self):
        self.lives -= 1

    def draw(self, screen):
        lives_text = font.render("Lives: " + str(self.lives), True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))


# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
lasers = pygame.sprite.Group()

# Create player spaceship
player = SpaceShip(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
all_sprites.add(player)

spawn_time = pygame.time.get_ticks() + random.randint(600, 1200)  # Random initial spawn time

scoreboard = Scoreboard()
lives = Lives()

paused = False  # Flag to indicate if the game is paused
game_over = False  # Flag to indicate if the game is over

while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Press 'p' to pause/resume the game
                paused = not paused
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button (MOUSE1) for shooting laser
                player.shoot_laser()

    if not game_over:
        if not paused:
            # Spawn new enemies
            if pygame.time.get_ticks() - spawn_time > 800:  # Adjust the spawn rate as needed (40% faster)
                enemy_count = random.randint(1, 2)  # Lower amount of enemies that spawn at once
                for _ in range(enemy_count):
                    enemy = Enemy(random.randint(50, SCREEN_WIDTH - 50), 0)
                    enemies.add(enemy)
                    all_sprites.add(enemy)
                spawn_time = pygame.time.get_ticks() + random.randint(600, 1200)  # Random next spawn time

            # Update game objects
            all_sprites.update()

            # Player kills enemies with laser
            killed = player.check_laser_collision(enemies)
            scoreboard.update(killed)

            # Player kills enemies by colliding with them
            killed = player.kill_enemy(enemies)
            if killed:
                lives.lose_life()
                if lives.lives <= 0:
                    game_over = True
                else:
                    player.can_lose_life = True
            scoreboard.update(killed)

            # Update player's laser
            player.update_laser()

            # Check if enemies reach the bottom of the screen
            if len([enemy for enemy in enemies if enemy.rect.bottom >= SCREEN_HEIGHT]) >= 5:
                game_over = True

            # Drawing
            screen.fill(BLACK)
            all_sprites.draw(screen)
            scoreboard.draw(screen)
            lives.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
        else:
            # Drawing when the game is paused
            screen.fill(BLACK)
            all_sprites.draw(screen)
            scoreboard.draw(screen)
            lives.draw(screen)
            pause_text = font.render("Paused", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 18))
            pygame.display.flip()
            clock.tick(FPS)
    else:
        # Drawing when the game is over
        screen.fill(BLACK)
        game_over_text = font.render("Defeated!", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 18))
        pygame.display.flip()
        clock.tick(FPS)