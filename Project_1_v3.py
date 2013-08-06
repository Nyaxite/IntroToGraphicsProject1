# Source File Name: Project_1.py
# Names: Michael Burnie, Evan Pugh
# Last Modified By: Evan Pugh
# Date Last Modified: August 5, 2013
""" 
  Program Description: You play as an orb of lightning. The objective is to get to the other side of 
  the level without dying. Click to attack; but be careful, after your attack has completed, you will
  need time to recharge. Enemies will shoot at you. Avoid them and their projectiles!

    Version: 3
    - In game Scoreboard added
    - included delay on first enemy attack
    - Added sounds, music
    - Added pickup item that increases player score
        - spawns in center of level
    - Added two new environments which get progressively longer:
        - medium: polygonal rainbow road
        - hard: space
    - alternating enemy colours/sizes
    - overall optimization of code, not sending in full objects, but rather variables

"""

import pygame, os, math, random, Buttons
pygame.init()

'''
List of constants
'''

#if windowed, start the screen close to the top left corner
WINDOW_POS_X = 50
WINDOW_POS_Y = 50
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (WINDOW_POS_X , WINDOW_POS_Y)

SCREEN = pygame.display.set_mode((800, 600) , pygame.FULLSCREEN | pygame.NOFRAME)#resolution

FRAMES_PER_SECOND = 30 #frames per second
MOUSE_SENSITIVITY_FACTOR = 0.8 #mouse sensitivity factor which can be used to increase or decrease mouse sensitivity

SCROLL_SPEED = 10 #scroll speed of the game. This is basically how fast the player moves when they move

GRAVITY = 1.5 #gravity value required for jumping
JUMP_SPEED = 20 #dy value of the player when they first initiate a jump

#various colour values used throughout
RED =           (255, 0  , 0  )
GREEN =         (0  , 255, 0  )
BLUE =          (0  , 0  , 255)
YELLOW =        (255, 255, 0  )
BLACK =         (0  , 0  , 0  )
WHITE =         (255, 255, 255)
DARK_BLUE =     (0  , 0  , 90 )
MID_LOW_BLUE =  (0  , 0  , 150)
MID_HIGH_BLUE = (0  , 0  , 190)
GREEN_YELLOW =  (128, 255, 0  )
DARK_RED =      (90 , 0  , 0  )
DARK_GREEN =    (0  , 90 , 0  )

#constants for player. Some are affected by difficulty, in which multiple constants are made. Numbers represent the number of frames
PLAYER_LEFT_POS = 300
PLAYER_BOTTOM_POS = 500
PLAYER_MAX_HEALTH = 50
PLAYER_INVULNERABILITY_DURATION_EASY = 40
PLAYER_INVULNERABILITY_DURATION_MEDIUM = 30
PLAYER_INVULNERABILITY_DURATION_HARD = 20
PLAYER_ATTACK_DURATION_EASY = 45
PLAYER_ATTACK_DURATION_MEDIUM  = 40
PLAYER_ATTACK_DURATION_HARD = 30

LIGHTNING_X_MAX_FROM_PLAYER = 100

#constants for enemies. Some are affected by difficulty, in which multiple constants are made. Numbers represent the number of frames
NUM_OF_ENEMIES_EASY = 10
NUM_OF_ENEMIES_MEDIUM = 15
NUM_OF_ENEMIES_HARD = 20
ENEMY_LOS_MAX_DISTANCE_EASY = 200  #line of sight
ENEMY_LOS_MAX_DISTANCE_MEDIUM = 300
ENEMY_LOS_MAX_DISTANCE_HARD = 400
ENEMY_FIRE_RESPONSE_TIME = 20  #number of frames for the enemy to begin firing after player is 'seen'
ENEMY_FIRE_DELAY_EASY = 150  #time between enemy shots
ENEMY_FIRE_DELAY_MEDIUM = 90
ENEMY_FIRE_DELAY_HARD = 60
ENEMY_CHARGE_EASY = 4  #speed of enemy bullets
ENEMY_CHARGE_MEDIUM = 5
ENEMY_CHARGE_HARD = 6
ENEMY_DAMAGE_EASY = 10  #damage taken by player if in contact with enemy
ENEMY_DAMAGE_MEDIUM = 12
ENEMY_DAMAGE_HARD = 15
ENEMY_BULLET_DAMAGE_EASY = 10  #damage taken by player if in contact with enemy's bullet
ENEMY_BULLET_DAMAGE_MEDIUM = 15
ENEMY_BULLET_DAMAGE_HARD = 20

ENEMY_SPREAD_VARIANCE_VALUE = 20  #the +/- of the average enemy spread, determining how far apart enemies can be for X value
ENEMY_SPAWN_HEIGHT_MAX = 550 #the highest (lower on screen) Y position on the screen enemies will spawn
ENEMY_SPAWN_HEIGHT_MIN = 200 #the lowest Y position on the screen enemies will spawn
ENEMY_START_X_BUFFER = 600 #the closest X distance from the left side of the environment that the enemies can spawn

#score constants, values in score
SCORE_ENEMY_DEATH = 10 #score for killing enemy
SCORE_BONUS_PICKUP = 30 #score for picking up bonus pickup
SCORE_BONUS_FINISH = 50 #score for finishing the game
SCORE_BONUS_FULL_HEALTH = 200 #score for finishing with full health
SCORE_BONUS_PACIFIST = 100 #score for beating game without killing enemies

#score multipliers awarded once the game ends. Depending on the difficulty, the player's score will be multiplied by the following values
SCORE_FACTOR_EASY = 1
SCORE_FACTOR_MEDIUM  = 2
SCORE_FACTOR_HARD  = 4

#game volume
MUSIC_VOLUME = 0.1
SOUND_VOLUME = 0.7

class Player(pygame.sprite.Sprite):
    ''' The player class involves all of the functions and values of the player that is controlled by the user.'''
    def __init__(self, difficulty):
        pygame.sprite.Sprite.__init__(self)
        self.difficulty = difficulty #read the difficulty
        
        #create player image
        self.image = pygame.image.load("player.png")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        
        #set player location  
        self.rect.left = PLAYER_LEFT_POS
        self.rect.bottom = PLAYER_BOTTOM_POS
        
        self.jumping = False #is player jumping
        
        #set player health, and create healthBar sprite
        self.health = PLAYER_MAX_HEALTH
        self.healthPercent = self.health / PLAYER_MAX_HEALTH * 100
        self.healthBar = StatusBar(self.healthPercent, RED, YELLOW, GREEN_YELLOW, GREEN)
        self.displayHealth = False  #don't display the health bar
        self.displayHealthDuration = 60 #after this many frames without taking damage, the healthbar will disappear again if shown
        self.displayHealthElapsed = 0
        
        #create charge bar for player attacks
        self.chargePercent = 100
        self.chargeBar = StatusBar(self.chargePercent, DARK_BLUE, MID_LOW_BLUE, MID_HIGH_BLUE, BLUE)
        
        #change values for player depending on difficulty
        if(self.difficulty == "easy"):
            self.invulnerabilityDuration = PLAYER_INVULNERABILITY_DURATION_EASY #duration of invulnerability when hit
            self.attackDuration = PLAYER_ATTACK_DURATION_EASY #duration of attack after initiation of attack
        elif(self.difficulty == "medium"):
            self.invulnerabilityDuration = PLAYER_INVULNERABILITY_DURATION_MEDIUM
            self.attackDuration = PLAYER_ATTACK_DURATION_MEDIUM
        elif(self.difficulty == "hard"):
            self.invulnerabilityDuration = PLAYER_INVULNERABILITY_DURATION_HARD
            self.attackDuration = PLAYER_ATTACK_DURATION_HARD
        
        self.invulnerable = False #is player invulnerable
        self.invulnerabilityElapsed = 0
                
        self.attacking = False #is player attacking
        self.attackElapsed = 0
        
        self.fullyCharged = True #is player fully charged to attack
        self.attackDelay = 60 #delay between attacks
        
        self.facing = "right" #current facing for player
        
        #setup in-game sound setup
        if not pygame.mixer:
            print("problem with sound")
        else:
            pygame.mixer.init()
            
            self.sndPlayerHurt = pygame.mixer.Sound("playerHurt.ogg")
            self.sndPlayerAttack = pygame.mixer.Sound("playerAttack.ogg")
            
            #set the volume and make adjustments from default for given sounds if required
            self.sndPlayerHurt.set_volume(SOUND_VOLUME)
            self.sndPlayerAttack.set_volume(SOUND_VOLUME)
        
        self.dy = JUMP_SPEED
        self.dx = SCROLL_SPEED
    def update(self):
        ''' The update method is called once per frame, which performs multiple actions. ''' 
        self.updateHealth()#update player Health
        self.updateCharge()#update player's charge
        self.checkAttack()#check player attack status
        self.checkInvulnerability()#check if player has been hit, and make them invulnerable
        
        if(self.jumping):#if the player is set to jump, initiate jump method
            self.jump()

    def checkAttack(self):
        ''' The various stages of attack: If the player is attacking and the attackingElapsed is < duration,
        the player can kill enemies. Otherwise, the player is charging for the next attack, and will be ready
        to attack later. '''
        if(self.attacking and self.attackElapsed == 0): #is attacking
            self.fullyCharged = False
            self.attack()
        if(self.attacking or not self.fullyCharged): #charge for next attack
            self.attackElapsed += 1 
        if(self.attackElapsed == self.attackDuration): #is neutral, charging
            self.attacking = False
            self.neutral()
        if(self.attackElapsed >= self.attackDelay): #is fully charged again
            self.fullyCharged = True
            self.attackElapsed = 0  

    def updateHealth(self):
        ''' Update the current health status for the player. This updates the health bar to show the player's
        current health. This bar is only displayed after the player has been hit for a specific number
        of frames. After that, it disappears, but continues to keep track of the player's health. '''
        if(self.displayHealth and self.displayHealthElapsed < self.displayHealthDuration):
            #show and update the health bar
            self.healthPercent = self.health * 100 / PLAYER_MAX_HEALTH
            self.healthBar = StatusBar(self.healthPercent, RED, YELLOW, GREEN_YELLOW, GREEN) #recreate healthbar object
            #position the health bar above the player
            self.healthBar.rect.centerx = self.rect.centerx
            self.healthBar.rect.centery = self.rect.centery - 50
            self.displayHealthElapsed += 1 #keep track of how long the health bar has been displayed
        elif(self.displayHealth and self.displayHealthElapsed >= self.displayHealthDuration): 
            #hide the health bar
            self.healthBar.reset()
            self.displayHealth = False
            self.displayHealthElapsed = 0
    
    def updateCharge(self):
        ''' Similar to the updateHealth function, this method keeps track of, and displays the current player's charge percent.
        The charge bar is displayed below the player. The player can attack again once the charge bar is at its peak or disappears.'''        
        if(not self.fullyCharged):
            #show charge bar and update charge percentage
            self.chargePercent = self.attackElapsed * 100 / self.attackDelay
            self.chargeBar = StatusBar(self.chargePercent, DARK_BLUE, MID_LOW_BLUE, MID_HIGH_BLUE, BLUE)
            #display chargebar below player
            self.chargeBar.rect.centerx = self.rect.centerx
            self.chargeBar.rect.centery = self.rect.centery + 50
        else:
            #hide the charge bar
            self.chargeBar.reset()
            
    def checkInvulnerability(self):
        ''' Check the current invulnerability state of the player. Invulnerability occurs when player has been hit
        by an enemy. Invulnerability only occurs briefly. '''
        if(self.invulnerable and self.invulnerabilityElapsed < self.invulnerabilityDuration):
            self.invulnerabilityElapsed += 1 #keep track of how long the player has been invulnerable
            
            #flash the images to show that the player has been hit
            if(self.invulnerabilityElapsed % 4 == 0 or self.invulnerabilityElapsed % 4 == 1):
                if(self.attacking):#check if player is attacking so it knows which images to flash
                    self.attack()
                else:
                    self.image = pygame.image.load("player.png")
            else:
                self.image = pygame.image.load("blankPlayer.gif")
        elif(self.invulnerable and self.invulnerabilityElapsed >= self.invulnerabilityDuration):
            if(self.attacking):#check if player is attacking so it knows which images to flash
                self.attack()
            else:
                self.image = pygame.image.load("player.png")
            self.invulnerable = False #make player no longer invulnerable
            self.invulnerabilityElapsed = 0
        
    def jump(self):
        ''' This method moves the player up on the screen once they jump, and a gravity-like value acts against them. '''
        self.dy -= GRAVITY
        if(self.dy > -JUMP_SPEED): #player is in the air
            self.rect.bottom -= self.dy
        else: #player has landed
            self.dy = JUMP_SPEED
            self.jumping = False  
    
    ''' The following 2 methods are called when the player uses the keyboard to move.
    This will turn the player left and right by flipping the image '''       
    def turnLeft(self):
        if(not self.facing == "left"):
            self.facing = "left"
            self.image = pygame.transform.flip(self.image, True, False)
            
    def turnRight(self):
        if(not self.facing == "right"):
            self.facing = "right"
            self.image = pygame.transform.flip(self.image, True, False)
    
    def attack(self):
        ''' This method is called when the player clicks, or is attacking '''
        self.image = pygame.image.load("player-attacking.gif") #change the image so it looks like the player is attacking
        self.sndPlayerAttack.play()
    
    def neutral(self):
        ''' This method defines the neutral/passive/not-attacking state ''' 
        self.image = pygame.image.load("player.png")  #change the image back to the neutral state
       
class Lightning(pygame.sprite.Sprite):
    '''The lightning class represents the player's attack. Lightning is used to destroy enemies. It is controlled
    with the mouse. Some of its functions reflect the Player class' functions. '''
    def __init__(self, difficulty):
        pygame.sprite.Sprite.__init__(self)
        #setup the image
        self.image = pygame.image.load("attackOrb1.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect() 
        self.difficulty = difficulty
        
        #instantiate player position, required for following player
        self.playerPosX = 0
        self.playerPosY = 0

        #lightning attack values
        self.attacking = False
        self.attackElapsed = 0
        self.attackDelay = 60 #delay between attacks
        
        #change values for lightning depending on difficulty
        if(self.difficulty == "easy"):
            self.attackDuration = PLAYER_ATTACK_DURATION_EASY #duration of attack after initiation of attack
        elif(self.difficulty == "medium"):
            self.attackDuration = PLAYER_ATTACK_DURATION_MEDIUM
        elif(self.difficulty == "hard"):
            self.attackDuration = PLAYER_ATTACK_DURATION_HARD
        
        self.fullyCharged = True #if fully charged, lightning can attack
        
    def update(self):
        ''' The update method is called once per frame, which performs multiple actions. '''
        
        #set the maximum distances the lightning can be from the player at any given time
        #i.e. 'reach' of lightning
        self.lightningXMax = self.playerPosX + LIGHTNING_X_MAX_FROM_PLAYER
        self.lightningXMin = self.playerPosX - LIGHTNING_X_MAX_FROM_PLAYER
        self.lightningYMax = self.playerPosY
        self.lightningYMin = self.playerPosY
        
        if(self.attacking and self.attackElapsed == 0): #attack
            self.fullyCharged = False
            self.attack()
        if(self.attacking or not self.fullyCharged): #charge increment
            self.attackElapsed += 1
        if(self.attackElapsed == self.attackDuration): #charging, not attacking
            self.attacking = False
            self.neutral()
        if(self.attackElapsed >= self.attackDelay): #fully charged
            self.fullyCharged = True
            self.attackElapsed = 0  
        
        #call the follow mouse method
        self.followMouse()
    
    def followMouse(self):
        ''' This method follow's the mouse of the player, and restricts lightning movement '''
        (mouseX, mouseY) = pygame.mouse.get_pos() #get the mouse position
        self.rect.center = (mouseX * MOUSE_SENSITIVITY_FACTOR, self.lightningYMax) #set the center of lightning to mouse, multiplied by sensitivity factor
        
        #check that the lightning maximum X and Y values are not exceeded by mouse movements
        if( self.rect.centerx > self.lightningXMax):
            self.rect.centerx = self.lightningXMax
        if( self.rect.centerx < self.lightningXMin):
            self.rect.centerx = self.lightningXMin
            
        if( self.rect.centery > self.lightningYMax):
            self.rect.centery = self.lightningYMax 
        if( self.rect.centery < self.lightningYMin):
            self.rect.centery = self.lightningYMin
            
    def attack(self):
        ''' This method is called when the player clicks, or is attacking ''' 
        self.image = pygame.image.load("attackOrb2.gif")
        self.attacking = False
    
    def neutral(self):
        ''' This method defines the neutral/passive/not-attacking state ''' 
        self.image = pygame.image.load("attackOrb1.gif")


class StatusBar(pygame.sprite.Sprite):
    '''The status bar class creates sprites that are used to display status, such as health and charge, for the player'''       
    def __init__(self, statusPercent, lowColor, midLowColor, midHighColor, highColor):
        pygame.sprite.Sprite.__init__(self)
        self.level = statusPercent #current percent value
        #get color values for low, mid-low, mid-high, and high amounts
        self.lowColor = lowColor 
        self.midLowColor = midLowColor
        self.midHighColor = midHighColor
        self.highColor = highColor
        
        #define the image, using rectangle shape
        self.image = pygame.Surface((100, 10))#create the background
        self.image.fill((0, 0, 0))
        pygame.draw.rect(self.image, (0, 255, 0), [1, 1, self.level, 8])#create the bar
        self.rect = self.image.get_rect()
        
        self.reset()
    
    def update(self):
        ''' The update method is called once per frame, which performs multiple actions. '''
        self.image.fill((0,0,0))#create the background
        
        #change the colour of the bar depending on current percentage value
        if self.level > 75: #if > 75%
            color = self.highColor
        elif self.level > 50: #if > 50%
            color = self.midHighColor
        elif self.level > 25: #if > 25%
            color = self.midLowColor
        else: #if < 25%
            color = self.lowColor
        pygame.draw.rect(self.image,color,[1, 1, self.level, 8]) #create the bar
        
    def reset(self):
        ''' The reset method puts the bar object off the screen, so it is not visible '''
        self.rect.left = -100
        self.rect.bottom = -100        

class Pickup(pygame.sprite.Sprite):
    ''' The Pickup class defines objects the player can pick up, often beneficial. '''
    def __init__(self, startx, starty):
        pygame.sprite.Sprite.__init__(self)
        #create the image
        self.image = pygame.image.load("pickup.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        
        #set the start X and Y values to the ones sent in
        self.rect.centerx = startx
        self.rect.centery = starty
        
    def reset(self):
        ''' Display the pickup off screen, usually after it has been collected '''
        self.rect.center = (-100, -100)
        
    def moveLeft(self):
        ''' Move the object left on the screen, called as the environment moves '''
        self.dx = SCROLL_SPEED
        self.rect.centerx += self.dx

    def moveRight(self):
        ''' Move the object right on the screen, called as the environment moves '''
        self.dx = SCROLL_SPEED
        self.rect.centerx -= self.dx

class Scoreboard(pygame.sprite.Sprite):
    ''' The scoreboard class controls the score for the player '''
    def __init__(self, score):
        pygame.sprite.Sprite.__init__(self)
        self.score = score #read in and instantiate score
        self.font = pygame.font.SysFont("None", 60)
    
    def update(self):
        ''' The update method is called once per frame, which performs multiple actions. '''
        #display text on the screen
        self.text = "Score: %d" % (self.score)
        self.image = self.font.render(self.text, 1, RED)
        self.rect = self.image.get_rect()

class Environment(pygame.sprite.Sprite):
    ''' The Environment class defines the scene or background for the level.
    The levels change depending on difficulty. '''
    def __init__(self, difficulty):
        pygame.sprite.Sprite.__init__(self)
        
        #setup background images
        #depending on difficulty, select corresponding level
        if(difficulty == "easy"):
            self.image = pygame.image.load("level-1.png")
        elif(difficulty == "medium"):
            self.image = pygame.image.load("level-2.png")
        elif(difficulty == "hard"):
            self.image = pygame.image.load("level-3.png")
        self.rect = self.image.get_rect()
        self.dx = SCROLL_SPEED
        
        self.atEnd = False #variable to define if the player has made it to the end of the level
        
        self.reset()
    
    def reset(self):
        ''' Reset the environment back to default position '''
        self.rect.left = 0
        
    
    def moveLeft(self):
        ''' Move the environment left. '''
        #check that the player hasn't moved to the far left
        if not (self.rect.left > 0):
            self.rect.centerx += self.dx
    
    def moveRight(self):
        ''' Move the environment right. ''' 
        #check that the player hasn't moved to the far right
        if not (self.rect.right < (0 + SCREEN.get_width())):
            self.rect.centerx -= self.dx
        else:
            self.atEnd = True
       
class Enemy(pygame.sprite.Sprite):
    '''The enemy class defines everything about the enemies for the player. Enemies shoot at the player.
    They can be killed if they come in contact with Lightning when the player is attacking. '''
    def __init__(self, difficulty, centerx, bottom):
        pygame.sprite.Sprite.__init__(self)
        self.difficulty = difficulty #read in the difficulty
        self.environmentLeft = 0 
        self.playerPosX = 0
        self.playerPosY = 0
        
        #setup the image, which is randomized between different enemy images
        self.enemyType = random.randint(1, 3)
        self.enemyTypePassiveStr = "enemy%i-passive.gif" % self.enemyType
        self.enemyTypeAggressiveStr = "enemy%i-aggressive.gif" % self.enemyType
        self.image = pygame.image.load(self.enemyTypePassiveStr)
        
        #set starting coordinates, which are sent in
        self.rect = self.image.get_rect()
        self.originalx = centerx
        self.originaly = bottom
        self.rect.centerx = self.originalx
        self.rect.bottom = self.originaly
        self.dx = 0
        
        #Setup variables for how powerful the enemy is, based on constants set by difficulty
        if(self.difficulty == "easy"):
            self.fireDelay = ENEMY_FIRE_DELAY_EASY #delay between attacks
            self.charge = ENEMY_CHARGE_EASY #speed of projectiles
            self.damage = ENEMY_DAMAGE_EASY #damage if player collides with enemy
            self.LOSMaxDistance = ENEMY_LOS_MAX_DISTANCE_EASY #line of sight distance
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

        #determine other mechanics for firing
        self.readyToFire = True #is fully charged to fire
        self.ableToFire = False #is player in range 
        self.fireElapsed = 0
        self.responseElapsed = 0
        self.dir = 180
        
        self.shell = Shell(self.difficulty) #create a shell object for each enemy
        
        #setup in-game sound setup
        if not pygame.mixer:
            print("problem with sound")
        else:
            pygame.mixer.init()
            
            self.sndEnemyDeath = pygame.mixer.Sound("enemyDeath.ogg")
            self.sndEnemyAttack = pygame.mixer.Sound("enemyAttack.ogg")
            self.sndClickSound = pygame.mixer.Sound("clickSound.ogg")
            
            #set the volume and make adjustments from default for given sounds if required
            self.sndEnemyDeath.set_volume(SOUND_VOLUME)
            self.sndEnemyAttack.set_volume(SOUND_VOLUME + 0.5)
            self.sndClickSound.set_volume(SOUND_VOLUME)
             
    def update(self):
        ''' The update method is called once per frame, which performs multiple actions. '''
        self.dx = 0 #reset the dx value
        self.shell.update() #update the shell object
        
        self.followPlayer() #call the follow player method
        
        #determine if the enemy can fire
        if(self.ableToFire): #enemy is able to fire (within LOS)
            if(self.readyToFire): #enemy is charged and ready to fire
                self.fire() #fire a shell
        if(self.fireElapsed >= self.fireDelay): #charged for next attack
            self.fireElapsed = 0
            self.readyToFire = True
        elif(not self.readyToFire): #charge
            self.fireElapsed += 1
        
        if (self.environmentLeft > 0):
            self.reset() 
          
    def followPlayer(self):
        ''' Find the player object and shoot at their current location '''
        #get the player location
        dx = self.rect.centerx - self.playerPosX
        dy = self.rect.centery - self.playerPosY
        
        dy *= -1
        
        #calculate shoot angles
        radians = math.atan2(dy, dx)
        self.dir = radians * 180 / math.pi
        self.dir += 180
        
        #calculate distance
        self.distance = math.sqrt((dx * dx) + (dy * dy))
        
        #if the player is within range
        if(self.distance < self.LOSMaxDistance):
            #set the image to aggressive
            self.image = pygame.image.load(self.enemyTypeAggressiveStr)
            
            #get ready to fire, begin delay
            if(self.responseElapsed >= ENEMY_FIRE_RESPONSE_TIME):
                self.responseElapsed = 0
                self.ableToFire = True #ready to fire
            else:
                self.responseElapsed += 1        
        else: #cannot attack player if not in LOS
            self.ableToFire = False 
            self.image = pygame.image.load(self.enemyTypePassiveStr)
              
    def reset(self):
        ''' Reset the enemy to original position '''
        self.rect.centerx = self.originalx
    
       
    def moveLeft(self):
        ''' Move enemy left '''
        self.dx = SCROLL_SPEED
        self.rect.centerx += self.dx

    def moveRight(self):
        ''' Move enemy right ''' 
        self.dx = SCROLL_SPEED
        self.rect.centerx -= self.dx
    
    def fire(self):
        ''' Fire a shell object '''
        self.sndEnemyAttack.play()
        self.readyToFire = False
        
        #set the shell object to the X, Y of enemy, and setup other required variables
        self.shell.x = self.rect.centerx
        self.shell.y = self.rect.centery
        self.shell.speed = self.charge
        self.shell.dir = self.dir
        self.shell.update()
     
    def kill(self):
        ''' Move enemy off screen when killed ''' 
        self.rect.center = (-500, -500)


class Shell(pygame.sprite.Sprite):
    ''' The shell class is created by the enemy class. THe shell is fired from the enemy, which is used 
    to damage the player. '''
    def __init__(self, difficulty):
        pygame.sprite.Sprite.__init__(self)
        self.difficulty = difficulty #get difficulty

        #setup image
        self.image = pygame.image.load("bullet.gif")
        self.rect = self.image.get_rect()
        self.rect.center = (-100, -100)
        
        #instantiate speed, directional variables
        self.speed = 0
        self.dir = 0        
        self.dx = 0
        self.dy = 0
        
        #depending on difficulty, change variables to increase/decrease challenge
        if(self.difficulty == "easy"):
            self.damage = ENEMY_BULLET_DAMAGE_EASY
        elif(self.difficulty == "medium"):
            self.damage = ENEMY_BULLET_DAMAGE_MEDIUM
        elif(self.difficulty == "hard"):
            self.damage = ENEMY_BULLET_DAMAGE_HARD
        
        self.environmentMoveDir = "none" #determine current environment move direction
        
        self.reset()
        
        
    def update(self):
        ''' The update method is called once per frame, which performs multiple actions. '''  
        self.calcVector()
        self.calcPos()
        self.checkBounds()
        self.rect.center = (self.x, self.y)
   
    
    def calcVector(self):
        ''' Calculate the vector of the shell '''
        radians = self.dir * math.pi / 180
        
        self.dx = self.speed * math.cos(radians)
        self.dy = self.speed * math.sin(radians)
        self.dy *= -1
        #increase/decrease dx by scroll speed depending on current direction environment is moving
        if(self.environmentMoveDir == "left"):
            self.dx += SCROLL_SPEED
        elif(self.environmentMoveDir == "right"):
            self.dx -= SCROLL_SPEED

        self.environmentMoveDir = "none"
    
         
    def calcPos(self):
        ''' Calculate current position of the shell '''   
        self.x += self.dx
        self.y += self.dy
    
    
    def checkBounds(self):
        ''' Check if bounds of shell have exceeded screen '''
        #reset the shell if it goes off screen
        if self.x > SCREEN.get_width():
            self.reset()
        if self.x < 0:
            self.reset()
        if self.y > SCREEN.get_height():
            self.reset()
        if self.y < 0:
            self.reset()
    
    
    def reset(self):
        ''' Move off stage and stop '''
        self.x = -100
        self.y = -100

class Gameplay():
    ''' This class brings all of the other classes together to create
        the game.  '''
    def game(self, difficulty, score): # the game difficulty and score are passed to method game
        pygame.display.set_caption("Project 1")
        
        background = pygame.Surface(size = (800, 600))
        background.fill((0, 0, 0))
        background = background.convert()
        SCREEN.blit(background, (0, 0))
        
        previousScore = score   # previous score is a placeholder for the previous levels score
        
        player = Player(difficulty) #instantiate Player and pass difficult
        lightning = Lightning(difficulty) #instantiate Lightning
        environment = Environment(difficulty) #instantiate Environment
        scoreboard = Scoreboard(score) #instantiate Scoreboard and pass score
        pickup = Pickup(environment.rect.centerx, 300)
        
        enemiesKilled = 0 # initialize enemies killed to zero
        
        #setup the in-game music
        pygame.mixer.music.load('ArgonRefinery.mp3')
        pygame.mixer.music.play(-1, 0.0)#repeat
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
            
        enemy = [] # instantiate enemy array
        collLightningToEnemy = [] # instantiate collision lightning to enemy array
        collEnemyToPlayer = [] # instantiate collision enemy to player array
        collShellToPlayer = [] # instantiate collision shell to player array
        
        # set the number of enemies based on difficulty
        if(difficulty == "easy"):
            numberOfEnemies = NUM_OF_ENEMIES_EASY
        elif(difficulty == "medium"):
            numberOfEnemies = NUM_OF_ENEMIES_MEDIUM
        elif(difficulty == "hard"):
            numberOfEnemies = NUM_OF_ENEMIES_HARD
        # set where the enemies are to spawn
        averageEnemySpread = (environment.rect.right - ENEMY_START_X_BUFFER) / numberOfEnemies
        # for each enemy
        for i in range(numberOfEnemies):
            enemy.append("0")
            collEnemyToPlayer.append("0")
            collShellToPlayer.append("0")
            collLightningToEnemy.append("0")
            #The following creates the enemies and determines where they are placed in the level
            enemyStartX = ENEMY_START_X_BUFFER + i * (random.randrange(averageEnemySpread - ENEMY_SPREAD_VARIANCE_VALUE, averageEnemySpread + ENEMY_SPREAD_VARIANCE_VALUE))   
            enemyStartY = random.randrange(ENEMY_SPAWN_HEIGHT_MIN, ENEMY_SPAWN_HEIGHT_MAX)
            enemy[i] = Enemy(difficulty, enemyStartX, enemyStartY)
            
        #instantiate the clock
        clock = pygame.time.Clock()
        
        #the following is the primary game loop. The in-game happens within this loop
        keepGoing = True
        while keepGoing:
            pygame.mouse.set_visible(False)#hide the mouse
            clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)
            
            #organize the sprites into groups
            environmentSprites = pygame.sprite.OrderedUpdates(environment)
            friendSprites = pygame.sprite.OrderedUpdates(player, lightning, player.healthBar, player.chargeBar, scoreboard, pickup)
            enemySprites = pygame.sprite.OrderedUpdates()

            collPlayerToPickup = pygame.sprite.collide_rect(player, pickup) #check if player hit pickup
            
            #send in player coordinates so lightning knows where the player is
            lightning.playerPosX = player.rect.centerx
            lightning.playerPosY = player.rect.centery
            
            for i in range(numberOfEnemies):
                enemySprites.add(enemy[i], enemy[i].shell)#give each enemy a shell
                
                #send in player coordinates and environment coordinates so the enemies know where the player/environment is
                enemy[i].playerPosX = player.rect.centerx
                enemy[i].playerPosY = player.rect.centery
                enemy[i].environmentLeft = environment.rect.left
                
                #check collisions  
                collEnemyToPlayer[i] = pygame.sprite.collide_mask(player, enemy[i])
                collShellToPlayer[i] = pygame.sprite.collide_mask(player, enemy[i].shell)
                collLightningToEnemy[i] = pygame.sprite.collide_mask(lightning, enemy[i])
                # if any enemy to player collision happens
                if((collEnemyToPlayer[i] or collShellToPlayer[i]) and not player.invulnerable):
                    player.invulnerable = True # make the player take no damage after being hit
                    player.displayHealthElapsed = 0                 # for a short period of time
                    player.displayHealth = True
                    if(collEnemyToPlayer[i]): #if enemy collides with player
                        player.health -= enemy[i].damage #take away health
                        player.sndPlayerHurt.play()
                    if(collShellToPlayer[i]): #if shell collides with player
                        player.health -= enemy[i].shell.damage #take away health
                        enemy[i].shell.reset() #reset shell
                        player.sndPlayerHurt.play()
                if(collLightningToEnemy[i] and player.attacking): #if lightning collides with enemy
                    score += SCORE_ENEMY_DEATH #add to score
                    enemy[i].sndEnemyDeath.play()
                    enemiesKilled += 1 #add to enemies killed
                    enemy[i].kill() #kill the enemy
            
            #if player collided with pickup, give bonus score
            if(collPlayerToPickup):
                pickup.reset()
                score += SCORE_BONUS_PICKUP
            
            #check for keys pressed
            keystate = pygame.key.get_pressed()
            if (keystate[pygame.K_LEFT] or keystate[pygame.K_a]):
                #move everything left
                player.turnLeft()
                environment.moveLeft()
                pickup.moveLeft()
                for i in range(numberOfEnemies):
                    enemy[i].moveLeft()
                    enemy[i].shell.environmentMoveDir = "left"
            elif (keystate[pygame.K_RIGHT] or keystate[pygame.K_d]):
                #move everything right
                player.turnRight()
                environment.moveRight()
                pickup.moveRight()
                for i in range(numberOfEnemies):
                    enemy[i].moveRight()
                    enemy[i].shell.environmentMoveDir = "right"
            if keystate[pygame.K_SPACE]:
                #set the player to jumping state
                player.jumping = True
                
            #check for other events
            for event in pygame.event.get():
                #if the player clicks a quit event, stop the game loop
                if event.type == pygame.QUIT:
                    keepGoing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    #if the player clicks, and the player is fully charged
                    if(player.fullyCharged):
                        #player and lightning attack
                        lightning.attacking = True
                        player.attacking = True
                        
            #check game end conditions
            if environment.atEnd or player.health <= 0:
                if(player.health <= 0): #if player is out of health
                    playing = "gameOver" #send gameOver
                else:#player has reached the end
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
                    score *= SCORE_FACTOR_HARD
                
                score += previousScore #add the score the user had from previous levels
                
                keepGoing = False
                #return mouse cursor
                pygame.mouse.set_visible(True) 
                return playing, score
            
            scoreboard.score = score
            
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
    '''The Menu class defines the screens for main menu and game end '''
    def __init__(self):
        #create the buttons for main menu
        self.easyButton = Buttons.Button()
        self.mediumButton = Buttons.Button()
        self.hardButton = Buttons.Button()
        self.quitButton = Buttons.Button()
        #create the buttons for game end
        self.returnToMenuButton = Buttons.Button()
        self.nextLevelButton = Buttons.Button()
        
        #instantiate the clock
        self.clock = pygame.time.Clock()

    def mainMenu(self):
        ''' The main menu is called when the game is first launched, and after the game is over. '''
        #create a background
        background = pygame.Surface(size = (800, 600))
        background.fill(BLACK)
        background = background.convert()
        SCREEN.blit(background, (0, 0))
        
        insFont = pygame.font.SysFont(None, 40)#set font
        
        titleImage = pygame.image.load("title.png")
        imagerect = titleImage.get_rect()
        
        #display instructions
        insLabels = []
        instructions = (
        "Controls: A - move left",
        "                 D - move right",
        "          space - jump",
        "         mouse - moves lightning",
        "     left click - attack",
        "             ESC - quit",
        "Goal: Get to the right side ",
        "      of the world to escape.")
    
        for line in instructions:
            tempLabel = insFont.render(line, 1, (255, 255, 255))
            insLabels.append(tempLabel)
            
        playing = "menu"
        while playing == "menu":
            self.clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)
            
            #if the player clicks a quit event, stop the loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    #check if a button was pressed, and return playing
                    if self.easyButton.pressed(pygame.mouse.get_pos()):
                        playing = "easy"
                    elif self.mediumButton.pressed(pygame.mouse.get_pos()):
                        playing = "medium"
                    elif self.hardButton.pressed(pygame.mouse.get_pos()):
                        playing = "hard"
                    elif self.quitButton.pressed(pygame.mouse.get_pos()):
                        playing = "quit"
                        
            #Parameters:                    surface, color,         x,   y,   length, height, width,  text,        text_color
            self.easyButton.create_button(  SCREEN,  DARK_GREEN,    100, 200, 200,    75,     0,      "Easy"     , WHITE)
            self.mediumButton.create_button(SCREEN,  DARK_BLUE,     100, 325, 200,    75,     0,      "Medium"   , WHITE)
            self.hardButton.create_button(  SCREEN,  DARK_RED,      100, 450, 200,    75,     0,      "Hard"     , WHITE)
            self.quitButton.create_button(  SCREEN,  RED,           690, 10,  100,    40,     0,      "Exit Game", WHITE)
            
            for i in range(len(insLabels)):
                SCREEN.blit(insLabels[i], (400, 200 + (30 * i)))
            
            SCREEN.blit(titleImage, imagerect)

            #flip the display
            pygame.display.flip()
            
        return playing
    
    def endMenu(self, score, playing, difficulty):
        ''' The endMenu method is called when the game has just ended '''
        #create a background
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
                    #check if a button was pressed, and return playing
                    if self.returnToMenuButton.pressed(pygame.mouse.get_pos()):
                        playing = "menu"
                    elif self.nextLevelButton.pressed(pygame.mouse.get_pos()):
                        #determine difficulty, and play next difficulty
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
             
            #setup end game messages. Different messages appear depending on whether the game has ended or if the player has completed a level   
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
    '''The main method is the primary method called when the game is first launched,
    and determines the order in which other primary methods are called '''
    playing = "menu" #the playing variable determines which screen will be displayed next
    
    gameplay = Gameplay() #create a gameplay object
    menu = Menu() #create a method object
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

if __name__ == "__main__": #call main
    main()
