import random, pygame, math

class Confetti:
    def __init__(self, x, y, position):
        self.x = x
        self.y = y
        self.w = 10
        self.h = 20
        self.position = position
        self.angle = random.randrange(0, 180) * (math.pi / 180)
        self.xvel = random.randrange(0, 15, 2)
        self.yvel = None

        if self.position == "right":
            self.yvel = random.randrange(0, 10, 2)
            self.angular_speed = -0.25
        else:
            self.yvel = random.randrange(-10, 0, 2)
            self.angular_speed = 0.25

        self.gravity = 0.04
        self.colors = [
            (212, 67, 67),
            (255, 180, 0),
            (144, 104, 212),
            (75, 177, 223),
            (158, 212, 80),
        ]
        self.color = random.choice(self.colors)

    def render(self, screen):
        rect_surf = pygame.Surface((10, 20), pygame.SRCALPHA)
        rect_surf.fill(self.color)

        rotated_surf = pygame.transform.rotate(rect_surf, self.angle)
        rotated_rect = rotated_surf.get_rect(center=(self.x, self.y))

        screen.blit(rotated_surf, rotated_rect.topleft)

    def update(self):
        # Confetti physics
        self.x += self.xvel
        self.y += self.yvel

        # Rotate confetti
        self.angle += self.angular_speed

        # Add air friction
        if self.yvel > 0:
            self.yvel -= self.gravity / 2
        elif self.yvel < 0:
            self.yvel += self.gravity / 2

        # Add gravity
        self.xvel += self.gravity
