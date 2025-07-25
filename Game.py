import pygame
import random
import os
import sys

# Constants
WIDTH, HEIGHT = 800, 600

# Main menu function
def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Main Menu")

    background = pygame.image.load("image/MenuBackground.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    font = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
    small_font = pygame.font.SysFont("Comic Sans MS", 30)

    start_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 60)
    highscore_button = pygame.Rect(WIDTH // 2 - 120, 400, 240, 60)
    quit_top_button = pygame.Rect(20, 20, 100, 40)

    def draw_button(text, rect, color=(0, 120, 250)):
        pygame.draw.rect(screen, color, rect, border_radius=12)
        label = font.render(text, True, (255, 255, 255))
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)
        

    def show_high_scores():
        try:
            with open("highscores.txt", "r") as file:
                high_score = file.read()
        except:
            high_score = "No score yet."

        back_button = pygame.Rect(300, 500, 200, 50)
        while True:
            screen.fill((0, 0, 0))
            title = font.render("High Score", True, (255, 255, 0))
            score_text = small_font.render(high_score, True, (255, 255, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 250))
            pygame.draw.rect(screen, (150, 50, 50), back_button, border_radius=10)
            back_label = small_font.render("Back", True, (255, 255, 255))
            back_label_rect = back_label.get_rect(center=back_button.center)
            screen.blit(back_label, back_label_rect)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                    return

    while True:
        screen.blit(background, (0, 0))
        draw_button("Start", start_button)
        draw_button("High Score", highscore_button)
        pygame.draw.rect(screen, (200, 50, 50), quit_top_button, border_radius=8)
        quit_label = small_font.render("Quit", True, (255, 255, 255))
        quit_label_rect = quit_label.get_rect(center=quit_top_button.center)
        screen.blit(quit_label, quit_label_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "start"
                elif highscore_button.collidepoint(event.pos):
                    show_high_scores()
                elif quit_top_button.collidepoint(event.pos):
                    pygame.quit(); sys.exit()
        pygame.display.update()

# Game function
def show_intro():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Instructions")
    font = pygame.font.SysFont("Comic Sans MS", 30)
    screen.fill((0, 0, 0))
    instructions = [
        "Welcome to Space Rocket Game!",
        "Instructions:",
        "- Use mouse to move the rocket.",
        "- Avoid falling asteroids to survive.",
        "- Press 'P' to pause and 'Esc' to exit.",
        "- Survive as long as you can and get high score!"
    ]
    skip_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 100, 150, 50)
    running = True
    start_time = pygame.time.get_ticks()

    while running:
        screen.fill((0, 0, 0))
        for i, line in enumerate(instructions):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 40))
        pygame.draw.rect(screen, (50, 150, 50), skip_button, border_radius=12)
        skip_text = font.render("Skip Intro", True, (255, 255, 255))
        skip_text_rect = skip_text.get_rect(center=skip_button.center)
        screen.blit(skip_text, skip_text_rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and skip_button.collidepoint(event.pos):
                return

        if pygame.time.get_ticks() - start_time > 5000:
            running = False

def run_game():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Rocket Game")

    background_img = pygame.image.load("image/SpaceBackground.png")
    rocket_img = pygame.image.load("image/rocket.png").convert_alpha()
    asteroid_imgs_raw = [pygame.image.load(f"image/Asteroid{i}.png").convert_alpha() for i in range(1, 7)]
    crash_sound = pygame.mixer.Sound("sounds/crash.wav")
    blast_sound = pygame.mixer.Sound("sounds/blast.wav")

    rocket_img = pygame.transform.scale(rocket_img, (60, 80))
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

    rocket_x, rocket_y = WIDTH // 2, HEIGHT - 100
    rocket_speed, score, lives = 7, 0, 3
    asteroids, asteroid_speed = [], 3.0
    font = pygame.font.SysFont("Comic Sans MS", 30)
    big_font = pygame.font.SysFont("Comic Sans MS", 50)
    clock = pygame.time.Clock()
    trail_particles, explosions = [], []
    big_explosion, show_game_over_menu = None, False
    paused = False

    high_score = 0
    if os.path.exists("highscores.txt"):
        with open("highscores.txt", "r") as file:
            try:
                high_score = int(file.read())
            except:
                high_score = 0

    def draw_text(text, x, y, color=(255, 255, 255), big=False):
        f = big_font if big else font
        screen.blit(f.render(text, True, color), (x, y))

    def draw_button(text, rect, color=(100, 100, 255)):
        pygame.draw.rect(screen, color, rect, border_radius=12)
        label = font.render(text, True, (255, 255, 255))
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    def create_asteroid():
        img = random.choice(asteroid_imgs_raw)
        size = random.randint(40, 70)
        scaled = pygame.transform.scale(img, (size, size))
        spin_speed = random.uniform(1, 4)
        return [random.randint(0, WIDTH - size), -size, scaled, 0, spin_speed, scaled.copy(), size]

    menu_button = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 60, 100, 40)
    quit_button = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 + 60, 100, 40)

    running, game_over = True, False
    while running:
        clock.tick(60)
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_p:
                    paused = not paused
            if show_game_over_menu and event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button.collidepoint(event.pos):
                    pygame.quit(); sys.exit()
                elif menu_button.collidepoint(event.pos):
                    return "menu"

        if paused:
            draw_text("Game Paused", WIDTH // 2 - 130, HEIGHT // 2, (255, 255, 0), True)
            pygame.display.update()
            continue

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and rocket_x > 0:
                rocket_x -= rocket_speed
            if keys[pygame.K_RIGHT] and rocket_x < WIDTH - rocket_img.get_width():
                rocket_x += rocket_speed
            rocket_x = max(0, min(WIDTH - rocket_img.get_width(), pygame.mouse.get_pos()[0] - 30))

            trail_particles.append([rocket_x + 30, rocket_y + 75, 8])
            for p in trail_particles[:]:
                pygame.draw.circle(screen, (255, 100, 0), (p[0], p[1]), int(p[2]))
                p[2] -= 0.3; p[1] += 2
                if p[2] <= 0: trail_particles.remove(p)

            if random.randint(1, 30) == 1:
                asteroids.append(create_asteroid())

            for a in asteroids[:]:
                a[1] += asteroid_speed; a[3] += a[4]
                img = pygame.transform.rotate(a[5], a[3])
                rect = img.get_rect(center=(a[0] + a[6] // 2, a[1] + a[6] // 2))
                screen.blit(img, rect.topleft)

                rocket_rect = pygame.Rect(rocket_x + 10, rocket_y + 10, 40, 60)
                a_rect = pygame.Rect(rect.left + 5, rect.top + 5, rect.width - 10, rect.height - 10)
                if rocket_rect.colliderect(a_rect):
                    if lives > 1:
                        explosions.append([rocket_x + 30, rocket_y + 40, 10, 50])
                        crash_sound.play()
                    else:
                        blast_sound.play()
                        big_explosion = [rocket_x + 30, rocket_y + 40, 10, pygame.time.get_ticks()]
                        game_over = True
                    asteroids.remove(a); lives -= 1; break
                elif a[1] > HEIGHT:
                    asteroids.remove(a); score += 10
                    if score % 100 == 0: asteroid_speed += 0.5

            for e in explosions[:]:
                pygame.draw.circle(screen, (255, 150, 0), (e[0], e[1]), int(e[2]))
                e[2] += 3
                if e[2] > e[3]: explosions.remove(e)

            screen.blit(rocket_img, (rocket_x, rocket_y))
            draw_text(f"Score: {score}", 10, 10)
            draw_text(f"Lives: {lives}", 10, 40)
            draw_text(f"High Score: {high_score}", 10, 70)
        else:
            if big_explosion:
                x, y, r, t = big_explosion
                r += 1000 / 300
                pygame.draw.circle(screen, (255, 100, 0), (x, y), int(r))
                big_explosion[2] = r
                if r > 1000:
                    big_explosion = None
                    if score > high_score:
                        with open("highscores.txt", "w") as file:
                            file.write(str(score))
                    show_game_over_menu = True
            elif show_game_over_menu:
                draw_text("Game Over", WIDTH//2 - 100, HEIGHT//2 - 80, (255, 0, 0), True)
                draw_text(f"Final Score: {score}", WIDTH//2 - 100, HEIGHT//2 - 20)
                draw_text(f"High Score: {high_score}", WIDTH//2 - 100, HEIGHT//2 + 10)
                draw_button("Menu", menu_button)
                draw_button("Quit", quit_button)

        pygame.display.update()

# Main program loop
def main():
    while True:
        action = main_menu()
        if action == "start":
            show_intro()
            back = run_game()
            if back != "menu":
                break

if __name__ == "__main__":
    main()
