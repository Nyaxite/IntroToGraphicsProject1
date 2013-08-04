# Source File Name: Project_1.py
# Names: Michael Burnie, Evan Pugh
# Last Modified By: Michael Burnie
# Date Last Modified: August 4, 2013
""" 
  Program Description: You play as an orb of lightning. The objective is to get to the other side of 
  the level without dying. 

    Version: 1
    - Added player
        - attacking state, player can kill enemies in this state
            - triggered with left click
        - player can move with W and D or arrow keys, and SPACE to jump
        - charging state occurs after attacking. Must charge prior to next attack
        - invulnerability state occurs after being hit, so the player cannot be hit again
        - jumping state simulates jumping mechanics
        - player health bar is displayed above the player
    - Added Enemies
        - Enemies shoot based on player location
        - Enemies spawn in random locations
    - Collisions between enemies and players are checked
    - Added background, level one
    - Menu with basic buttons
 
"""

import pygame, os, math, random, Buttons
pygame.init()

WINDOW_POS_X = 50
WINDOW_POS_Y = 50

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (WINDOW_POS_X , WINDOW_POS_Y)

SCREEN = pygame.display.set_mode((800, 600) )#, pygame.FULLSCREEN | pygame.NOFRAME)#resolution

FRAMES_PER_SECOND = 30
MOUSE_SENSITIVITY_FACTOR = 0.7

SCROLL_SPEED = 10

GRAVITY = 1.5
JUMP_SPEED = 20

PLAYER_LEFT_POS = 300
PLAYER_BOTTOM_POS = 500
PLAYER_MAX_HEALTH = 50

NUM_OF_ENEMIES = 15
ENEMY_LOS_MAX_DISTANCE = 300

class Player(pygame.sprite.Sprite):
    """
    Constructor for Player Class   
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("player.png")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()  
        self.rect.left = PLAYER_LEFT_POS
        self.rect.bottom = PLAYER_BOTTOM_POS
        self.jumping = False
        
        self.health = PLAYER_MAX_HEALTH
        self.healthPercent = self.health / PLAYER_MAX_HEALTH * 100
        self.healthBar = HealthBar(self.healthPercent)
        self.displayHealth = False
        self.displayHealthDuration = 60
        self.displayHealthElapsed = 0
        
        self.invulnerable = False
        self.invulnerabilityDuration = 30
        self.invulnerabilityElapsed = 0
                
        self.attacking = False
        self.attackDuration = 30 #in frames
        self.attackElapsed = 0
        
        self.fullyCharged = True
        self.attackDelay = 60 #delay between attacks
        
        self.facing = "right"
        
        self.dy = JUMP_SPEED
        self.dx = SCROLL_SPEED
        
    def update(self):
        
        self.updateHealth()
        self.checkInvulnerability()
        
        if(self.jumping):
            self.jump()
            
        if(self.attacking and self.attackElapsed == 0):
            self.fullyCharged = False
            self.attack()
        if(self.attackElapsed == self.attackDuration):
            self.attacking = False
            self.neutral()
        if(self.attackElapsed >= self.attackDelay):
            self.fullyCharged = True
            self.attackElapsed = 0  
        if(self.attacking or not self.fullyCharged):
            self.attackElapsed += 1  
    
    def updateHealth(self):
        if(self.displayHealth and self.displayHealthElapsed < self.displayHealthDuration):
            self.healthPercent = self.health * 100 / PLAYER_MAX_HEALTH
            print(self.health, PLAYER_MAX_HEALTH, self.healthPercent)
            self.healthBar = HealthBar(self.healthPercent)
            self.healthBar.rect.centerx = self.rect.centerx
            self.healthBar.rect.centery = self.rect.centery - 50
            self.displayHealthElapsed += 1
        elif(self.displayHealth and self.displayHealthElapsed >= self.displayHealthDuration):
            self.healthBar.reset()
            self.displayHealth = False
            self.displayHealthElapsed = 0
            
    def checkInvulnerability(self):
        if(self.invulnerable and self.invulnerabilityElapsed < self.invulnerabilityDuration):
            self.invulnerabilityElapsed += 1 
            if(self.invulnerabilityElapsed % 4 == 0 or self.invulnerabilityElapsed % 4 == 1):
                self.image = pygame.image.load("player.png")
            else:
                self.image = pygame.image.load("blankPlayer.gif")
        elif(self.invulnerable and self.invulnerabilityElapsed >= self.invulnerabilityDuration):
            self.image = pygame.image.load("player.png")
            self.invulnerable = False
            self.invulnerabilityElapsed = 0
        
    def jump(self):
        self.dy -= GRAVITY
        if(self.dy > -JUMP_SPEED):
            self.rect.bottom -= self.dy
        else:
            self.dy = JUMP_SPEED
            self.jumping = False  
            
    def turnLeft(self):
        if(not self.facing == "left"):
            self.facing = "left"
            self.image = pygame.transform.flip(self.image, True, False)
            
    def turnRight(self):
        if(not self.facing == "right"):
            self.facing = "right"
            self.image = pygame.transform.flip(self.image, True, False)
            
    def moveRight(self):
        self.turnRight()
        self.rect.centerx += self.dx
        
    def moveLeft(self):
        self.turnLeft()
        self.rect.centerx -= self.dx
        
    def attack(self):
        self.image = pygame.image.load("player-attacking.gif")
        
    def neutral(self):
        self.image = pygame.image.load("player.png")  
        
class Lightning(pygame.sprite.Sprite):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("attackOrb1.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect() 
        self.player = player
        
        self.attacking = False
        self.attackDuration = 30 #in frames
        self.attackElapsed = 0
        
        self.fullyCharged = True
        self.attackDelay = 60 #delay between attacks
        
    def update(self):
        
        self.lightningXMax = self.player.rect.left + 100
        self.lightningXMin = self.player.rect.left  - 50
        self.lightningYMax = self.player.rect.bottom  - 25
        self.lightningYMin = self.player.rect.bottom  - 25
        
        if(self.attacking and self.attackElapsed == 0):
            self.fullyCharged = False
            self.attack()
        if(self.attackElapsed == self.attackDuration):
            self.attacking = False
            self.neutral()
        if(self.attackElapsed >= self.attackDelay):
            self.fullyCharged = True
            self.attackElapsed = 0  
        if(self.attacking or not self.fullyCharged):
            self.attackElapsed += 1
        
        self.followMouse()
        
    def followMouse(self):
        (mouseX, mouseY) = pygame.mouse.get_pos()
        self.rect.center = (mouseX * MOUSE_SENSITIVITY_FACTOR, mouseY * MOUSE_SENSITIVITY_FACTOR)
        
        if( self.rect.centerx > self.lightningXMax):
            self.rect.centerx = self.lightningXMax
        if( self.rect.centerx < self.lightningXMin):
            self.rect.centerx = self.lightningXMin
            
        if( self.rect.bottom > self.lightningYMax):
            self.rect.bottom = self.lightningYMax 
        if( self.rect.bottom < self.lightningYMin):
            self.rect.bottom = self.lightningYMin

    def attack(self):
        self.image = pygame.image.load("attackOrb2.gif")
        self.attacking = False
        
    def neutral(self):
        self.image = pygame.image.load("attackOrb1.gif")
        
class HealthBar(pygame.sprite.Sprite):
    def __init__(self, healthPercent):
        pygame.sprite.Sprite.__init__(self)
        self.level = healthPercent
        self.image = pygame.Surface((100, 10))
        self.image.fill((0, 0, 0))
        pygame.draw.rect(self.image, (0, 255, 0), [1, 1, self.level, 8])
        self.rect = self.image.get_rect()
        
        self.reset()
        
    def update(self):
        self.image.fill((0,0,0))
        if self.level > 50:
            color = (0, 255, 0)
        elif self.level > 25:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        pygame.draw.rect(self.image,color,[1, 1, self.level, 8])
        
    def reset(self):
        self.rect.left = -100
        self.rect.bottom = -100
        
                  
class Environment(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("interior-start.png")
        self.rect = self.image.get_rect()
        self.dx = SCROLL_SPEED
        
        self.atEnds = False
        
        self.reset()
        
    def update(self):
        if ((self.rect.left > 0) or (self.rect.right < (0 + SCREEN.get_width()))):
            self.atEnds = True
            self.reset()
        else:
            self.atEnds = False
            
    def reset(self):
        self.atEnds = False
        self.rect.left = 0
        
    def moveLeft(self):
        self.rect.centerx += self.dx
        
    def moveRight(self):
        self.rect.centerx -= self.dx
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, environment, player, centerx, bottom):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("enemy-passive.png")
        self.rect = self.image.get_rect()
        self.originalx = centerx
        self.originaly = bottom
        self.rect.centerx = self.originalx
        self.rect.bottom = self.originaly
        self.dx = 0
        self.environment = environment
        self.player = player
        
        self.readyToFire = True
        self.ableToFire = False
        self.fireDelay = 90 #in frames
        self.fireElapsed = 0
        
        self.dir = 180
        self.charge = 5
        
        self.damage = 5
        
        self.shell = Shell(self.environment)
            
    def update(self):
        self.dx = 0
        self.shell.update()
        
        self.followPlayer()
        
        if(self.ableToFire):
            if(self.readyToFire):
                self.fire()
        if(self.fireElapsed >= self.fireDelay):
            self.fireElapsed = 0
            self.readyToFire = True
        elif(not self.readyToFire):
            self.fireElapsed += 1
        
        if (self.environment.rect.left > 0):
            self.reset() 
            
    def followPlayer(self):
        dx = self.rect.centerx - self.player.rect.centerx
        dy = self.rect.centery - self.player.rect.centery
        dy *= -1
        
        radians = math.atan2(dy, dx)
        self.dir = radians * 180 / math.pi
        self.dir += 180
        
        #calculate distance
        self.distance = math.sqrt((dx * dx) + (dy * dy))
        
        if(self.distance < ENEMY_LOS_MAX_DISTANCE):
            self.ableToFire = True
            self.image = pygame.image.load("enemy-aggressive.png")
        else:
            self.ableToFire = False
            self.image = pygame.image.load("enemy-passive.png")
        
    def reset(self):
        self.rect.centerx = self.originalx     
        
    def moveLeft(self):
        self.dx = SCROLL_SPEED
        self.rect.centerx += self.dx

    def moveRight(self):
        self.dx = SCROLL_SPEED
        self.rect.centerx -= self.dx
        
    def fire(self):
        self.readyToFire = False
    
        self.shell.x = self.rect.centerx
        self.shell.y = self.rect.centery
        self.shell.speed = self.charge
        self.shell.dir = self.dir
        self.shell.update()
        
    def kill(self):
        self.rect.center = (-500, -500)
        
class Shell(pygame.sprite.Sprite):
    def __init__(self, environment):
        pygame.sprite.Sprite.__init__(self)
        self.environment = environment
        
        self.image = pygame.Surface((10, 10))
        self.image.fill((0xff, 0xff, 0xff))
        self.image.set_colorkey((0xff, 0xff, 0xff))
        pygame.draw.circle(self.image, (0, 0, 0), (5, 5), 5)
        self.image = pygame.transform.scale(self.image, (5, 5))
        self.rect = self.image.get_rect()
        self.rect.center = (-100, -100)
        
        self.speed = 0
        self.dir = 0
        
        self.dx = 0
        self.dy = 0
        
        self.damage = 5
        
        self.environmentMoveDir = "none"
        
        self.reset()
         
    def update(self):
        self.calcVector()
        self.calcPos()
        self.checkBounds()
        self.rect.center = (self.x, self.y)
   
    def calcVector(self):
        
        radians = self.dir * math.pi / 180
        
        self.dx = self.speed * math.cos(radians)
        self.dy = self.speed * math.sin(radians)
        self.dy *= -1
        if(self.environmentMoveDir == "left"):
            self.dx += SCROLL_SPEED
        elif(self.environmentMoveDir == "right"):
            self.dx -= SCROLL_SPEED

        self.environmentMoveDir = "none"
            
    def calcPos(self):
        self.x += self.dx
        self.y += self.dy
    
    def checkBounds(self):
        if self.x > SCREEN.get_width():
            self.reset()
        if self.x < 0:
            self.reset()
        if self.y > SCREEN.get_height():
            self.reset()
        if self.y < 0:
            self.reset()
    
    def reset(self):
        """ move off stage and stop"""
        self.x = -100
        self.y = -100
#         self.speed = 0

class Gameplay():
    def game(self):
        pygame.display.set_caption("Project 1")
        
        background = pygame.Surface(size = (800, 600))
        background.fill((0, 0, 0))
        background = background.convert()
        SCREEN.blit(background, (0, 0))
        
        player = Player()
        lightning = Lightning(player)
        environment = Environment()
        
        enemy = []
        collLightningToEnemy = []
        collEnemyToPlayer = []
        collShellToPlayer = []
        
        for i in range(NUM_OF_ENEMIES):
            enemy.append("0")
            collEnemyToPlayer.append("0")
            collShellToPlayer.append("0")
            collLightningToEnemy.append("0")
            enemy[i] = Enemy(environment, player, 1000 + (random.randrange(300, 400) + (100 * i)), random.randrange(200, 500))      
            
        #instantiate the clock
        clock = pygame.time.Clock()
        
        #the following is the primary game loop. The in-game happens within this loop
        keepGoing = True
        while keepGoing:
            pygame.mouse.set_visible(False)#hide the mouse
            clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)
            
            #if the player clicks a quit event, stop the game loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False
            
            environmentSprites = pygame.sprite.OrderedUpdates(environment)
            friendSprites = pygame.sprite.OrderedUpdates(player, lightning, player.healthBar)
            enemySprites = pygame.sprite.OrderedUpdates()

            for i in range(NUM_OF_ENEMIES):
                enemySprites.add(enemy[i], enemy[i].shell)
                
                #check collisions  
                collEnemyToPlayer[i] = pygame.sprite.collide_rect(player, enemy[i])
                collShellToPlayer[i] = pygame.sprite.collide_mask(player, enemy[i].shell)
                collLightningToEnemy[i] = pygame.sprite.collide_rect(lightning, enemy[i])
                
                if((collEnemyToPlayer[i] or collShellToPlayer[i]) and not player.invulnerable):
                    player.invulnerable = True
                    player.displayHealthElapsed = 0
                    player.displayHealth = True
                    if(collEnemyToPlayer[i]):
                        player.health -= enemy[i].damage
                    if(collShellToPlayer[i]):
                        player.health -= enemy[i].shell.damage
                        enemy[i].shell.reset()
                if(collLightningToEnemy[i] and player.attacking):
                    print("Hit enemy", i)
                    enemy[i].kill()      
                      
            keystate = pygame.key.get_pressed()
            if ((keystate[pygame.K_LEFT] or keystate[pygame.K_a]) and not environment.atEnds):
                player.turnLeft()
                environment.moveLeft()
                for i in range(NUM_OF_ENEMIES):
                    enemy[i].moveLeft()
                    enemy[i].shell.environmentMoveDir = "left"
            elif ((keystate[pygame.K_RIGHT] or keystate[pygame.K_d]) and not environment.atEnds):
                player.turnRight()
                environment.moveRight()
                for i in range(NUM_OF_ENEMIES):
                    enemy[i].moveRight()
                    enemy[i].shell.environmentMoveDir = "right"
            elif ((keystate[pygame.K_RIGHT] or keystate[pygame.K_a]) and environment.atEnds):
                player.moveLeft()
            elif ((keystate[pygame.K_RIGHT] or keystate[pygame.K_d]) and environment.atEnds):
                player.moveRight()
            if keystate[pygame.K_SPACE]:
                player.jumping = True
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if(player.fullyCharged):
                    lightning.attacking = True
                    player.attacking = True
                    
            #clear each sprite
            friendSprites.clear(SCREEN, background)
            enemySprites.clear(SCREEN, background)
            environmentSprites.clear(SCREEN, background)
    
            #update each sprite
            friendSprites.update()
            enemySprites.update()
            environmentSprites.update()
            
            #draw the sprites on the screen
            environmentSprites.draw(SCREEN)
            friendSprites.draw(SCREEN)
            enemySprites.draw(SCREEN)
            
            #flip the display
            pygame.display.flip()
            
        #return mouse cursor
        pygame.mouse.set_visible(True) 
        
        playing = "menu"
        return playing

class Menu():
    def mainMenu(self):
        
        background = pygame.Surface(size = (800, 600))
        background.fill((0, 255, 0))
        background = background.convert()
        SCREEN.blit(background, (0, 0))
        
        #instantiate the clock
        clock = pygame.time.Clock()
        
        easyButton = Buttons.Button()
        mediumButton = Buttons.Button()
        hardButton = Buttons.Button()
        quitButton = Buttons.Button()
        
        #the following is the primary game loop. The in-game happens within this loop
        playing = "menu"
                    
        while playing == "menu":
            clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)
            
            #if the player clicks a quit event, stop the game loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if easyButton.pressed(pygame.mouse.get_pos()):
                        playing = "easy"
                    elif mediumButton.pressed(pygame.mouse.get_pos()):
                        playing = "medium"
                    elif hardButton.pressed(pygame.mouse.get_pos()):
                        playing = "hard"
                    elif quitButton.pressed(pygame.mouse.get_pos()):
                        playing = "quit"
                        
            #Parameters:                surface,   color,      x,  y,  length, height, width,    text,       text_color
            easyButton.create_button(   SCREEN, (107,142, 35), 0  , 100, 75,    65,     0,      "Easy"  ,   (0, 0, 0))
            mediumButton.create_button( SCREEN, (107,142, 35), 100, 100, 75,    65,     0,      "Medium",   (0, 0, 0))
            hardButton.create_button(   SCREEN, (107,142, 35), 200, 100, 75,    65,     0,      "Hard"  ,   (0, 0, 0))
            quitButton.create_button(   SCREEN, (107,142, 35), 300, 100, 75,    65,     0,      "Quit"  ,   (0, 0, 0))
            
            
            #flip the display
            pygame.display.flip()
            
        return playing

def main():
    playing = "menu"
    
    gameplay = Gameplay()
    menu = Menu()
    
    while playing != "quit":
        if(playing == "menu"):
            playing = menu.mainMenu()
        elif(playing == "easy"):
            playing = gameplay.game()#get the score from the player's game
        else:
            playing = "quit"

if __name__ == "__main__":
    main()
