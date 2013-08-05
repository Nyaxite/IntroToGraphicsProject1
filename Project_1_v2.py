# Source File Name: Project_1.py
# Names: Michael Burnie, Evan Pugh
# Last Modified By: Michael Burnie
# Date Last Modified: August 4, 2013
""" 
  Program Description: You play as an orb of lightning. The objective is to get to the other side of 
  the level without dying. Click to attack; but be careful, after your attack has completed, you will
  need time to recharge. Enemies will shoot at you. Avoid them and their projectiles!

    Version: 2
    - Added game end screen
        - displays:
            - score
            - difficulty
        - button to move onto next difficulty if level completed
        - button to return to main menu
    - Added difficulties: easy, medium, hard
        - As difficulty increases:
            - Player is invulnerable less time after being hit
            - Player cannot attack for as long between charges
            - More enemies appear
            - Enemies do more damage
            - Enemies fire faster
            - Enemy bullet speeds increase
            - Enemies can see player from farther away
        - To come: difficulty levels will change the location
    - Added charge bar below player
        - displays current charge percentage of attack
    - Added score bonuses:
        - bonus for completing level
        - bonus for completing level without taking damage
        - bonus for completing level without attacking
        - more to come...
    - Enemy pictures updated
        - change colour when player is in line of sight and attackable
    - Dozens of constants added to make for better/easier code
    - Changed enemy start positions so that they are scalable depending on:
        - number of enemies
        - size of background
        - constants declared at start of code
    - Changed some button functionality and positions
    - Fixed player attack distance so it's equal left and right
 
"""

import pygame, os, math, random, Buttons
pygame.init()

WINDOW_POS_X = 50
WINDOW_POS_Y = 50

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (WINDOW_POS_X , WINDOW_POS_Y)

SCREEN = pygame.display.set_mode((800, 600) )#, pygame.FULLSCREEN | pygame.NOFRAME)#resolution

FRAMES_PER_SECOND = 30
MOUSE_SENSITIVITY_FACTOR = 0.8

SCROLL_SPEED = 10

GRAVITY = 1.5
JUMP_SPEED = 20

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (0, 0, 90)
MID_LOW_BLUE = (0, 0, 150)
MID_HIGH_BLUE = (0, 0, 190)
GREEN_YELLOW = (128, 255, 0)
DARK_RED = (90, 0, 0)
DARK_GREEN = (0, 90, 0)

PLAYER_LEFT_POS = 300
PLAYER_BOTTOM_POS = 500
PLAYER_MAX_HEALTH = 50
PLAYER_INVULNERABILITY_DURATION_EASY = 40
PLAYER_INVULNERABILITY_DURATION_MEDIUM = 30
PLAYER_INVULNERABILITY_DURATION_HARD = 20
PLAYER_ATTACK_DURATION_EASY = 45
PLAYER_ATTACK_DURATION_MEDIUM  = 40
PLAYER_ATTACK_DURATION_HARD = 30

NUM_OF_ENEMIES_EASY = 10
NUM_OF_ENEMIES_MEDIUM = 15
NUM_OF_ENEMIES_HARD = 20
ENEMY_LOS_MAX_DISTANCE_EASY = 200
ENEMY_LOS_MAX_DISTANCE_MEDIUM = 300
ENEMY_LOS_MAX_DISTANCE_HARD = 400
ENEMY_FIRE_DELAY_EASY = 150
ENEMY_FIRE_DELAY_MEDIUM = 90
ENEMY_FIRE_DELAY_HARD = 60
ENEMY_CHARGE_EASY = 3
ENEMY_CHARGE_MEDIUM = 5
ENEMY_CHARGE_HARD = 7
ENEMY_DAMAGE_EASY = 10
ENEMY_DAMAGE_MEDIUM = 12
ENEMY_DAMAGE_HARD = 15
ENEMY_BULLET_DAMAGE_EASY = 10
ENEMY_BULLET_DAMAGE_MEDIUM = 15
ENEMY_BULLET_DAMAGE_HARD = 20

#the +/- of the average enemy spread, determining how far apart enemies can be for X value
ENEMY_SPREAD_VARIANCE_VALUE = 20
ENEMY_SPAWN_HEIGHT_MAX = 600 #the highest (lower on screen) Y position on the screen enemies will spawn
ENEMY_SPAWN_HEIGHT_MIN = 100 #the lowest Y position on the screen enemies will spawn
ENEMY_START_X_BUFFER = 600 #the closest X distance from the left side of the environment that the enemies can spawn

SCORE_ENEMY_DEATH = 10
SCORE_BONUS_FINISH = 50
SCORE_BONUS_FULL_HEALTH = 200
SCORE_BONUS_PACIFIST = 100

SCORE_FACTOR_EASY = 1
SCORE_FACTOR_MEDIUM  = 2
SCORE_FACTOR_HARD  = 4

class Player(pygame.sprite.Sprite):
    """
    Constructor for Player Class   
    """
    def __init__(self, difficulty):
        pygame.sprite.Sprite.__init__(self)
        self.difficulty = difficulty
        self.image = pygame.image.load("player.png")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()  
        self.rect.left = PLAYER_LEFT_POS
        self.rect.bottom = PLAYER_BOTTOM_POS
        self.jumping = False
        
        self.health = PLAYER_MAX_HEALTH
        self.healthPercent = self.health / PLAYER_MAX_HEALTH * 100
        self.healthBar = StatusBar(self.healthPercent, RED, YELLOW, GREEN_YELLOW, GREEN)
        self.displayHealth = False
        self.displayHealthDuration = 60
        self.displayHealthElapsed = 0
        
        self.chargePercent = 100
        self.chargeBar = StatusBar(self.chargePercent, DARK_BLUE, MID_LOW_BLUE, MID_HIGH_BLUE, BLUE)
        
        if(self.difficulty == "easy"):
            self.invulnerabilityDuration = PLAYER_INVULNERABILITY_DURATION_EASY
            self.attackDuration = PLAYER_ATTACK_DURATION_EASY
        elif(self.difficulty == "medium"):
            self.invulnerabilityDuration = PLAYER_INVULNERABILITY_DURATION_MEDIUM
            self.attackDuration = PLAYER_ATTACK_DURATION_MEDIUM
        elif(self.difficulty == "hard"):
            self.invulnerabilityDuration = PLAYER_INVULNERABILITY_DURATION_HARD
            self.attackDuration = PLAYER_ATTACK_DURATION_HARD
            
        self.invulnerable = False
        self.invulnerabilityElapsed = 0
                
        self.attacking = False
        self.attackElapsed = 0
        
        self.fullyCharged = True
        self.attackDelay = 60 #delay between attacks
        
        self.facing = "right"
        
        self.dy = JUMP_SPEED
        self.dx = SCROLL_SPEED
        
    def update(self):
        
        self.updateHealth()#update player Health
        self.updateCharge()
        self.checkInvulnerability()#check if player has been hit, and make them invulnerable
        
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
            self.healthBar = StatusBar(self.healthPercent, RED, YELLOW, GREEN_YELLOW, GREEN)
            self.healthBar.rect.centerx = self.rect.centerx
            self.healthBar.rect.centery = self.rect.centery - 50
            self.displayHealthElapsed += 1
        elif(self.displayHealth and self.displayHealthElapsed >= self.displayHealthDuration):
            self.healthBar.reset()
            self.displayHealth = False
            self.displayHealthElapsed = 0
            
    def updateCharge(self):
        if(not self.fullyCharged):
            self.chargePercent = self.attackElapsed * 100 / self.attackDelay
            self.chargeBar = StatusBar(self.chargePercent, DARK_BLUE, MID_LOW_BLUE, MID_HIGH_BLUE, BLUE)
            self.chargeBar.rect.centerx = self.rect.centerx
            self.chargeBar.rect.centery = self.rect.centery + 50
        else:
            self.chargeBar.reset()
            
    def checkInvulnerability(self):
        if(self.invulnerable and self.invulnerabilityElapsed < self.invulnerabilityDuration):
            self.invulnerabilityElapsed += 1 
            if(self.invulnerabilityElapsed % 4 == 0 or self.invulnerabilityElapsed % 4 == 1):
                if(self.attacking):
                    self.attack()
                else:
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
        
        self.lightningXMax = self.player.rect.right + 50
        self.lightningXMin = self.player.rect.left  - 50
        self.lightningYMax = self.player.rect.bottom  - 30
        self.lightningYMin = self.player.rect.bottom  - 30
        
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
        self.rect.center = (mouseX * MOUSE_SENSITIVITY_FACTOR, self.lightningYMax)
        
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
        
class StatusBar(pygame.sprite.Sprite):
    def __init__(self, statusPercent, lowColor, midLowColor, midHighColor, highColor):
        pygame.sprite.Sprite.__init__(self)
        self.level = statusPercent
        self.lowColor = lowColor
        self.midLowColor = midLowColor
        self.midHighColor = midHighColor
        self.highColor = highColor
        self.image = pygame.Surface((100, 10))
        self.image.fill((0, 0, 0))
        pygame.draw.rect(self.image, (0, 255, 0), [1, 1, self.level, 8])
        self.rect = self.image.get_rect()
        
        self.reset()
        
    def update(self):
        self.image.fill((0,0,0))
        if self.level > 75:
            color = self.highColor
        elif self.level > 50:
            color = self.midHighColor
        elif self.level > 25:
            color = self.midLowColor
        else:
            color = self.lowColor
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
        self.atEnd = False
        
        self.reset()
        
#     def update(self):
#         if ((self.rect.left > 0) or (self.rect.right < (0 + SCREEN.get_width()))):
#             self.reset
            
    def reset(self):
        self.rect.left = 0
        
    def moveLeft(self):
        if not (self.rect.left > 10):
            self.rect.centerx += self.dx
        
    def moveRight(self):
        if not (self.rect.right < (0 + SCREEN.get_width())):
            self.rect.centerx -= self.dx
        else:
            self.atEnd = True
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, difficulty, environment, player, centerx, bottom):
        pygame.sprite.Sprite.__init__(self)
        self.difficulty = difficulty
        self.environment = environment
        self.player = player
        
        self.image = pygame.image.load("enemy1-passive.gif")
        self.rect = self.image.get_rect()
        self.originalx = centerx
        self.originaly = bottom
        self.rect.centerx = self.originalx
        self.rect.bottom = self.originaly
        self.dx = 0
        
        if(self.difficulty == "easy"):
            self.fireDelay = ENEMY_FIRE_DELAY_EASY
            self.charge = ENEMY_CHARGE_EASY
            self.damage = ENEMY_DAMAGE_EASY
            self.LOSMaxDistance = ENEMY_LOS_MAX_DISTANCE_EASY
        elif(self.difficulty == "medium"):
            self.fireDelay = ENEMY_FIRE_DELAY_MEDIUM
            self.charge = ENEMY_CHARGE_MEDIUM
            self.damage = ENEMY_DAMAGE_MEDIUM
            self.LOSMaxDistance = ENEMY_LOS_MAX_DISTANCE_MEDIUM
        elif(self.difficulty == "hard"):
            self.fireDelay = ENEMY_FIRE_DELAY_HARD
            self.charge = ENEMY_CHARGE_HARD
            self.damage = ENEMY_DAMAGE_HARD
            self.LOSMaxDistance = ENEMY_LOS_MAX_DISTANCE_HARD

        self.readyToFire = True
        self.ableToFire = False
        self.fireElapsed = 0
        self.dir = 180
        self.shell = Shell(self.difficulty, self.environment)
            
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
        
        if(self.distance < self.LOSMaxDistance):
            self.ableToFire = True
            self.image = pygame.image.load("enemy1-aggressive.gif")
        else:
            self.ableToFire = False
            self.image = pygame.image.load("enemy1-passive.gif")
        
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
    def __init__(self, difficulty, environment):
        pygame.sprite.Sprite.__init__(self)
        self.difficulty = difficulty
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
        
        if(self.difficulty == "easy"):
            self.damage = ENEMY_BULLET_DAMAGE_EASY
        elif(self.difficulty == "medium"):
            self.damage = ENEMY_BULLET_DAMAGE_MEDIUM
        elif(self.difficulty == "hard"):
            self.damage = ENEMY_BULLET_DAMAGE_HARD
        
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
    def game(self, difficulty, score):
        pygame.display.set_caption("Project 1")
        
        background = pygame.Surface(size = (800, 600))
        background.fill((0, 0, 0))
        background = background.convert()
        SCREEN.blit(background, (0, 0))
        
        previousScore = score
        score = 0
        
        player = Player(difficulty)
        lightning = Lightning(player)
        environment = Environment()
        
        enemiesKilled = 0
        
        enemy = []
        collLightningToEnemy = []
        collEnemyToPlayer = []
        collShellToPlayer = []
        
        if(difficulty == "easy"):
            numberOfEnemies = NUM_OF_ENEMIES_EASY
        elif(difficulty == "medium"):
            numberOfEnemies = NUM_OF_ENEMIES_MEDIUM
        elif(difficulty == "hard"):
            numberOfEnemies = NUM_OF_ENEMIES_HARD
            
        averageEnemySpread = (environment.rect.right - ENEMY_START_X_BUFFER) / numberOfEnemies
        
        for i in range(numberOfEnemies):
            enemy.append("0")
            collEnemyToPlayer.append("0")
            collShellToPlayer.append("0")
            collLightningToEnemy.append("0")
            #The following creates the enemies and determines where they are placed in the level
            enemyStartX = ENEMY_START_X_BUFFER + i * (random.randrange(averageEnemySpread - ENEMY_SPREAD_VARIANCE_VALUE, averageEnemySpread + ENEMY_SPREAD_VARIANCE_VALUE))   
            enemyStartY = random.randrange(ENEMY_SPAWN_HEIGHT_MIN, ENEMY_SPAWN_HEIGHT_MAX)
            enemy[i] = Enemy(difficulty, environment, player, enemyStartX, enemyStartY)
            
        #instantiate the clock
        clock = pygame.time.Clock()
        
        #the following is the primary game loop. The in-game happens within this loop
        keepGoing = True
        while keepGoing:
            pygame.mouse.set_visible(False)#hide the mouse
            clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)
            
            environmentSprites = pygame.sprite.OrderedUpdates(environment)
            friendSprites = pygame.sprite.OrderedUpdates(player, lightning, player.healthBar, player.chargeBar)
            enemySprites = pygame.sprite.OrderedUpdates()

            for i in range(numberOfEnemies):
                enemySprites.add(enemy[i], enemy[i].shell)
                
                #check collisions  
                collEnemyToPlayer[i] = pygame.sprite.collide_mask(player, enemy[i])
                collShellToPlayer[i] = pygame.sprite.collide_mask(player, enemy[i].shell)
                collLightningToEnemy[i] = pygame.sprite.collide_mask(lightning, enemy[i])
                
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
                    score += SCORE_ENEMY_DEATH
                    enemiesKilled += 1
                    enemy[i].kill()      
                      
            keystate = pygame.key.get_pressed()
            if (keystate[pygame.K_LEFT] or keystate[pygame.K_a]):
                player.turnLeft()
                environment.moveLeft()
                for i in range(numberOfEnemies):
                    enemy[i].moveLeft()
                    enemy[i].shell.environmentMoveDir = "left"
            elif (keystate[pygame.K_RIGHT] or keystate[pygame.K_d]):
                player.turnRight()
                environment.moveRight()
                for i in range(numberOfEnemies):
                    enemy[i].moveRight()
                    enemy[i].shell.environmentMoveDir = "right"
            if keystate[pygame.K_SPACE]:
                player.jumping = True
                
            #if the player clicks a quit event, stop the game loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if(player.fullyCharged):
                        lightning.attacking = True
                        player.attacking = True
                        
            if environment.atEnd or player.health <= 0:
                if(player.health <= 0):
                    playing = "gameOver"
                else:
                    playing = "endGame"
                    score += SCORE_BONUS_FINISH #add a bonus to play score if they finished the level
                    
                    #add bonus score if the player finished with full health
                    if(player.health == PLAYER_MAX_HEALTH):
                        score += SCORE_BONUS_FULL_HEALTH
                        
                    #add bonus score if the player kills no enemies
                    if(enemiesKilled == 0):
                        score += SCORE_BONUS_PACIFIST
                
                
                #multiply the score by the factor for the given difficulty, for this level only
                if(difficulty == "easy"):
                    score *= SCORE_FACTOR_EASY
                elif(difficulty == "medium"):
                    score *= SCORE_FACTOR_MEDIUM
                elif(difficulty == "hard"):
                    score *= SCORE_FACTOR_EASY
                
                score += previousScore #add the score the user had from previous levels
                
                keepGoing = False
                #return mouse cursor
                pygame.mouse.set_visible(True) 
                return playing, score
                    
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
        return playing, score
    
class Menu():
    def __init__(self):        
        self.easyButton = Buttons.Button()
        self.mediumButton = Buttons.Button()
        self.hardButton = Buttons.Button()
        self.quitButton = Buttons.Button()
        
        self.returnToMenuButton = Buttons.Button()
        self.nextLevelButton = Buttons.Button()
        
        #instantiate the clock
        self.clock = pygame.time.Clock()

    def mainMenu(self):
        
        background = pygame.Surface(size = (800, 600))
        background.fill(BLACK)
        background = background.convert()
        SCREEN.blit(background, (0, 0))
        
        playing = "menu"
        while playing == "menu":
            self.clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)
            
            #if the player clicks a quit event, stop the game loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.easyButton.pressed(pygame.mouse.get_pos()):
                        playing = "easy"
                    elif self.mediumButton.pressed(pygame.mouse.get_pos()):
                        playing = "medium"
                    elif self.hardButton.pressed(pygame.mouse.get_pos()):
                        playing = "hard"
                    elif self.quitButton.pressed(pygame.mouse.get_pos()):
                        playing = "quit"
                        
            #Parameters:                surface,   color,            x,  y,  length, height, width,    text,       text_color
            self.easyButton.create_button(   SCREEN, DARK_GREEN, 100, 200, 200,    75,     0,      "Easy"  ,   WHITE)
            self.mediumButton.create_button( SCREEN, DARK_BLUE, 100, 325, 200,    75,     0,      "Medium",   WHITE)
            self.hardButton.create_button(   SCREEN, DARK_RED, 100, 450, 200,    75,     0,      "Hard"  ,   WHITE)
            self.quitButton.create_button(   SCREEN, RED, 690, 10, 100,    40,     0,      "Exit Game"  ,   WHITE)

            #flip the display
            pygame.display.flip()
            
        return playing
    
    def endMenu(self, score, playing, difficulty):
        
        background = pygame.Surface(size = (800, 600))
        background.fill(BLACK)
        background = background.convert()
        SCREEN.blit(background, (0, 0))

        #message strings for end game screen
        gameOverMessage = "Game Over!"
        gameEndMessage = "Level Complete!"
        scoreMessage = "Score: %d" % score
        difficultyMessage = "Difficulty: %s" % difficulty
        insBigFont = pygame.font.SysFont(None, 36)  

        while playing == "endGame" or playing == "gameOver":
            self.clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)
            
            #if the player clicks a quit event, stop the game loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.returnToMenuButton.pressed(pygame.mouse.get_pos()):
                        playing = "menu"
                    elif self.nextLevelButton.pressed(pygame.mouse.get_pos()):
                        if(difficulty == "easy"):
                            playing = "medium"
                        elif(difficulty == "medium"):
                            playing = "hard"
                        elif(difficulty == "hard"):
                            playing = "hard"
                    elif self.quitButton.pressed(pygame.mouse.get_pos()):
                        playing = "quit"
            
                        #Parameters:                surface,   color,        x,  y,  length, height, width,    text,               text_color
            self.returnToMenuButton.create_button(  SCREEN, DARK_RED,       100, 325, 200,      75,   0,        "Return to Menu",   WHITE)
            self.nextLevelButton.create_button(     SCREEN, DARK_GREEN,     -200, -300, 10,     10,   0,        "Next",             WHITE) 
            self.quitButton.create_button(          SCREEN, RED,            690, 10, 100,       40,   0,         "Exit Game"  ,     WHITE)
                
            if(playing == "endGame"):
                self.nextLevelButton.create_button( SCREEN, DARK_GREEN, 100, 200, 200,    75,     0,      "Next Level",       WHITE) 
                SCREEN.blit(insBigFont.render(gameEndMessage, True, WHITE),(10, 10))
            elif(playing == "gameOver"):  
                SCREEN.blit(insBigFont.render(gameOverMessage, True, WHITE),(10, 10))
                
            SCREEN.blit(insBigFont.render(scoreMessage, True, WHITE),(10, 50))
            SCREEN.blit(insBigFont.render(difficultyMessage, True, WHITE),(10, 100))

            #flip the display
            pygame.display.flip()
            
        return playing

def main():
    playing = "menu"
    
    gameplay = Gameplay()
    menu = Menu()
    score = 0
    
    while playing != "quit":
        if(playing == "menu"):
            playing = menu.mainMenu()
        elif(playing == "easy"):
            difficulty = "easy"
            playing, score = gameplay.game(difficulty, score)
        elif(playing == "medium"):
            difficulty = "medium"
            playing, score = gameplay.game(difficulty, score)
        elif(playing == "hard"):
            difficulty = "hard"
            playing, score = gameplay.game(difficulty, score)
        elif(playing == "endGame" or playing == "gameOver"):
                
            playing = menu.endMenu(score, playing, difficulty)
            
            #reset the score if the game has ended
            if(playing == "menu"):
                score = 0
            
        else:
            playing = "quit"

if __name__ == "__main__":
    main()
