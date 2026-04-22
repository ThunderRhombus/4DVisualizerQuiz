import pygame
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Changing Circle")
clock = pygame.time.Clock()

# Circle properties
center = (WIDTH // 2, HEIGHT // 2)
orbit_radius1 = 150
orbit_radius2 = 100
circle_radius = 30
angle1 = 0.0
angle2 = 180.0


def get_gradient_color(hue):
    """Convert hue (0-360) to RGB color"""
    hue = hue % 360
    c = 255
    x = c * (1 - abs((hue / 60) % 2 - 1))

    if hue < 60:
        return (int(c), int(x), 0)
    elif hue < 120:
        return (int(x), int(c), 0)
    elif hue < 180:
        return (0, int(c), int(x))
    elif hue < 240:
        return (0, int(x), int(c))
    elif hue < 300:
        return (int(x), 0, int(c))
    else:
        return (int(c), 0, int(x))


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial, label=""):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.min = min_val
        self.max = max_val
        self.value = float(initial)
        self.label = label
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._set_value_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_value_from_pos(event.pos[0])

    def _set_value_from_pos(self, mx):
        t = (mx - self.x) / float(self.w)
        t = max(0.0, min(1.0, t))
        self.value = self.min + t * (self.max - self.min)

    def draw(self, surf, font):
        # bar
        pygame.draw.rect(surf, (80, 80, 80), self.rect)
        # handle
        t = (self.value - self.min) / float(self.max - self.min)
        handle_x = int(self.x + t * self.w)
        handle_y = self.y + self.h // 2
        pygame.draw.circle(surf, (200, 200, 200), (handle_x, handle_y), 10)
        # label and value
        label_surf = font.render(f"{self.label}: {self.value:.2f}", True, (220, 220, 220))
        surf.blit(label_surf, (self.x, self.y - 22))


# Default slider-controlled settings
gradient_timing_default = 1.0
rotation_speed_default = 2.0

# Prepare UI
font = pygame.font.SysFont(None, 24)
# Sliders for circle 1 (bottom row)
gradient_slider1 = Slider(50, HEIGHT - 80, 300, 16, 0.1, 5.0, gradient_timing_default, "Gradient Timing 1")
rotation_slider1 = Slider(450, HEIGHT - 80, 300, 16, 0.0, 10.0, rotation_speed_default, "Rotation Speed 1")
# Sliders for circle 2 (top row)
gradient_slider2 = Slider(50, HEIGHT - 140, 300, 16, 0.1, 5.0, gradient_timing_default, "Gradient Timing 2")
rotation_slider2 = Slider(450, HEIGHT - 140, 300, 16, 0.0, 10.0, rotation_speed_default, "Rotation Speed 2")

# Alpha for semi-transparent circles (0.5)
ALPHA = int(0.5 * 255)

def draw_circle_alpha(surf, color_rgb, alpha, pos, radius):
    size = radius * 2
    circle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    r, g, b = color_rgb
    pygame.draw.circle(circle_surf, (r, g, b, alpha), (radius, radius), radius)
    surf.blit(circle_surf, (int(pos[0] - radius), int(pos[1] - radius)))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # pass events to sliders
        gradient_slider1.handle_event(event)
        rotation_slider1.handle_event(event)
        gradient_slider2.handle_event(event)
        rotation_slider2.handle_event(event)

    # Clear screen
    screen.fill((20, 20, 20))

    # Use slider values for both circles
    gradient_timing1 = gradient_slider1.value
    rotation_speed1 = rotation_slider1.value
    gradient_timing2 = gradient_slider2.value
    rotation_speed2 = rotation_slider2.value

    # Calculate positions
    x1 = center[0] + orbit_radius1 * math.cos(math.radians(angle1))
    y1 = center[1] + orbit_radius1 * math.sin(math.radians(angle1))
    x2 = center[0] + orbit_radius2 * math.cos(math.radians(angle2))
    y2 = center[1] + orbit_radius2 * math.sin(math.radians(angle2))

    # Get colors based on angles scaled by respective gradient timings
    color1 = get_gradient_color(angle1 * gradient_timing1)
    color2 = get_gradient_color(angle2 * gradient_timing2)

    # Draw center point
    pygame.draw.circle(screen, (100, 100, 100), center, 5)

    # Draw moving circles with alpha
    draw_circle_alpha(screen, color1, ALPHA, (x1, y1), circle_radius)
    draw_circle_alpha(screen, color2, ALPHA, (x2, y2), circle_radius)

    # Draw sliders
    gradient_slider1.draw(screen, font)
    rotation_slider1.draw(screen, font)
    gradient_slider2.draw(screen, font)
    rotation_slider2.draw(screen, font)

    # Update angles
    angle1 += rotation_speed1
    angle2 += rotation_speed2

    pygame.display.flip()
    clock.tick(60)

pygame.quit()