
import pygame
import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)
BLUE = (0, 0, 255)
 
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
 
 
class Player(pygame.sprite.Sprite):
 
    def __init__(self):
 
        super().__init__()
 
        width = 10
        height = 10
        self.image = pygame.Surface([width, height])
        self.image.fill(PURPLE)
        self.reset = 0
        self.rect = self.image.get_rect()
        self.startingX = 300
        self.startingY = SCREEN_HEIGHT - self.rect.height
        self.change_x = 0
        self.change_y = 0
        self.level = None
 
    def update(self):
        self.calc_grav()
        if self.rect.x < 0:
            self.change_x = 0
            self.rect.x = 0
        
        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.change_x = 0
            self.rect.x = SCREEN_WIDTH - self.rect.width
 
        self.rect.x += self.change_x
 
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        self.rect.y += self.change_y

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
 
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
 
            self.change_y = 0
 
            if isinstance(block, MovingPlatform):
                self.rect.x += block.change_x

        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for enemy in enemy_hit_list:
            self.reset = 1
            self.rect.x = self.startingX
            self.rect.y = self.startingY
 
    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35
 
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height
 
    def jump(self):
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
 
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -7
 
    def go_left(self):
        if self.rect.x <= 0 and self.change_x >= 0:
            self.change_x = 0
            self.rect.x = 0
        else:
            self.change_x = -3
 
    def go_right(self):
        if self.rect.x >= SCREEN_WIDTH - self.rect.width and self.change_x <= 0:
            self.change_x = 0
            self.rect.x = SCREEN_WIDTH - self.rect.width
        else:
            self.change_x = 3
 
    def stop(self):
        self.change_x = 0
 
class Platform(pygame.sprite.Sprite):
 
    def __init__(self, width, height, color):
        super().__init__()
 
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

class MovingPlatform(Platform):
    change_x = 0
    change_y = 0
    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0
 
    player = None
    level = None

    def update(self):
        self.rect.x += self.change_x
        hit = pygame.sprite.collide_rect(self, self.player)

        if hit:
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            elif self.change_x > 0:
                self.player.rect.left = self.rect.right
            else:
                if self.player.rect.right > self.rect.left:
                    self.player.rect.right = self.rect.left - 1
                else:
                    self.player.rect.left = self.rect.right + 1

        self.rect.y += self.change_y
 
        hit = pygame.sprite.collide_rect(self, self.player)

        if hit:
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            elif self.change_y > 0:
                self.player.rect.top = self.rect.bottom
            else:
                if self.player.rect.bottom < self.rect.top:
                    self.player.rect.bottom = self.rect.top - 1
                else:
                    self.player.rect.top = self.rect.bottom + 1
 
        if self.rect.bottom > self.boundary_bottom and self.change_y > 0:
            self.change_y *= -1.0
    
        if self.rect.top < self.boundary_top and self.change_y < -0:
            self.change_y *= -1.0
 
        if self.rect.x < self.boundary_left or self.rect.x > self.boundary_right:
            self.change_x *= -1.0
 
class TeleportingPlatform(Platform):
    change_x = 0
    change_y = 0
    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0
 
    player = None
    level = None

    def update(self):

        self.rect.x += self.change_x

        hit = pygame.sprite.collide_rect(self, self.player)

        if hit:
            if self.change_x <= 0:
                self.player.rect.right = self.rect.left
            else:
                self.player.rect.left = self.rect.right
 
        self.rect.y += self.change_y
 
        hit = pygame.sprite.collide_rect(self, self.player)

        if hit:
            if self.change_y <= 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom
 
        if self.rect.y > self.boundary_bottom:
            self.rect.y = self.boundary_top
    
        if self.rect.y < self.boundary_top:
            self.rect.y = self.boundary_bottom

        if self.rect.x > self.boundary_right:
            self.rect.x = self.boundary_left
    
        if self.rect.x < self.boundary_left:
            self.rect.x = self.boundary_right
 
class Level(object):
 
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        player.startingX = 300
        player.startingY = SCREEN_HEIGHT - player.rect.height
        self.player = player
        self.background = None
 
    def update(self):
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        screen.fill(BLUE)
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)

class Level_00(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)
 
        #[x, y, width, height, color]
        platform_list = [
            [700, 580, 100, 20, WHITE],
            [0, 580, 100, 20, WHITE],
            ]


        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

class Level_01(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)
 
        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [700, 290, 20, 20, GREEN],
            [100, 560, 100, 40, GREEN],
            [100, 320, 20, 180,  GREEN],
            [50, 500, 20, 20, GREEN],
            [20, 450, 20, 20, GREEN],
            [50, 400, 20, 20, GREEN],
            [20, 350, 20, 20, GREEN],
            [640, 320, 20, 180, GREEN],
            [150, 400, 440, 20, GREEN],
            [140, 340, 20, 20, GREEN]
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [400, 280, 60, 20, GREEN, 400, 600, 1, 280, 280, 0],
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 560, 400, 40, RED],
            [0, 580, 100, 20, RED],
            ]

        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

class Level_02(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)
 
        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [700, 290, 20, 20, GREEN],
            [100, 560, 100, 40, GREEN],
            [100, 320, 20, 180,  GREEN],
            [50, 500, 20, 20, GREEN],
            [20, 450, 20, 20, GREEN],
            [50, 400, 20, 20, GREEN],
            [20, 350, 20, 20, GREEN],
            [460, 320, 20, 20, GREEN],
            [640, 320, 20, 180, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [400, 280, 60, 20, GREEN, 400, 600, 1, 280, 280, 0],
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 560, 400, 40, RED],
            [150, 400, 440, 20, RED],
            [0, 580, 100, 20, RED],
            [360, 200, 40, 130, RED],
            ]

        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

class Level_03(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)
 
        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [700, 290, 20, 20, GREEN],
            [100, 560, 100, 40, GREEN],
            [460, 320, 20, 20, GREEN],
            [100, 310, 40, 10, GREEN],
            [640, 320, 20, 180, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [400, 280, 60, 20, GREEN, 400, 600, 1, 280, 280, 0],
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],
            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 560, 400, 40, RED],
            [150, 400, 440, 20, RED],
            [0, 580, 100, 20, RED],
            [360, 200, 40, 130, RED],
            [100, 320, 40, 180,  RED],
            ]

        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

class Level_04(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)

        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [700, 290, 20, 20, GREEN],
            [100, 560, 100, 40, GREEN],
            [520, 380, 20, 20, GREEN],
            [100, 310, 40, 10, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [600, 280, 60, 20, GREEN, 600, 600, 0, 280, 400, 1],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],
            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 560, 400, 40, RED],
            [150, 400, 440, 20, RED],
            [0, 580, 100, 20, RED],
            [360, 200, 40, 160, RED],
            [100, 320, 40, 180, RED],
            [280, 220, 20, 180, RED],
            [640, 320, 20, 180, RED],
            ]

        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

class Level_05(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)

        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [700, 290, 20, 20, GREEN],
            [100, 560, 100, 40, GREEN],
            [100, 310, 50, 10, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [600, 280, 60, 20, GREEN, 600, 600, 0, 280, 340, 1],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],
            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],
            [460, 380, 20, 20, GREEN, 460, 540, 2, 380, 380, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 560, 400, 40, RED],
            [150, 400, 440, 20, RED],
            [360, 200, 40, 160, RED],
            [100, 320, 50, 100, RED],
            [280, 220, 20, 180, RED],
            [640, 320, 20, 180, RED],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        teleporting_enemy_list = [
            [0, 600, 100, 20, RED, 0, 0, 0, -20, 620, -1.0],
            ]
        
        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        for enemy in teleporting_enemy_list:
            block = TeleportingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)

class Level_06(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)

        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [100, 560, 100, 40, GREEN],
            [100, 310, 50, 10, GREEN],
            [460, 480, 180, 20, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [660, 280, 60, 20, GREEN, 660, 660, 0, 280, 440, -1],
            [720, 580, 60, 20, GREEN, 720, 720, 0, 440, 600, 1],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],
            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],
            [460, 380, 20, 20, GREEN, 460, 540, 2, 380, 380, 0],
            [400, 560, 20, 20, GREEN, 400, 460, 1, 560, 560, 0],
            [540, 560, 20, 20, GREEN, 480, 540, -1, 560, 560, 0],
            [560, 560, 20, 20, GREEN, 560, 620, 1, 560, 560, 0],
            [700, 560, 20, 20, GREEN, 640, 700, -1, 560, 560, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 580, 400, 20, RED],
            [150, 400, 440, 20, RED],
            [360, 200, 40, 160, RED],
            [100, 320, 50, 100, RED],
            [280, 220, 20, 180, RED],
            [640, 320, 20, 180, RED],
            [380, 420, 20, 180, RED],
            ]
            
        teleporting_enemy_list = [
            [0, 600, 100, 20, RED, 0, 0, 0, -20, 620, -1.0],
            ]

        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)
            
        for enemy in teleporting_enemy_list:
            block = TeleportingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)

class Level_07(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)

        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [100, 560, 100, 40, GREEN],
            [100, 310, 50, 10, GREEN],
            [460, 480, 180, 20, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [660, 280, 60, 20, GREEN, 660, 660, 0, 280, 440, -1],
            [720, 580, 60, 20, GREEN, 720, 720, 0, 440, 600, 1],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],
            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],
            [460, 380, 20, 20, GREEN, 460, 540, 2, 380, 380, 0],
            [400, 560, 20, 20, GREEN, 400, 460, 1, 560, 560, 0],
            [540, 560, 20, 20, GREEN, 480, 540, -1, 560, 560, 0],
            [560, 560, 20, 20, GREEN, 560, 620, 1, 560, 560, 0],
            [700, 560, 20, 20, GREEN, 640, 700, -1, 560, 560, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 580, 400, 20, RED],
            [150, 400, 440, 20, RED],
            [360, 200, 40, 160, RED],
            [100, 320, 50, 100, RED],
            [280, 220, 20, 180, RED],
            [640, 320, 20, 180, RED],
            [380, 420, 20, 180, RED],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_enemy_list = [
            [570, 400, 20, 20, RED, 570, 640, 1, 400, 400, 0],
            [570, 400, 20, 20, RED, 570, 570, 0, 400, 500, 1],
            [520, 400, 20, 20, RED, 520, 520, 0, 400, 500, 1.5],
            [470, 400, 20, 20, RED, 470, 470, 0, 400, 500, 2],
            [640, 270, 20, 20, RED, 640, 800, 2, 270, 600, 2],
            ]
            
        teleporting_enemy_list = [
            [0, 600, 100, 20, RED, 0, 0, 0, -20, 620, -1.0],
            ]
        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        for enemy in moving_enemy_list:
            block = MovingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)
            
        for enemy in teleporting_enemy_list:
            block = TeleportingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)

class Level_08(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)

        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [100, 110, 50, 10, GREEN],
            [460, 480, 180, 20, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [660, 280, 60, 20, GREEN, 660, 660, 0, 280, 440, -1],
            [720, 580, 60, 20, GREEN, 720, 720, 0, 440, 600, 1],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],

            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],

            [100, 300, 20, 20, GREEN, 0, 100, 1.5, 300, 300, 0],
            [0, 250, 20, 20, GREEN, 0, 100, 1.5, 250, 250, 0],
            [100, 200, 20, 20, GREEN, 0, 100, 1.5, 200, 200, 0],
            [0, 150, 20, 20, GREEN, 0, 100, 1.5, 150, 150, 0],

            [460, 380, 20, 20, GREEN, 460, 540, 2, 380, 380, 0],
            [400, 560, 20, 20, GREEN, 400, 460, 1, 560, 560, 0],
            [540, 560, 20, 20, GREEN, 480, 540, -1, 560, 560, 0],
            [560, 560, 20, 20, GREEN, 560, 620, 1, 560, 560, 0],
            [100, 400, 100, 20, GREEN, 100, 100, 0, 400, 600, -1.0],
            [700, 560, 20, 20, GREEN, 640, 700, -1, 560, 560, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 580, 400, 20, RED],
            [150, 400, 440, 20, RED],
            [360, 200, 40, 160, RED],
            [100, 120, 50, 300, RED],
            [280, 220, 20, 180, RED],
            [640, 320, 20, 180, RED],
            [380, 420, 20, 180, RED],
            [0, 580, 200, 20, RED],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_enemy_list = [
            [570, 400, 20, 20, RED, 570, 640, 1, 400, 400, 0],
            [570, 400, 20, 20, RED, 570, 570, 0, 400, 500, 1],
            [520, 400, 20, 20, RED, 520, 520, 0, 400, 500, 1.5],
            [470, 400, 20, 20, RED, 470, 470, 0, 400, 500, 2],
            [640, 270, 20, 20, RED, 640, 800, 2, 270, 600, 2],
            ]
            
        teleporting_enemy_list = [
            [0, 600, 100, 20, RED, 0, 0, 0, -20, 620, -1.0],
            ]
        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        for enemy in moving_enemy_list:
            block = MovingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)
            
        for enemy in teleporting_enemy_list:
            block = TeleportingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)

class Level_09(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)

        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [460, 480, 180, 20, GREEN],
            [100, 100, 600, 20, GREEN],
            [200, 180, 600, 20, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [660, 280, 60, 20, GREEN, 660, 660, 0, 280, 440, -1],
            [720, 580, 60, 20, GREEN, 720, 720, 0, 440, 600, 1],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],
            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],
            [100, 300, 20, 20, GREEN, 0, 100, 1.5, 300, 300, 0],
            [0, 250, 20, 20, GREEN, 0, 100, 1.5, 250, 250, 0],
            [100, 200, 20, 20, GREEN, 0, 100, 1.5, 200, 200, 0],
            [0, 150, 20, 20, GREEN, 0, 100, 1.5, 150, 150, 0],
            [460, 380, 20, 20, GREEN, 460, 540, 2, 380, 380, 0],
            [400, 560, 20, 20, GREEN, 400, 460, 1, 560, 560, 0],
            [540, 560, 20, 20, GREEN, 480, 540, -1, 560, 560, 0],
            [560, 560, 20, 20, GREEN, 560, 620, 1, 560, 560, 0],
            [100, 400, 100, 20, GREEN, 100, 100, 0, 400, 600, -1.0],
            [700, 560, 20, 20, GREEN, 640, 700, -1, 560, 560, 0],
            ]

        teleporting_platform_list = [
            [120, 140, 20, 60, GREEN, 120, 800, 5, 140, 140, 0],
            ]

        #[x, y, width, height, color]
        enemy_list = [
            [400, 580, 400, 20, RED],
            [780, 0, 20, 200, RED],
            [150, 400, 440, 20, RED],
            [360, 200, 40, 140, RED],
            [100, 120, 50, 300, RED],
            [280, 240, 20, 160, RED],
            [640, 320, 20, 180, RED],
            [380, 420, 20, 180, RED],
            [0, 580, 200, 20, RED],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_enemy_list = [
            [570, 400, 20, 20, RED, 570, 640, 1, 400, 400, 0],
            [570, 400, 20, 20, RED, 570, 570, 0, 400, 500, 1],
            [520, 400, 20, 20, RED, 520, 520, 0, 400, 500, 1.5],
            [470, 400, 20, 20, RED, 470, 470, 0, 400, 500, 2],
            [640, 270, 20, 20, RED, 640, 800, 2, 270, 600, 2],
            [0, 0, 20, 20, RED, 0, 800, 5, 0, 120, 1],
            ]
            
        teleporting_enemy_list = [
            [0, 600, 100, 20, RED, 0, 0, 0, -20, 620, -1.0],
            ]

        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        for enemy in moving_enemy_list:
            block = MovingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)
            
        for enemy in teleporting_enemy_list:
            block = TeleportingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)
        
        for platform in teleporting_platform_list:
            block = TeleportingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

class Level_10(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)

        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [460, 480, 180, 20, GREEN],
            [100, 100, 660, 20, GREEN],
            [200, 180, 600, 20, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [660, 280, 60, 20, GREEN, 660, 660, 0, 280, 440, -1],
            [720, 580, 60, 20, GREEN, 720, 720, 0, 440, 600, 1],
            [300, 380, 60, 20, GREEN, 300, 400, -1, 380, 380, 0],
            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],
            [100, 300, 20, 20, GREEN, 0, 100, 1.5, 300, 300, 0],
            [0, 250, 20, 20, GREEN, 0, 100, 1.5, 250, 250, 0],
            [100, 200, 20, 20, GREEN, 0, 100, 1.5, 200, 200, 0],
            [0, 150, 20, 20, GREEN, 0, 100, 1.5, 150, 150, 0],
            [460, 380, 20, 20, GREEN, 460, 540, 2, 380, 380, 0],
            [400, 560, 20, 20, GREEN, 400, 460, 1, 560, 560, 0],
            [540, 560, 20, 20, GREEN, 480, 540, -1, 560, 560, 0],
            [560, 560, 20, 20, GREEN, 560, 620, 1, 560, 560, 0],
            [100, 400, 100, 20, GREEN, 100, 100, 0, 400, 600, -1.0],
            [700, 560, 20, 20, GREEN, 640, 700, -1, 560, 560, 0],
            ]

        teleporting_platform_list = [
            [120, 120, 20, 20, GREEN, 120, 800, 5, 120, 120, 0],
            [120, 160, 20, 20, GREEN, 120, 800, 5, 160, 160, 0],
            ]
        
        #[x, y, width, height, color]
        enemy_list = [
            [400, 580, 400, 20, RED],
            [780, 0, 20, 200, RED],
            [150, 400, 440, 20, RED],
            [360, 200, 40, 140, RED],
            [100, 120, 50, 300, RED],
            [280, 240, 20, 160, RED],
            [640, 320, 20, 180, RED],
            [380, 420, 20, 180, RED],
            [0, 580, 200, 20, RED],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_enemy_list = [
            [570, 400, 20, 20, RED, 570, 640, 1, 400, 400, 0],
            [570, 400, 20, 20, RED, 570, 570, 0, 400, 500, 1],
            [520, 400, 20, 20, RED, 520, 520, 0, 400, 500, 1.5],
            [470, 400, 20, 20, RED, 470, 470, 0, 400, 500, 2],
            [640, 270, 20, 20, RED, 640, 800, 2, 270, 600, 2],
            [800, 270, 20, 20, RED, 640, 800, 2, 270, 600, 2],
            [0, 100, 20, 20, RED, 0, 800, 5, 0, 120, 1],
            [0, 0, 20, 20, RED, 0, 800, 5, 0, 120, 1],
            ]
            
        teleporting_enemy_list = [
            [0, 600, 100, 20, RED, 0, 0, 0, -20, 620, -1.0],
            [800, 140, 20, 20, RED, 120, 800, -5, 140, 140, 0],
            ]
        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        for enemy in moving_enemy_list:
            block = MovingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)
            
        for enemy in teleporting_enemy_list:
            block = TeleportingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)
        
        for platform in teleporting_platform_list:
            block = TeleportingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

class Level_11(Level):
 
    def __init__(self, player):
        
        Level.__init__(self, player)

        #[x, y, width, height, color]
        platform_list = [
            [750, 250, 50, 25, WHITE],
            [460, 480, 180, 20, GREEN],
            [100, 100, 660, 20, GREEN],
            [200, 180, 600, 20, GREEN],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_platform_list = [
            [300, 280, 60, 20, GREEN, 100, 300, -1, 280, 280, 0],
            [660, 280, 60, 20, GREEN, 660, 660, 0, 280, 440, -1],
            [720, 580, 60, 20, GREEN, 720, 720, 0, 440, 600, 1],
            [300, 380, 60, 20, GREEN, 300, 350, -1, 380, 380, 0],
            [100, 500, 20, 20, GREEN, 0, 100, 1.5, 500, 500, 0],
            [0, 450, 20, 20, GREEN, 0, 100, 1.5, 450, 450, 0],
            [100, 400, 20, 20, GREEN, 0, 100, 1.5, 400, 400, 0],
            [0, 350, 20, 20, GREEN, 0, 100, 1.5, 350, 350, 0],
            [100, 300, 20, 20, GREEN, 0, 100, 1.5, 300, 300, 0],
            [0, 250, 20, 20, GREEN, 0, 100, 1.5, 250, 250, 0],
            [100, 200, 20, 20, GREEN, 0, 100, 1.5, 200, 200, 0],
            [0, 150, 20, 20, GREEN, 0, 100, 1.5, 150, 150, 0],
            [400, 560, 20, 20, GREEN, 400, 460, 1, 560, 560, 0],
            [540, 560, 20, 20, GREEN, 480, 540, -1, 560, 560, 0],
            [560, 560, 20, 20, GREEN, 560, 620, 1, 560, 560, 0],
            [100, 400, 100, 20, GREEN, 100, 100, 0, 400, 600, -1.0],
            [700, 560, 20, 20, GREEN, 640, 700, -1, 560, 560, 0],
            ]

        teleporting_platform_list = [
            [120, 120, 20, 20, GREEN, 120, 800, 5, 120, 120, 0],
            [120, 160, 20, 20, GREEN, 120, 800, 5, 160, 160, 0],
            [500, 180, 80, 20, GREEN, 500, 500, 0, 180, 400, -1],
            [560, 290, 80, 20, GREEN, 560, 560, 0, 180, 400, -1],
            [430, 180, 50, 20, GREEN, 430, 430, 0, 180, 400, 1],
            [400, 235, 50, 20, GREEN, 400, 400, 0, 180, 400, 1],
            [430, 290, 50, 20, GREEN, 430, 430, 0, 180, 400, 1],
            [400, 345, 50, 20, GREEN, 400, 400, 0, 180, 400, 1],
            ]
        
        #[x, y, width, height, color]
        enemy_list = [
            [400, 580, 400, 20, RED],
            [780, 0, 20, 200, RED],
            [150, 400, 440, 20, RED],
            [360, 200, 40, 100, RED],
            [100, 120, 50, 300, RED],
            [280, 240, 20, 160, RED],
            [640, 200, 20, 300, RED],
            [380, 420, 20, 180, RED],
            [0, 580, 200, 20, RED],
            [480, 240, 20, 160, RED],
            ]

        #[x, y, width, height, color, leftX, rightX, xspeed, topY, bottomY, yspeed]
        moving_enemy_list = [
            [570, 400, 20, 20, RED, 570, 640, 1, 400, 400, 0],
            [570, 400, 20, 20, RED, 570, 570, 0, 400, 500, 1],
            [520, 400, 20, 20, RED, 520, 520, 0, 400, 500, 1.5],
            [470, 400, 20, 20, RED, 470, 470, 0, 400, 500, 2],
            [640, 270, 20, 20, RED, 640, 800, 2, 270, 600, 2],
            [800, 270, 20, 20, RED, 640, 800, 2, 270, 600, 2],
            [0, 100, 20, 20, RED, 0, 800, 5, 0, 120, 1],
            [0, 0, 20, 20, RED, 0, 800, 5, 0, 120, 1],
            ]
            
        teleporting_enemy_list = [
            [0, 600, 100, 20, RED, 0, 0, 0, -20, 620, -1.0],
            [800, 140, 20, 20, RED, 120, 800, -5, 140, 140, 0],
            ]
        for enemy in enemy_list:
            block = Platform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.player = self.player
            self.enemy_list.add(block)

        for platform in platform_list:
            block = Platform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        for platform in moving_platform_list:
            block = MovingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        for enemy in moving_enemy_list:
            block = MovingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)
            
        for enemy in teleporting_enemy_list:
            block = TeleportingPlatform(enemy[2], enemy[3], enemy[4])
            block.rect.x = enemy[0]
            block.rect.y = enemy[1]
            block.boundary_left = enemy[5]
            block.boundary_right = enemy[6]
            block.boundary_top = enemy[8]
            block.boundary_bottom = enemy[9]
            block.change_x = enemy[7]
            block.change_y = enemy[10]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)
        
        for platform in teleporting_platform_list:
            block = TeleportingPlatform(platform[2], platform[3], platform[4])
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.boundary_left = platform[5]
            block.boundary_right = platform[6]
            block.boundary_top = platform[8]
            block.boundary_bottom = platform[9]
            block.change_x = platform[7]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

def main():
    pygame.init()
    pygame.mixer.init(frequency = 44100, size = -16, channels = 10, buffer = 2**12)
    PracticeSong = pygame.mixer.Sound('music/practice.mp3')
    MainMenuSong = pygame.mixer.Sound('music/mainmenu.mp3')
    MainGameSong = pygame.mixer.Sound('music/Manic.mp3')
    bruh = pygame.mixer.Sound('music/bruh.mp3')
    twentyone = pygame.mixer.Sound('music/21.mp3')
    boom = pygame.mixer.Sound('music/vineboom.mp3')
    oof = pygame.mixer.Sound('music/oof.mp3')
    ooh = pygame.mixer.Sound('music/ooh.mp3')
    LU = pygame.mixer.Sound('music/levelup.mp3')
    channel1 = pygame.mixer.Channel(0)
    channel2 = pygame.mixer.Channel(1)
    channel3 = pygame.mixer.Channel(2)
    channel4 = pygame.mixer.Channel(3)


    channel1.play(MainMenuSong, -1)
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
 
    pygame.display.set_caption("Rage Simulator")
 
    practice = 0

    player = Player()
    dead = 0


    player.rect.x = player.startingX
    player.rect.y = player.startingY

    level_list = []
    level_list.append(Level_00(player))
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))
    level_list.append(Level_03(player))
    level_list.append(Level_04(player))
    level_list.append(Level_05(player))
    level_list.append(Level_06(player))
    level_list.append(Level_07(player))
    level_list.append(Level_08(player))
    level_list.append(Level_09(player))
    level_list.append(Level_10(player))
    level_list.append(Level_11(player))
 
    current_level_no = 0
    current_level = level_list[current_level_no]
 
    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    font = pygame.font.Font(None, 64)
    text_list = []
    wanted_text_list = [
        ["Rage Game", 250, 100, BLACK],
        ["Start", 50, 500, BLACK],
        ["Practice", 600, 500, BLACK],
    ]
    
    text_list2 = []
    wanted_text_list2 = [
        ["Press Esc to return to the main menu", 5, 20, BLACK],
        ["Press the + and - to change levels", 50, 80, BLACK],
    ]
    
    for i in wanted_text_list:
        text = font.render(i[0], True, i[3])
        textpos = text.get_rect(x = i[1], y = i[2])
        out = (text, textpos)
        text_list.append(out)
    
    for i in wanted_text_list2:
        text = font.render(i[0], True, i[3])
        textpos = text.get_rect(x = i[1], y = i[2])
        out = (text, textpos)
        text_list2.append(out)


    active_sprite_list.add(player)
    done = False
 
    clock = pygame.time.Clock()
 
    while not done:
        main_menu = current_level_no
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.go_left()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.go_right()
                if event.key == pygame.K_SPACE:
                    print(practice)
                if (event.key == pygame.K_EQUALS) and practice == 1 and current_level_no < 11:
                    current_level_no += 1
                    current_level = level_list[current_level_no]
                    player.level = current_level
                    player.rect.x = player.startingX
                    player.rect.y = player.startingY
                if (event.key == pygame.K_MINUS) and practice == 1 and current_level_no > 1:
                    current_level_no -= 1
                    current_level = level_list[current_level_no]
                    player.level = current_level
                    player.rect.x = player.startingX
                    player.rect.y = player.startingY
 
            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT) and player.change_x < 0:
                    player.stop()
                if (event.key == pygame.K_RIGHT) and player.change_x > 0:
                    player.stop()
                if (event.key == pygame.K_a) and player.change_x < 0:
                    player.stop()
                if (event.key == pygame.K_d) and player.change_x > 0:
                    player.stop()
                if (event.key == pygame.K_ESCAPE) and practice == 1:
                    channel2.stop()
                    channel3.stop()
                    channel1.play(MainMenuSong, -1)
                    current_level_no = 0
                    current_level = level_list[current_level_no]
                    player.level = current_level
                    player.rect.x = player.startingX
                    player.rect.y = player.startingY
                    practice = 0


        current_level.update()
        active_sprite_list.update()
 
 
        screen.blit(text, textpos)
        if player.rect.y >= 240 and player.rect.y < 280 and player.rect.x > 740:
            channel4.play(LU)
            current_level_no += 1
            current_level = level_list[current_level_no]
            player.level = current_level
            player.rect.x = player.startingX
            player.rect.y = player.startingY
        elif player.rect.x >= 700 and player.rect.y > 530 and main_menu == 0:
            channel1.stop()
            channel3.stop()
            channel2.play(PracticeSong, -1)
            current_level_no += 1
            practice = 1
            current_level = level_list[current_level_no]
            player.level = current_level
            player.rect.x = player.startingX
            player.rect.y = player.startingY
        elif player.rect.x <= 100 and player.rect.y > 530 and main_menu == 0:
            channel1.stop()
            channel2.stop()
            channel3.play(MainGameSong, -1)
            current_level_no += 1
            current_level = level_list[current_level_no]
            player.level = current_level
            player.rect.x = player.startingX
            player.rect.y = player.startingY
        
        if player.reset >= 1 and practice == 0:
            channel2.stop()
            channel3.stop()
            channel1.play(MainMenuSong, -1)
            current_level_no = 0
            current_level = level_list[current_level_no]
            player.level = current_level
            player.reset = 0
            dead = 1
        elif player.reset >= 1 and practice == 1:
            player.reset = 0
            dead = 1

        current_level.draw(screen)
        active_sprite_list.draw(screen)
        if main_menu == 0:
            for i in text_list:
                screen.blit(i[0], i[1])
        elif main_menu == 1 and practice == 1:
            for i in text_list2:
                screen.blit(i[0], i[1])
 
        if dead == 1:
            dead = 0
            death = random.randint(1, 5)
            if death == 1:
                channel4.play(bruh)
            elif death == 2:
                channel4.play(twentyone)
            elif death == 3:
                channel4.play(boom)
            elif death == 4:
                channel4.play(oof)
            elif death == 5:
                channel4.play(ooh)

 
        clock.tick(60)
 
        pygame.display.flip()
 
    pygame.quit()
 

if __name__ == "__main__":
    main()