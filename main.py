# Imports required libraries for the game to run
import json
import os
import random
import random as r
import sys

import pygame as pg
import pygame.mixer
from pygame import mixer

from images import *

# initializes basic pygame functions
pygame.mixer.pre_init(44100, -16, 2, 2048 * 4)
pygame.init()
clock = pg.time.Clock()

# sets display side
screen = pg.display.set_mode((1280, 720))

# pre-inits lists and variables used globally in the program
tile_rects = []
enemies = []
game_start = False
win = False

# loads the json files that contain level data such as the map and all the spawn locations
file = open("levels.json", "r")
content = file.read()
map_gen = json.loads(content)

# initializez and loads the audio that will be used in the below game
mixer.music.load(os.path.join("audio", "sad.wav"))
mixer.music.set_volume(.3)
spotted_sound = mixer.Sound("audio/ghostbreath.wav")
unlock_sound = mixer.Sound("audio/Key Jiggle.wav")
mixer.music.play(-1)

# renders the font that's used in the game
font = pg.font.Font('Shiver.ttf', 12)

class text_effects:
    """
    static method used to store the text effects
    """
    @staticmethod
    def shakytext(text, x, y):
        """"
        :param text:
        :param x:
        :param y:
        :description:
        makes the individual letters shake when this function is used to blit text to a screen
        """
        spacing = 0
        for l in text:
            rngx = [-1, 1][random.randrange(2)]
            rngy = [-1, 1][random.randrange(2)]
            somewords = font.render(l, True, [255, 255, 255])
            screen.blit(somewords, (x + spacing + rngx, y + rngy))
            spacing += 15

# instantiates the above method to be called later in the code
text = text_effects

class MapRender:
    """
    Used to render the map from the levels.json file

    :description: Iterates throught the nested list and places a tile based on the number in the list
    """
    def __init__(self):
        """
        initializes all class variables
        """
        self.tile_rects = []
        self.door_rect = None
        self.current_level = 4

    def render_tiles(self):
        """
        Generates the map here
        each if checks for a different number in the nested list and blits the tile to that location
        Each tile is also added to an array that will later be used for collisions with the player
        """
        y = 0
        for row in map_gen[self.current_level]['level']:
            x = 0
            for tile in row:
                '''
                0: Floor
                1: Top Wall
                2: Left Wall
                3: Right Wall
                4: Bot Wall
                5: Top Left Corner
                6: Top Right Corner
                7: Bot Left Corner
                8: Bot Right Corner
                9: Top Right Sharp Corner
                10: Top Left Sharp Corner
                11: Bot Wall Left Curved
                12: Bot Wall Right Curved
                '''
                if tile == 0:  # floor
                    screen.blit(floor_tile, (x * 64, y * 64))
                elif tile == 1:  # top wall
                    screen.blit(top_wall, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 2:  # left wall
                    screen.blit(left_wall, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 3:  # right wall
                    screen.blit(right_wall, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 4:  # bot wall
                    screen.blit(bottom_wall, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 5:  # top left corner
                    screen.blit(top_left_corner, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 6:  # top right corner
                    screen.blit(top_right_corner, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 7:  # bot left corner
                    screen.blit(bot_left_corner, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 8:  # bot right corner
                    screen.blit(bot_right_corner, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 9:  # bot right corner
                    screen.blit(top_right_scorner, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 10:  # bot right corner
                    screen.blit(top_left_scorner, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 11:  # bot right corner
                    screen.blit(bot_rcurve, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 12:  # bot right corner
                    screen.blit(bot_lcurve, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                elif tile == 13:  # bot right corner
                    screen.blit(top_door, (x * 64, y * 64))
                    self.tile_rects.append(pygame.Rect(x * 64, y * 64, 64, 64))
                    self.door_rect = (pygame.Rect(x * 64, y * 64, 64, 70))
                x += 1
            y += 1

class player(pg.sprite.Sprite):
    """
    Main player class that contains most of the important code for the game to run
    """
    def animations(self):
        """
        Calls the animations and their frame duration in the game.
        """
        if self.idle:
            if self.current_frame < 5:
                self.image = idle[int(self.current_frame)]
                self.current_frame += 0.07
            else:
                self.current_frame = 0

        if self.right:
            if self.current_frame < 5:
                self.image = run[int(self.current_frame)]
                self.current_frame += 0.5
            else:
                self.current_frame = 0

        if self.left:
            if self.current_frame < 5:
                self.image = pg.transform.flip(run[int(self.current_frame)], True, False)
                self.current_frame += 0.5
            else:
                self.current_frame = 0

    def __init__(self):
        """
        all var's used in the player class
        """
        #creates a sprite super init
        pg.sprite.Sprite.__init__(self)
        # player movement
        self.image = player_img.convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = map_gen[map_render.current_level]['player_loc']
        self.speed = [0, 0]
        self.rebound_rect = None
        self.has_key = False
        self.current_frame = 0
        self.left = False
        self.right = False
        self.attack = False
        self.idle = True
        self.dead = False

        # Fog Of War
        self.dark = True
        self.fog = pg.Surface((1280, 720))
        self.fog.fill(pg.Color('#33142b'))
        self.light_mask = shadows
        self.light_mask = pg.transform.scale(self.light_mask, (300, 300))
        self.light_rect = self.light_mask.get_rect()

    def render_fog(self):
        """
        used to render the "shadow"/darkness around the player to simulate the dark conditions
        """
        self.fog.fill(pg.Color('#000000'))
        self.light_rect.center = self.rect.center
        self.fog.blit(self.light_mask, self.light_rect)
        screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_RGB_MULT)

    def collision_test(self, tiles):
        """
        :param tiles:
        tests for collisions with the player so see if they have collided with any time that was mapped earlier
        """
        hit_list = []
        for tile in tiles:
            if self.rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def colliders(self):
        """
        Does the actual collisions and sets the players position to that of which before when collided
        so that the player can run into the walls
        """
        hit_list = self.collision_test(map_render.tile_rects)
        for tile in hit_list:
            if self.speed[0] > 0:
                self.rect.right = self.rebound_rect.right
            if self.speed[0] < 0:
                self.rect.left = self.rebound_rect.left
            if self.speed[1] > 0:
                self.rect.bottom = self.rebound_rect.bottom
            if self.speed[1] < 0:
                self.rect.top = self.rebound_rect.top

    def Attack(self):
        """
        Code to attack enemies if they reach within a certain distance from the player
        """
        if self.attack:
            for enemy in enemies:
                if enemy.rect.centerx <= self.rect.centerx + 90 or enemy.rect.centerx <= self.rect.centerx - 90:
                    if enemy.rect.centery <= self.rect.centery + 90 or enemy.rect.centery <= self.rect.centery - 90:
                        enemy.dead = True

    def level_up(self):
        """
        checks if the player collides with a door rect and if they have a key.
        Then levels them up to the next level.
        Once all the levels are done then win is set to true which brings the player to the victory screen
        """
        global game_start, win
        if self.rect.colliderect(map_render.door_rect):
            if map_render.current_level < 5:
                if self.has_key:
                    unlock_sound.play()
                    if map_render.current_level + 1 == 5:
                        game_start = False
                        win = True
                    else:
                        map_render.current_level += 1
                    map_render.tile_rects.clear()
                    enemies.clear()
                    enemy_sprites.empty()
                    key.__init__()
                    player.rect.center = map_gen[map_render.current_level]['player_loc']
                    enemy_render()
                    player.has_key = False
                else:
                    # generates the shaky text from the static method above
                    text.shakytext("I need to find a key...", player.rect.x-120, player.rect.y+80)
    def update(self):
        """
        called every frames and checks for movements and player position so that the above functions can run properly
        """
        self.animations()
        self.speed = [0, 0]
        self.rebound_rect = self.rect.copy()
        key_state = pg.key.get_pressed()
        if key_state[pg.K_a]:
            self.speed[0] = -3
            self.left = True
            self.right = False
            self.idle = False
        elif key_state[pg.K_d]:
            self.speed[0] = 3
            self.left = False
            self.right = True
            self.idle = False
        else:
            self.idle = True
            self.left = False
            self.right = False

        if key_state[pg.K_w]:
            self.speed[1] = -3
            self.left = False
            self.right = True
            self.idle = False
        elif key_state[pg.K_s]:
            self.speed[1] = 3
            self.left = False
            self.right = True
            self.idle = False
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        if key_state[pg.K_SPACE]:
            self.attack = True
        elif not key_state[pg.K_SPACE]:
            self.attack = False

class Enemy(pg.sprite.Sprite):
    def __init__(self):
        """
        Inits all variables used in the enemy class
        """

        # make this a super init of the built in sprite class
        pg.sprite.Sprite.__init__(self)
        self.image = enemy_img.convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = r.choice(map_gen[map_render.current_level]['spawn_loc'])
        self.speed = [0, 0]
        self.rebound_rect = None
        self.hp = 1
        self.screem = False
        self.dead = False
        self.current_frame = 0
        self.left = False
        self.right = False

    def animations(self):
        """
        enemy animations and frame timings
        :note: animations are based on the players position relative from the enemy
        """
        if self.left:
            if self.current_frame < 5:
                self.image = move[int(self.current_frame)]
                self.current_frame += 0.07
            else:
                self.current_frame = 0
        if self.right:
            if self.current_frame < 5:
                self.image = pg.transform.flip(move[int(self.current_frame)], True, False)
                self.current_frame += 0.07
            else:
                self.current_frame = 0

    def update(self):  # follow player function
        """
        Called every frame
        moves the enemy closer to the player each tick until their sprites collide which kills the player
        also calls the animations from above
        """
        self.animations()
        self.speed = [0, 0]
        if not player.rect.x + 300 <= self.rect.x or not player.rect.x - 300 <= self.rect.x:
            if not player.rect.y + 300 <= self.rect.y or not player.rect.y - 300 <= self.rect.y:
                if not self.screem:
                    spotted_sound.play()
                    self.screem = True
                if not self.rect.colliderect(player.rect):
                    if self.rect.x > player.rect.x:
                        self.speed[0] = 2
                        self.rect.x -= self.speed[0]
                        self.right = True
                        self.left = False
                    elif self.rect.x < player.rect.x:
                        self.speed[0] = 2
                        self.rect.x += self.speed[0]
                        self.left = True
                        self.right = False
                    if self.rect.y > player.rect.y:
                        self.speed[1] = 2
                        self.rect.y -= self.speed[1]
                    elif self.rect.y < player.rect.y:
                        self.speed[1] = 2
                        self.rect.y += self.speed[1]
                else:
                    player.dead = True

class Key(pg.sprite.Sprite):
    """
    Sprite class for the key thats generated on every level
    """
    global win, game_start
    def __init__(self):
        """
        Declares variables needed for the init
        """

        # creates a built-in sprite super init
        pg.sprite.Sprite.__init__(self)
        self.image = keyy
        self.rect = self.image.get_rect()
        self.rect.center = map_gen[map_render.current_level]["key_loc"]
        self.simage = mini_key

    def update(self):
        """
        Checks if its collided with the player and gives them a key
        """
        if self.rect.colliderect(player.rect):
            player.has_key = True
        if player.has_key:
            self.image = self.simage
            self.rect.x = player.rect.x + 10
            self.rect.y = player.rect.y + 25

class Menu:
    """
    Class that dictates what happens with the screens out of game such as menu and settings
    """
    def __init__(self):
        # sets mainmenu as the base image for the screens
        self.image = mainmenu

    def update(self):
        """
        Updates each tick and changes the displayed screen from the game, victory, menu,
        and setting based on input and game state
        """
        global game_start, win
        key_state = pg.key.get_pressed()
        if key_state[pg.K_SPACE] and game_start == False:
            game_start = True
            player.dead = False
            map_render.current_level = 0
            map_render.tile_rects.clear()
            key.__init__()
            player.rect.center = map_gen[map_render.current_level]['player_loc']
            player.has_key = False
            win = False
        if key_state[pg.K_TAB]:
            self.image = controls
        if self.image == controls and key_state[pg.K_ESCAPE]:
            self.image = mainmenu
        if win:
            self.image = end
            if key_state[pg.K_m]:
                win = False
                self.image = mainmenu
        if player.dead:
            game_start = False

#  instantiates the above classes
map_render = MapRender()
all_sprites = pg.sprite.Group()
enemy_sprites = pg.sprite.Group()

# static function used to create multiple enemies from a single repeated instance
def enemy_render():
    for i in range(map_gen[map_render.current_level]['enemy_amount']):
        enemy = Enemy()
        enemy_sprites.add(enemy)
        enemies.append(enemy)
enemy_render()

# instantiates player and sprite groups the above classes
player = player()
all_sprites.add(player)
key = Key()
all_sprites.add(key)
menu = Menu()

def main():
    """
    main game loop that contains everything from above
    runs until program is stopped
    """
    while True:
        """
        based on game states different options are availiple to player such as menus and movement
        """
        global game_start, win
        menu.update()
        if game_start:
            for enemy in enemies:
                if enemy.dead:
                    enemy_sprites.remove(enemy)
            screen.fill(pg.Color('#33142b'))
            map_render.tile_rects.clear()
            map_render.render_tiles()
            player.colliders()
            player.Attack()
            all_sprites.update()
            all_sprites.draw(screen)
            enemy_sprites.update()
            enemy_sprites.draw(screen)
            player.render_fog()
            player.level_up()
        if not game_start:
            menu.update()
            screen.blit(menu.image, (0, 0))

        # checks is game is closed by the user and quits
        for event in pg.event.get():
            if event.type == pg.QUIT:
                file.close()
                pg.quit()
                sys.exit()
        # updates display and sets fps to 60 ticks
        pg.display.update()
        clock.tick(60)

# runs the main function thus playing the game
if __name__ == '__main__':
    main()