import pygame, sys, os, math, random

# CONSTANTS 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (3, 7, 30),
    (55, 6, 23),
    (106, 4, 15),
    (157, 2, 8),
    (208, 0, 0),
    (220, 47, 2),
    (232, 93, 4),
    (244, 140, 6),
    (250, 163, 7),
    (255, 186, 8)
]

class Wheel:
    def __init__(self):
        self.title = os.getenv("TITLE")
        self.subtitle = os.getenv("SUBTITLE")
        self.common_prizes = os.getenv("COMMON_PRIZES").split(", ")
        self.rare_prizes = os.getenv("RARE_PRIZES").split(", ")
        self.prizes = self.common_prizes + self.rare_prizes

        self.triangle_angle = ((360 * math.pi / 180) / len(self.prizes))

        self.state = "idle"
        self.credits = 0
        self.spins = 0
        self.spinned_angle = 0
        self.initial_rotation = self.triangle_angle * 4.5
        self.rotation_angle = self.initial_rotation
        self.speed = 0
        self.max_speed = 0.05
        self.acceleration = 0.001
        self.radius = 350
        self.margin = 100
        self.prize_index = None

    def render(self, screen):
        # Update screen
        pygame.display.update()

        # Clear screen
        pygame.draw.rect(screen, BLACK, (0, 0, screen.get_width(), screen.get_height()))

        # Render title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render(self.title, True, WHITE)
        title = pygame.transform.rotate(title, 90)
        screen.blit(title, (self.margin, screen.get_height() // 2 - title.get_height() // 2))

        # Render subtitle
        subtitle = title_font.render(self.subtitle, True, WHITE)
        subtitle = pygame.transform.rotate(subtitle, 90)
        screen.blit(subtitle, (self.margin + title.get_width() + 32, screen.get_height() // 2 - subtitle.get_height() // 2))

        # Render credits
        medium_font = pygame.font.Font(None, 48)
        credits_text = medium_font.render("Créditos: " + str(self.credits), True, WHITE)
        credits_text = pygame.transform.rotate(credits_text, 90)
        screen.blit(credits_text, (screen.get_width() - self.margin - credits_text.get_width(), self.margin))


        # Render wheel
        small_font = pygame.font.Font(None, 24)
        center = (screen.get_width() // 2, screen.get_height() // 2)
        for i in range(len(self.prizes)):
            angle = (self.triangle_angle * i) + self.rotation_angle
            fill_color = COLORS[i % len(COLORS)]

            # Render triangles
            if i < len(self.prizes):
                next_angle = self.triangle_angle * (i + 1) + self.rotation_angle

                first_cathetus = (center[0] + math.cos(angle) * self.radius, center[1] + math.sin(angle) * self.radius)
                second_cathetus = (center[0] + math.cos(next_angle) * self.radius, center[1] + math.sin(next_angle) * self.radius)

                pygame.draw.polygon(screen, fill_color, [center, first_cathetus, second_cathetus])

            # Render prize names
            mid_angle = angle + (self.triangle_angle / 2)  # middle of the wedge
            prize = small_font.render(self.prizes[i], True, WHITE)

            # Convert radians -> degrees and rotate so it's upright in the wedge
            prize = pygame.transform.rotate(prize, -math.degrees(mid_angle) + 270)

            # Position text along radius, centered
            text_radius = self.radius * 0.9
            text_x = center[0] + math.cos(mid_angle) * text_radius - prize.get_width() / 2
            text_y = center[1] + math.sin(mid_angle) * text_radius - prize.get_height() / 2

            screen.blit(prize, (text_x, text_y))

        # Render pointer 
        pointer_points = [
            (center[0] - self.radius - 30, center[1] + 25),
            (center[0] - self.radius - 30, center[1] - 25),
            (center[0] - self.radius + 30, center[1])
        ]
        pygame.draw.polygon(screen, WHITE, pointer_points)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_c:
                    self.credits += 1
                elif event.key == pygame.K_p:
                    if self.credits > 0:
                        if self.state == "idle":
                            self.state = "playing"
                            self.credits -= 1
                            self.spins += 1

                            # Every 100 spins, win a rare prize
                            if self.spins != 0 and self.spins % 100 == 0:
                                # Select a random index from rare prizes array and add the length of common prices
                                self.prize_index = len(self.common_prizes) - 1 + random.randrange(0, len(self.rare_prizes) - 1)
                            else:
                                # Select a random index from common prizes array
                                self.prize_index = random.randrange(0, len(self.common_prizes) - 1)
                    else:
                        if self.state == "idle":
                            self.state = "no_credits"


    def update(self):
        # Rotate wheel
        self.rotation_angle += self.speed

        if self.state == "playing":
            if self.speed < self.max_speed:
                self.speed += self.acceleration
            else:
                self.state = "stopping"

        if self.state == "stopping":
            spin = (10 * self.triangle_angle)
            if self.rotation_angle >= self.initial_rotation + spin * 3 - (self.triangle_angle * self.prize_index):
                self.speed = 0
                half_triangle_angle = self.triangle_angle / 2
                self.rotation_angle = half_triangle_angle * round(self.rotation_angle / half_triangle_angle)
                self.state = "idle"

        if self.state == "no_credits":
            pass
