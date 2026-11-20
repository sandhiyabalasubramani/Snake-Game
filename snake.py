#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PySnake - Classic Arcade Snake Game
An enhanced, modern Snake game built with Pygame.

Features:
- Clean and modern retro-arcade UI with subtle grid lines
- Responsive controls with Arrow Keys and WASD
- Intelligent fruit spawning preventing snake body overlap
- Top HUD bar displaying Score, High Score, and Speed
- Interactive Start Screen, Pause Menu, and Game Over Screen
- Dynamic difficulty scaling as score increases
- Cross-platform support (Windows, macOS, Linux)
"""

import sys
import os
import random
import pygame
from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_w,
    K_s,
    K_a,
    K_d,
    K_p,
    K_r,
    K_q,
    K_SPACE,
    K_RETURN,
    K_ESCAPE,
    Rect,
)

# ==============================================================================
# Game Configuration & Constants
# ==============================================================================
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
BLOCK_SIZE = 20
HEADER_HEIGHT = 40  # Top status bar height

GRID_COLS = WINDOW_WIDTH // BLOCK_SIZE  # 32 columns: 0, 20, ..., 620
GRID_ROWS = WINDOW_HEIGHT // BLOCK_SIZE  # 24 rows: 0, 20, ..., 460
HEADER_ROWS = HEADER_HEIGHT // BLOCK_SIZE  # 2 rows for header: y = 0, 20

BASE_SPEED = 10
SPEED_INCREMENT = 1.0  # +1 FPS every 30 points
MAX_SPEED = 24

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")

# ==============================================================================
# Color Palette (Modern Dark Theme)
# ==============================================================================
COLOR_BG = (18, 22, 31)             # Deep dark background
COLOR_GRID = (25, 30, 44)           # Subtle grid lines
COLOR_HEADER_BG = (13, 17, 23)      # Dark header bar
COLOR_HEADER_BORDER = (45, 55, 72)  # Header divider
COLOR_TEXT_PRIMARY = (240, 246, 252)# Crisp white
COLOR_TEXT_MUTED = (139, 148, 158)  # Soft gray
COLOR_TEXT_GOLD = (241, 224, 90)    # Trophy yellow
COLOR_TEXT_RED = (248, 81, 73)      # Alert red

# Snake colors
COLOR_SNAKE_HEAD = (57, 211, 83)    # Bright vibrant green
COLOR_SNAKE_BODY = (46, 160, 67)    # Emerald green
COLOR_SNAKE_OUTLINE = (35, 134, 54) # Segment border
COLOR_SNAKE_EYE = (255, 255, 255)   # Eyes white
COLOR_SNAKE_PUPIL = (15, 23, 42)    # Pupil dark navy

# Fruit colors
COLOR_FRUIT = (255, 75, 75)         # Vibrant apple red
COLOR_FRUIT_SHINE = (255, 140, 140) # Apple highlight
COLOR_FRUIT_LEAF = (74, 222, 128)   # Apple leaf green
COLOR_FRUIT_STEM = (139, 69, 19)    # Apple stem brown

# Game States
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAMEOVER = "gameover"

OPPOSITE_DIRECTIONS = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}


# ==============================================================================
# Helper Functions
# ==============================================================================
def get_font(size, bold=False):
    """
    Safely get a system font cross-platform (Windows, macOS, Linux).
    Falls back to Pygame's default font if system fonts are unavailable.
    """
    for font_name in ["Segoe UI", "Arial", "Consolas", "Helvetica", "DejaVu Sans"]:
        try:
            font = pygame.font.SysFont(font_name, size, bold=bold)
            if font:
                return font
        except Exception:
            continue
    return pygame.font.Font(None, size)


def load_high_score():
    """Load high score from disk safely."""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                val = f.read().strip()
                return int(val) if val.isdigit() else 0
        except (IOError, ValueError):
            return 0
    return 0


def save_high_score(score):
    """Save high score to disk safely."""
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(int(score)))
    except IOError:
        pass


def spawn_fruit(snake_segments):
    """
    Spawn fruit at a random grid coordinate that is NOT occupied by the snake.
    Ensures fruit never appears inside the snake's body.
    """
    all_positions = [
        [col * BLOCK_SIZE, row * BLOCK_SIZE]
        for col in range(GRID_COLS)
        for row in range(HEADER_ROWS, GRID_ROWS)
    ]
    occupied = {tuple(pos) for pos in snake_segments}
    available = [pos for pos in all_positions if tuple(pos) not in occupied]

    if not available:
        return [300, 300]
    return list(random.choice(available))


def calculate_speed(score):
    """Calculate dynamic game speed (FPS) based on current score."""
    speed = BASE_SPEED + (score // 30) * SPEED_INCREMENT
    return min(speed, MAX_SPEED)


# ==============================================================================
# Drawing Functions
# ==============================================================================
def draw_grid(surface):
    """Draw a clean, subtle grid background in the playable area."""
    surface.fill(COLOR_BG)

    # Vertical lines
    for x in range(0, WINDOW_WIDTH + 1, BLOCK_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, HEADER_HEIGHT), (x, WINDOW_HEIGHT), 1)

    # Horizontal lines
    for y in range(HEADER_HEIGHT, WINDOW_HEIGHT + 1, BLOCK_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (WINDOW_WIDTH, y), 1)


def draw_hud(surface, score, high_score, speed, font_small):
    """Draw the professional top HUD status bar."""
    # Background rectangle
    pygame.draw.rect(surface, COLOR_HEADER_BG, Rect(0, 0, WINDOW_WIDTH, HEADER_HEIGHT))
    # Bottom divider line
    pygame.draw.line(
        surface, COLOR_HEADER_BORDER, (0, HEADER_HEIGHT - 1), (WINDOW_WIDTH, HEADER_HEIGHT - 1), 2
    )

    # Score
    score_surf = font_small.render(f"SCORE: {score}", True, COLOR_TEXT_PRIMARY)
    surface.blit(score_surf, (15, 10))

    # High Score
    high_surf = font_small.render(f"HIGH SCORE: {high_score}", True, COLOR_TEXT_GOLD)
    high_rect = high_surf.get_rect(center=(WINDOW_WIDTH // 2, HEADER_HEIGHT // 2))
    surface.blit(high_surf, high_rect)

    # Speed
    speed_surf = font_small.render(f"SPEED: {speed:.1f} FPS", True, COLOR_TEXT_MUTED)
    speed_rect = speed_surf.get_rect(right=WINDOW_WIDTH - 15, centery=HEADER_HEIGHT // 2)
    surface.blit(speed_surf, speed_rect)


def draw_fruit(surface, fruit_pos):
    """Draw an attractive apple with stem, leaf, and light reflection."""
    x, y = fruit_pos

    # Main fruit body
    fruit_rect = Rect(x + 2, y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4)
    pygame.draw.rect(surface, COLOR_FRUIT, fruit_rect, border_radius=6)

    # Fruit highlight / shine
    pygame.draw.circle(surface, COLOR_FRUIT_SHINE, (x + 6, y + 6), 2)

    # Stem
    pygame.draw.line(surface, COLOR_FRUIT_STEM, (x + 10, y + 4), (x + 10, y + 1), 2)

    # Leaf
    pygame.draw.circle(surface, COLOR_FRUIT_LEAF, (x + 12, y + 2), 2)


def draw_snake(surface, snake_segments, direction):
    """Draw the snake with styled body segments and an expressive head."""
    for i, segment in enumerate(snake_segments):
        x, y = segment
        seg_rect = Rect(x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2)

        if i == 0:
            # Snake Head
            pygame.draw.rect(surface, COLOR_SNAKE_HEAD, seg_rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_SNAKE_OUTLINE, seg_rect, width=1, border_radius=6)

            # Eyes looking in movement direction
            eye_radius = 2
            pupil_radius = 1

            if direction == "right":
                eye1 = (x + 14, y + 6)
                eye2 = (x + 14, y + 14)
                p1 = (x + 15, y + 6)
                p2 = (x + 15, y + 14)
            elif direction == "left":
                eye1 = (x + 6, y + 6)
                eye2 = (x + 6, y + 14)
                p1 = (x + 5, y + 6)
                p2 = (x + 5, y + 14)
            elif direction == "up":
                eye1 = (x + 6, y + 6)
                eye2 = (x + 14, y + 6)
                p1 = (x + 6, y + 5)
                p2 = (x + 14, y + 5)
            else:  # down
                eye1 = (x + 6, y + 14)
                eye2 = (x + 14, y + 14)
                p1 = (x + 6, y + 15)
                p2 = (x + 14, y + 15)

            # Draw eyes
            for ep in (eye1, eye2):
                pygame.draw.circle(surface, COLOR_SNAKE_EYE, ep, eye_radius)
            for pp in (p1, p2):
                pygame.draw.circle(surface, COLOR_SNAKE_PUPIL, pp, pupil_radius)
        else:
            # Snake Body
            pygame.draw.rect(surface, COLOR_SNAKE_BODY, seg_rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_SNAKE_OUTLINE, seg_rect, width=1, border_radius=4)


def draw_modal_box(surface, width, height):
    """Draw a semi-transparent modal card for screens/menus."""
    modal = pygame.Surface((width, height), pygame.SRCALPHA)
    modal.fill((13, 17, 23, 235))
    rect = modal.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
    surface.blit(modal, rect)
    pygame.draw.rect(surface, COLOR_HEADER_BORDER, rect, width=2, border_radius=10)
    return rect


def draw_start_screen(surface, high_score, font_title, font_medium, font_small):
    """Render the clean and stylish Start Screen."""
    draw_grid(surface)
    draw_modal_box(surface, 460, 320)

    # Title
    title_surf = font_title.render("SNAKE GAME", True, COLOR_SNAKE_HEAD)
    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 130))
    surface.blit(title_surf, title_rect)

    # Subtitle
    sub_surf = font_small.render("Classic Arcade Edition", True, COLOR_TEXT_MUTED)
    sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, 168))
    surface.blit(sub_surf, sub_rect)

    # High score banner
    hs_surf = font_medium.render(f"High Score: {high_score}", True, COLOR_TEXT_GOLD)
    hs_rect = hs_surf.get_rect(center=(WINDOW_WIDTH // 2, 210))
    surface.blit(hs_surf, hs_rect)

    # Controls guide
    ctrl_lines = [
        "Controls: Arrow Keys or W / A / S / D",
        "Pause: [P] or [SPACE]   |   Quit: [ESC]",
    ]
    y_ctrl = 250
    for line in ctrl_lines:
        line_surf = font_small.render(line, True, COLOR_TEXT_MUTED)
        line_rect = line_surf.get_rect(center=(WINDOW_WIDTH // 2, y_ctrl))
        surface.blit(line_surf, line_rect)
        y_ctrl += 22

    # Start prompt
    prompt_surf = font_medium.render("Press [SPACE] or [ENTER] to Play", True, COLOR_TEXT_PRIMARY)
    prompt_rect = prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, 330))
    surface.blit(prompt_surf, prompt_rect)


def draw_pause_screen(surface, font_title, font_small):
    """Render the Pause overlay."""
    draw_modal_box(surface, 360, 180)

    title_surf = font_title.render("PAUSED", True, COLOR_TEXT_GOLD)
    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
    surface.blit(title_surf, title_rect)

    info_surf = font_small.render("Press [P] or [SPACE] to Resume", True, COLOR_TEXT_PRIMARY)
    info_rect = info_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
    surface.blit(info_surf, info_rect)


def draw_game_over_screen(surface, score, high_score, is_new_high, font_title, font_medium, font_small):
    """Render the Game Over screen with score breakdown and restart options."""
    draw_modal_box(surface, 460, 320)

    # Game Over Title
    go_surf = font_title.render("GAME OVER", True, COLOR_TEXT_RED)
    go_rect = go_surf.get_rect(center=(WINDOW_WIDTH // 2, 130))
    surface.blit(go_surf, go_rect)

    # New High Score tag or standard score
    if is_new_high and score > 0:
        new_tag = font_small.render("*** NEW HIGH SCORE! ***", True, COLOR_TEXT_GOLD)
        tag_rect = new_tag.get_rect(center=(WINDOW_WIDTH // 2, 172))
        surface.blit(new_tag, tag_rect)

    # Score breakdown
    score_surf = font_medium.render(f"Final Score: {score}", True, COLOR_TEXT_PRIMARY)
    score_rect = score_surf.get_rect(center=(WINDOW_WIDTH // 2, 210))
    surface.blit(score_surf, score_rect)

    best_surf = font_small.render(f"Best Score: {high_score}", True, COLOR_TEXT_GOLD)
    best_rect = best_surf.get_rect(center=(WINDOW_WIDTH // 2, 245))
    surface.blit(best_surf, best_rect)

    # Options
    r_surf = font_medium.render("Press [R] or [SPACE] to Restart", True, COLOR_SNAKE_HEAD)
    r_rect = r_surf.get_rect(center=(WINDOW_WIDTH // 2, 295))
    surface.blit(r_surf, r_rect)

    q_surf = font_small.render("Press [Q] or [ESC] to Quit", True, COLOR_TEXT_MUTED)
    q_rect = q_surf.get_rect(center=(WINDOW_WIDTH // 2, 335))
    surface.blit(q_surf, q_rect)


# ==============================================================================
# Game Controller Class
# ==============================================================================
class SnakeGame:
    def __init__(self, surface=None):
        self.surface = surface or pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("PySnake - Classic Arcade Game")

        # Fonts
        self.font_title = get_font(42, bold=True)
        self.font_medium = get_font(22, bold=True)
        self.font_small = get_font(16, bold=False)

        # High score
        self.high_score = load_high_score()
        self.is_new_high = False

        # State & Clock
        self.state = STATE_START
        self.clock = pygame.time.Clock()

        # Core Game Variables
        self.snake_position = [100, 100]
        self.snake_segments = [[100, 100], [80, 100], [60, 100]]
        self.fruit_position = [300, 300]
        self.fruit_spawned = True
        self.direction = "right"
        self.change_direction = "right"
        self.player_score = 0
        self.current_speed = BASE_SPEED

    def reset(self):
        """Reset the game state for a new round."""
        self.snake_position = [100, 100]
        self.snake_segments = [[100, 100], [80, 100], [60, 100]]
        self.fruit_position = spawn_fruit(self.snake_segments)
        self.fruit_spawned = True
        self.direction = "right"
        self.change_direction = "right"
        self.player_score = 0
        self.current_speed = BASE_SPEED
        self.is_new_high = False
        self.high_score = load_high_score()
        self.state = STATE_PLAYING

    def handle_input(self):
        """Process keyboard events according to current game state."""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                # --- START SCREEN INPUTS ---
                if self.state == STATE_START:
                    if event.key in (K_SPACE, K_RETURN):
                        self.reset()
                    elif event.key in (K_ESCAPE, K_q):
                        pygame.quit()
                        sys.exit()

                # --- PLAYING STATE INPUTS ---
                elif self.state == STATE_PLAYING:
                    # Arrow keys & WASD bindings
                    if event.key in (K_RIGHT, K_d):
                        if self.direction != "left":
                            self.change_direction = "right"
                    elif event.key in (K_LEFT, K_a):
                        if self.direction != "right":
                            self.change_direction = "left"
                    elif event.key in (K_UP, K_w):
                        if self.direction != "down":
                            self.change_direction = "up"
                    elif event.key in (K_DOWN, K_s):
                        if self.direction != "up":
                            self.change_direction = "down"
                    elif event.key in (K_p, K_SPACE):
                        self.state = STATE_PAUSED
                    elif event.key == K_ESCAPE:
                        self.state = STATE_PAUSED

                # --- PAUSED STATE INPUTS ---
                elif self.state == STATE_PAUSED:
                    if event.key in (K_p, K_SPACE):
                        self.state = STATE_PLAYING
                    elif event.key in (K_q, K_ESCAPE):
                        pygame.quit()
                        sys.exit()

                # --- GAMEOVER STATE INPUTS ---
                elif self.state == STATE_GAMEOVER:
                    if event.key in (K_r, K_SPACE, K_RETURN):
                        self.reset()
                    elif event.key in (K_q, K_ESCAPE):
                        pygame.quit()
                        sys.exit()

    def update(self):
        """Update game physics, snake movement, collisions, and score."""
        if self.state != STATE_PLAYING:
            return

        # Direction confirmation
        if self.change_direction != OPPOSITE_DIRECTIONS.get(self.direction):
            self.direction = self.change_direction

        # Move snake head
        if self.direction == "right":
            self.snake_position[0] += BLOCK_SIZE
        elif self.direction == "left":
            self.snake_position[0] -= BLOCK_SIZE
        elif self.direction == "up":
            self.snake_position[1] -= BLOCK_SIZE
        elif self.direction == "down":
            self.snake_position[1] += BLOCK_SIZE

        # Insert new head position
        self.snake_segments.insert(0, list(self.snake_position))

        # Fruit eating logic
        if self.snake_position == self.fruit_position:
            self.player_score += 10
            self.current_speed = calculate_speed(self.player_score)

            if self.player_score > self.high_score:
                self.high_score = self.player_score
                self.is_new_high = True
                save_high_score(self.high_score)

            # Spawn fruit guaranteed outside snake body
            self.fruit_position = spawn_fruit(self.snake_segments)
        else:
            self.snake_segments.pop()

        # Wall Collision Check (respecting top header)
        if (
            self.snake_position[0] < 0
            or self.snake_position[0] >= WINDOW_WIDTH
            or self.snake_position[1] < HEADER_HEIGHT
            or self.snake_position[1] >= WINDOW_HEIGHT
        ):
            self.state = STATE_GAMEOVER
            return

        # Self Collision Check
        for body_segment in self.snake_segments[1:]:
            if self.snake_position == body_segment:
                self.state = STATE_GAMEOVER
                return

    def render(self):
        """Render the complete scene to the display surface."""
        if self.state == STATE_START:
            draw_start_screen(
                self.surface,
                self.high_score,
                self.font_title,
                self.font_medium,
                self.font_small,
            )

        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER):
            draw_grid(self.surface)
            draw_fruit(self.surface, self.fruit_position)
            draw_snake(self.surface, self.snake_segments, self.direction)
            draw_hud(
                self.surface,
                self.player_score,
                self.high_score,
                self.current_speed,
                self.font_small,
            )

            if self.state == STATE_PAUSED:
                draw_pause_screen(self.surface, self.font_title, self.font_small)
            elif self.state == STATE_GAMEOVER:
                draw_game_over_screen(
                    self.surface,
                    self.player_score,
                    self.high_score,
                    self.is_new_high,
                    self.font_title,
                    self.font_medium,
                    self.font_small,
                )

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while True:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(self.current_speed if self.state == STATE_PLAYING else 30)


# ==============================================================================
# Screenshot Generation Utility (for CI / Documentation)
# ==============================================================================
def capture_screenshot(output_path="screenshots/game_screenshot.png"):
    """
    Simulate a realistic game scene and save high-resolution screenshot.
    Can run in headless environments as well.
    """
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    game = SnakeGame(surface)

    # Set up a vibrant mid-game demonstration state
    game.state = STATE_PLAYING
    game.player_score = 90
    game.high_score = 150
    game.current_speed = calculate_speed(90)
    game.direction = "right"
    game.change_direction = "right"

    # Snake in an active path
    game.snake_segments = [
        [320, 200],  # Head
        [300, 200],
        [280, 200],
        [260, 200],
        [240, 200],
        [240, 220],
        [240, 240],
        [260, 240],
        [280, 240],
    ]
    game.snake_position = list(game.snake_segments[0])
    game.fruit_position = [420, 200]

    game.render()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pygame.image.save(surface, output_path)
    pygame.quit()
    print(f"Screenshot successfully saved to {output_path}")


# ==============================================================================
# Entry Point
# ==============================================================================
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--screenshot":
        capture_screenshot()
        sys.exit(0)

    pygame.init()
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()
