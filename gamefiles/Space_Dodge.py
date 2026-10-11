import pygame
import time
import random
from pathlib import Path
pygame.font.init()

WIDTH, HEIGHT = 1280, 720
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Made by LWD200... Space Dodge!")
icon = pygame.image.load("Image.jpg").convert_alpha()
pygame.display.set_icon(icon)

BG = pygame.transform.scale(pygame.image.load("SpaceBG.png"), (WIDTH, HEIGHT))

PLAYER_WIDTH = 25
PLAYER_HEIGHT = 25

PLAYER_VEL = 5
STAR_VEL = 15

STAR_WIDTH = 20
STAR_HEIGHT = 20

PLAYER_IMAGE = pygame.transform.scale(
    pygame.image.load("cube_1.png").convert_alpha(),
    (PLAYER_WIDTH, PLAYER_HEIGHT)
)

FONT = pygame.font.SysFont("Arial", 30)

HIGH_SCORE_FILE = Path(__file__).with_name("highscore.txt")

def load_high_score():
    try:
        return float(HIGH_SCORE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0.0

def save_high_score(high_score):
    HIGH_SCORE_FILE.write_text(f"{high_score:.2f}", encoding="utf-8")

def draw(player, elapsed_time, stars, high_score):
    screen.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {elapsed_time:.2f}", 1, (255, 255, 255))
    screen.blit(time_text, (10, 10))
    high_score_text = FONT.render(f"Best: {high_score:.2f}", 1, (255, 255, 255))
    screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

    # pygame.draw.rect(screen, (0, 0, 255), player)
    screen.blit(PLAYER_IMAGE, player.topleft)

    for star, _, _ in stars:
        pygame.draw.circle(screen, (255, 255, 255), (star.x + star.width // 2, star.y + star.height // 2), star.width // 2)

    pygame.display.update()

def main():
    run = True
    high_score = load_high_score()

    player = pygame.Rect(
        (WIDTH - PLAYER_WIDTH) // 2,
        (HEIGHT - PLAYER_HEIGHT) // 2,
        PLAYER_WIDTH,
        PLAYER_HEIGHT,
    )

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    star_add_increment = 2000
    star_count = 0
    stars = []
    hit = False

    while run:
        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        if star_count > star_add_increment:
            for _ in range(10):
                edge = random.choice(("top", "bottom", "left", "right"))
                if edge == "top":
                    star = pygame.Rect(random.randint(0, WIDTH - STAR_WIDTH), -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                    velocity = (random.randint(-5, 5), STAR_VEL)
                elif edge == "bottom":
                    star = pygame.Rect(random.randint(0, WIDTH - STAR_WIDTH), HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                    velocity = (random.randint(-5, 5), -STAR_VEL)
                elif edge == "left":
                    star = pygame.Rect(-STAR_WIDTH, random.randint(0, HEIGHT - STAR_HEIGHT), STAR_WIDTH, STAR_HEIGHT)
                    velocity = (STAR_VEL, random.randint(-5, 5))
                else:
                    star = pygame.Rect(WIDTH, random.randint(0, HEIGHT - STAR_HEIGHT), STAR_WIDTH, STAR_HEIGHT)
                    velocity = (-STAR_VEL, random.randint(-5, 5))
                stars.append((star, *velocity))
            star_add_increment = max(200, star_add_increment - 50)
            star_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.y - PLAYER_VEL >= 0:
            player.y -= PLAYER_VEL
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.y + PLAYER_VEL + player.height <= HEIGHT:
            player.y += PLAYER_VEL

        for star_data in stars[:]:
            star, velocity_x, velocity_y = star_data
            star.x += velocity_x
            star.y += velocity_y
            if star.right < 0 or star.left > WIDTH or star.bottom < 0 or star.top > HEIGHT:
                stars.remove(star_data)
            else:
                closest_x = max(player.left, min(star.centerx, player.right))
                closest_y = max(player.top, min(star.centery, player.bottom))
                distance_x = star.centerx - closest_x
                distance_y = star.centery - closest_y
                if distance_x * distance_x + distance_y * distance_y <= (star.width // 2) ** 2:
                    hit = True
                    break

        if hit:
            if elapsed_time > high_score:
                high_score = elapsed_time
                save_high_score(high_score)
            draw(player, elapsed_time, stars, high_score)
            game_over_panel = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 85, 600, 170)
            pygame.draw.rect(screen, (20, 20, 20), game_over_panel, border_radius=12)
            lose_text = FONT.render("You were hit. You lose. Try again.", 1, (255, 0, 0))
            screen.blit(lose_text, lose_text.get_rect(center=(WIDTH // 2, game_over_panel.top + 48)))
            restart_button = pygame.Rect(WIDTH // 2 - 90, game_over_panel.top + 95, 180, 50)
            pygame.draw.rect(screen, (0, 0, 0), restart_button, border_radius=8)
            restart_text = FONT.render("Restart", True, (255, 255, 255))
            screen.blit(restart_text, restart_text.get_rect(center=restart_button.center))
            pygame.display.update()
            restart = False
            while run:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and restart_button.collidepoint(event.pos):
                        player.center = (WIDTH // 2, HEIGHT // 2)
                        start_time = time.time()
                        elapsed_time = 0
                        star_add_increment = 2000
                        star_count = 0
                        stars.clear()
                        hit = False
                        restart = True
                        break
                clock.tick(60)
                if restart:
                    break
            if restart:
                continue
            break

        draw(player, elapsed_time, stars, high_score)

    pygame.quit()

if __name__ == "__main__":
    main()