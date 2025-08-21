import pygame, dotenv
from wheel import Wheel

# Initialize pygame
pygame.init()

# Import environment variables
dotenv.load_dotenv()

# Initialize window
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Prize Wheel")

# Hide mouse cursor
pygame.mouse.set_visible(False)

# Initialize wheel object
wheel = Wheel()

while True:
    wheel.render(screen)
    wheel.events()
    wheel.update(screen)
