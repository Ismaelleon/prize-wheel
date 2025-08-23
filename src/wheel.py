import pygame, sys, os, math, random, time
from confetti import Confetti

# CONSTANTS 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DEBUG_COLOR = (0, 255, 0)
COLORS = [
    (175, 29, 31),
    (94, 0, 10),
]

class Wheel:
    def __init__(self):
        self.title = os.getenv("TITLE")
        self.subtitle = os.getenv("SUBTITLE")
        self.common_prizes = os.getenv("COMMON_PRIZES").split(", ")
        self.special_prizes = os.getenv("SPECIAL_PRIZES").split(", ")
        self.rare_prizes = os.getenv("RARE_PRIZES").split(", ")
        self.prizes = self.common_prizes + self.special_prizes + self.rare_prizes

        # Intervals of spins for special and rare prizes
        self.special_interval = 25
        self.rare_interval = 500

        self.triangle_angle = ((360 * math.pi / 180) / len(self.prizes))

        self.debug = False
        self.state = "idle"
        self.credits = 0
        self.spins = 0
        self.total_spins = 10
        self.spinned_angle = 0
        # FIX LATER so we can change the number of prizes
        self.initial_rotation = self.triangle_angle * 4.5
        self.rotation_angle = self.initial_rotation
        self.speed = 0
        self.max_speed = 0.125
        self.acceleration = 0.001
        self.radius = 350
        self.margin = 100
        self.prize_index = None
        self.start_time = 0
        self.elapsed_time = 0
        self.counting_time = False
        self.light_radius = 15
        self.confetti = []
        self.max_confetti = 500
        self.stop_confetti = False
        self.sound_channel = None
        self.playing_song = False

        self.images = {
            "background": pygame.image.load("assets/images/background.png"),
            "title": pygame.image.load("assets/images/title.png"),
        }

        # Rotate all images
        for key in self.images:
            self.images[key] = pygame.transform.rotate(self.images[key], 90)

        self.sounds = {
            "coin-in": pygame.mixer.Sound("assets/sounds/coin-in.mp3"),
            "playing": pygame.mixer.Sound("assets/sounds/playing.mp3"),
            "you-lose": pygame.mixer.Sound("assets/sounds/you-lose.mp3"),
            "you-win": pygame.mixer.Sound("assets/sounds/you-win.mp3"),
        }

        _, _, files = next(os.walk("assets/music/"))
        self.songs = []
        self.current_song = 0
        
        for i, _ in enumerate(files):
            song = "song_" + str(i + 1)

            song_file = pygame.mixer.Sound("assets/music/" + song + ".mp3")
            self.songs.append(song_file)

        # Load spins when initializing game
        self.load_spins()

    def load_spins(self):
        with open("spins.txt", "r") as file:
            spins = file.read()
            self.spins = int(spins)

    def save_spins(self):
        with open("spins.txt", "w") as file:
            file.write(str(self.spins))

    def reset(self):
        self.state = "idle"
        self.start_time = 0
        self.elapsed_time = 0
        self.counting_time = False
        self.stop_confetti = False
        self.songs[self.current_song].set_volume(1)
        self.confetti = []
        self.rotation_angle = self.initial_rotation

    def wait(self):
        if not self.counting_time:
            self.start_time = pygame.time.get_ticks()
            self.counting_time = True
        else:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

    def render(self, screen):
        # Update screen
        pygame.display.update()

        # Background
        bg = pygame.transform.scale(self.images["background"], (screen.get_width(), screen.get_height()))
        screen.blit(bg, (0, 0))

        # Render title
        new_height = screen.get_height() - self.margin * 2
        new_width = new_height * self.images["title"].get_width() / self.images["title"].get_height()

        title = pygame.transform.scale(self.images["title"], (new_width, new_height))
        screen.blit(title, (0, screen.get_height() // 2 - title.get_height() // 2))
        """
        title_font = pygame.font.Font(None, 64)
        title = title_font.render(self.title, True, WHITE)
        title = pygame.transform.rotate(title, 90)
        screen.blit(title, (self.margin, screen.get_height() // 2 - title.get_height() // 2))

        # Render subtitle
        subtitle = title_font.render(self.subtitle, True, WHITE)
        subtitle = pygame.transform.rotate(subtitle, 90)
        screen.blit(subtitle, (self.margin + title.get_width() + 32, screen.get_height() // 2 - subtitle.get_height() // 2))
        """

        # Render credits
        medium_font = pygame.font.Font(None, 48)
        credits_text = medium_font.render("Créditos: " + str(self.credits), True, WHITE)
        credits_text = pygame.transform.rotate(credits_text, 90)
        screen.blit(credits_text, (screen.get_width() - self.margin - credits_text.get_width(), self.margin))

        # Render current song
        song_text = medium_font.render("Canción " + str(self.current_song), True, WHITE)
        song_text = pygame.transform.rotate(song_text, 90)
        screen.blit(song_text, (screen.get_width() - self.margin - song_text.get_width(), screen.get_height() - self.margin - song_text.get_height()))


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
            prize_font = pygame.font.Font(None, 480 // len(self.prizes))
            mid_angle = angle + (self.triangle_angle / 2)  # middle of the wedge
            prize = prize_font.render(self.prizes[i], True, (240, 224, 103))

            # Convert radians -> degrees and rotate so it's upright in the wedge
            text_angle_deg = -math.degrees(mid_angle)
            prize = pygame.transform.rotate(prize, text_angle_deg)

            # Position text along radius, centered
            text_radius = self.radius * 0.5
            text_x = center[0] + math.cos(mid_angle) * text_radius - prize.get_width() / 2
            text_y = center[1] + math.sin(mid_angle) * text_radius - prize.get_height() / 2

            screen.blit(prize, (text_x, text_y))

        # Render circle border
        pygame.draw.circle(screen, (65, 18, 12), center, self.radius + 5, width=25)

        # Render light bulbs
        for i in range(36):
            angle = (10 * math.pi / 180) * i

            if math.cos(angle) != -1:
                bulb_radius = 10
                x = center[0] + math.cos(angle) * (self.radius - bulb_radius / 2)
                y = center[1] + math.sin(angle) * (self.radius - bulb_radius / 2)
                
                pygame.draw.circle(screen, (247, 205, 45), (x, y), bulb_radius)

                transparent_surf = pygame.Surface((self.light_radius * 2, self.light_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(transparent_surf, (247, 205, 45, 50), (self.light_radius, self.light_radius), self.light_radius)

                screen.blit(transparent_surf, (x - self.light_radius, y - self.light_radius))

        # Render pointer 
        pointer_points = [
            (center[0] - self.radius - 30, center[1] + 25),
            (center[0] - self.radius - 30, center[1] - 25),
            (center[0] - self.radius + 25, center[1])
        ]
        pygame.draw.polygon(screen, (244, 178, 1), pointer_points)

        # Render win message
        if self.state == "show_prize":
            if self.prizes[self.prize_index] != "Perdiste":
                text = medium_font.render("¡Felicitaciones, ganaste!", True, WHITE)
                text = pygame.transform.rotate(text, 90)

                screen.blit(text, (screen.get_width() - self.margin * 3, screen.get_height() // 2 - text.get_height() // 2))
            else:
                text = medium_font.render("Lo sentimos, perdiste :(", True, WHITE)
                text = pygame.transform.rotate(text, 90)

                screen.blit(text, (screen.get_width() - self.margin * 3, screen.get_height() // 2 - text.get_height() // 2))

        # Render confetti
        for confetti in self.confetti:
            confetti.render(screen)

        # Render DEBUG DATA
        if self.debug == True:
            debug_font = pygame.font.Font(None, 24)

            # Render number of spins
            spins_text = debug_font.render("spins: " + str(self.spins), True, DEBUG_COLOR)
            spins_text = pygame.transform.rotate(spins_text, 90)
            x = screen.get_width() - spins_text.get_width() * 6
            y = screen.get_height() - spins_text.get_height()
            screen.blit(spins_text, (x, y))

            # Render state
            state_text = debug_font.render("state: " + self.state, True, DEBUG_COLOR)
            state_text = pygame.transform.rotate(state_text, 90)
            x = screen.get_width() - state_text.get_width() * 5
            y = screen.get_height() - state_text.get_height()
            screen.blit(state_text, (x, y))

            # Render counting time
            counting_time_text = debug_font.render("counting_time: " + str(self.counting_time), True, DEBUG_COLOR)
            counting_time_text = pygame.transform.rotate(counting_time_text, 90)
            x = screen.get_width() - counting_time_text.get_width() * 4
            y = screen.get_height() - counting_time_text.get_height()
            screen.blit(counting_time_text, (x, y))

            # Render elapsed time
            elapsed_time_text = debug_font.render("elapsed_time: " + str(self.elapsed_time), True, DEBUG_COLOR)
            elapsed_time_text = pygame.transform.rotate(elapsed_time_text, 90)
            x = screen.get_width() - elapsed_time_text.get_width() * 3
            y = screen.get_height() - elapsed_time_text.get_height()
            screen.blit(elapsed_time_text, (x, y))

            # Render winned prize
            if self.prize_index != None:
                won_prize_text = debug_font.render("won prize: " + self.prizes[self.prize_index], True, DEBUG_COLOR)
                won_prize_text = pygame.transform.rotate(won_prize_text, 90)
                x = screen.get_width() - won_prize_text.get_width() * 2
                y = screen.get_height() - won_prize_text.get_height()
                screen.blit(won_prize_text, (x, y))

            # Render prize index
            prize_index_text = debug_font.render("prize_index: " + str(self.prize_index), True, DEBUG_COLOR)
            prize_index_text = pygame.transform.rotate(prize_index_text, 90)
            x = screen.get_width() - prize_index_text.get_width()
            y = screen.get_height() - prize_index_text.get_height()
            screen.blit(prize_index_text, (x, y))

    def decide_prize(self):
        # Every 100 spins, win a rare prize
        common_quantity = len(self.common_prizes)
        if self.spins != 0 and self.spins % self.rare_interval == 0:
            special_quantity = len(self.special_prizes)
            rare_quantity = len(self.rare_prizes)

            # Index inside rare prizes list
            rare_index = 0

            # If rare prizes has more than one prize get a random index
            if rare_quantity != 0:
                rare_index = random.randrange(0, rare_quantity)

            # Select a random index from rare prizes array and add the length of common and special prizes
            self.prize_index = common_quantity + special_quantity + rare_index
        # Every 25 spins, win a special prize
        elif self.spins != 0 and self.spins % self.special_interval == 0:
            special_quantity = len(self.special_prizes)

            # Index inside special prizes list
            special_index = 0
            
            # If special prizes has more than one prize get a random index
            if special_quantity != 0:
                special_index = random.randrange(0, special_quantity)

            # Select a random index from special prizes array and add the length of common prizes
            self.prize_index = common_quantity + special_index
        # Each spin, win a common prize (you lose included)
        else:
            # Select a random index from common prizes array
            self.prize_index = random.randrange(0, common_quantity)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_c:
                    self.credits += 1
                    self.sound_channel = self.sounds["coin-in"].play()
                elif event.key == pygame.K_r and self.state == "show_prize":
                    self.reset()
                elif event.key == pygame.K_d:
                    self.debug = not self.debug
                elif event.key == pygame.K_m and self.credits > 0:
                    if self.current_song < len(self.songs) - 1:
                        self.songs[self.current_song].stop()
                        self.playing_song = False
                        self.current_song += 1
                    else:
                        self.songs[self.current_song].stop()
                        self.playing_song = False
                        self.current_song = 0
                elif event.key == pygame.K_p:
                    if self.state == "idle":
                        if self.credits > 0:
                            self.state = "playing"
                            self.songs[self.current_song].set_volume(0)
                            self.sound_channel = self.sounds["playing"].play()
                            self.credits -= 1
                            self.spins += 1
                            
                            self.save_spins()
                            self.decide_prize()
                        else:
                            if self.state == "idle":
                                pass
                elif event.key == pygame.K_MINUS and self.debug:
                    self.spins -= 1
                elif event.key == pygame.K_PLUS and self.debug:
                    self.spins += 1

    def update(self, screen):
        # Rotate wheel
        self.rotation_angle += self.speed

        # Play music
        if self.playing_song == False:
            self.songs[self.current_song].play(-1)
            self.playing_song = True

        # Change light radius (min radius 15)
        radius = abs(math.sin(time.time()) * 18)
        if radius > 15:
            self.light_radius = radius

        if self.state == "playing":
            if self.speed < self.max_speed:
                self.speed += self.acceleration
            else:
                self.state = "stopping"

        if self.state == "stopping":
            spin = (len(self.prizes) * self.triangle_angle)
            if self.rotation_angle >= self.initial_rotation + spin * self.total_spins - (self.triangle_angle * self.prize_index):
                self.speed = 0
                half_triangle_angle = self.triangle_angle / 2
                self.rotation_angle = half_triangle_angle * round(self.rotation_angle / half_triangle_angle)
                
                # Stop the playing sound
                self.sounds["playing"].stop()

                if self.prizes[self.prize_index] == "Perdiste":
                    self.sound_channel = self.sounds["you-lose"].play()
                else:
                    self.sound_channel = self.sounds["you-win"].play()
                
                self.state = "show_prize"

        if self.state == "show_prize":
            # If mixer is not busy, set music volume to 1
            if self.sound_channel.get_sound() != self.sounds["you-win"] and self.sound_channel.get_sound() != self.sounds["you-lose"]:
                self.songs[self.current_song].set_volume(1)

            if self.prizes[self.prize_index] == "Perdiste":
                # Wait 5 seconds before changing state
                self.wait()
                if self.elapsed_time > 5:
                    self.reset()
            else:
                if len(self.confetti) < self.max_confetti and not self.stop_confetti:
                    right_confetti = Confetti(0, 0, "right")
                    left_confetti = Confetti(0, screen.get_height(), "left")

                    self.confetti.append(right_confetti)
                    self.confetti.append(left_confetti)
                else:
                    # Stop throwing confetti
                    self.stop_confetti = True

                # Update confetti
                if len(self.confetti) > 0:
                    for confetti in self.confetti:
                        confetti.update()

                        # Remove confetti if not shown on screen
                        if confetti.x > screen.get_width() + confetti.w and self.stop_confetti:
                            self.confetti.remove(confetti)
