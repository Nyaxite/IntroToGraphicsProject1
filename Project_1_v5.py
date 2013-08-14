# Source File Name: Project_1.py
# Names: Michael Burnie, Evan Pugh
# Last Modified By: Michael Burnie
# Date Last Modified: August 12, 2013
""" 
  Program Description: You play as an orb of lightning. The objective is to get to the other side of 
  the level without dying. Click to attack; but be careful, after your attack has completed, you will
  need time to recharge. Enemies will shoot at you. Avoid them and their projectiles!

    Version: 5
    - Added endless mode!
        - The game never ends
        - Enemies continuously spawn
    - The boss can now shoot
        - Shoots 8 projectiles outwards from the center
        - Does the same damage as a hard enemy
        - Has a charge bar to display time between shots
    - Completed splash screen
    - Changed the location at which enemies can spawn

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
JUMP_SPEED = 24 #dy value of the player when they first initiate a jump

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
PLAYER_BOTTOM_POS = 550
PLAYER_MAX_HEALTH = 50
PLAYER_INVULNERABILITY_DURATION_EASY = 40
PLAYER_INVULNERABILITY_DURATION_MEDIUM = 30
PLAYER_INVULNERABILITY_DURATION_HARD = 20
PLAYER_ATTACK_DURATION_EASY = 45
PLAYER_ATTACK_DURATION_MEDIUM  = 40
PLAYER_ATTACK_DURATION_HARD = 30
PLAYER_DAMAGE = 1

LIGHTNING_X_MAX_FROM_PLAYER = 100

#constants for enemies. Some are affected by difficulty, in which multiple constants are made. Numbers represent the number of frames
NUM_OF_ENEMIES_EASY = 10
NUM_OF_ENEMIES_MEDIUM = 15
NUM_OF_ENEMIES_HARD = 20
NUM_OF_ENEMIES_BOSS = 5
NUM_OF_ENEMIES_ENDLESS = 10
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
ENEMY_START_X_BUFFER = 850 #the closest X distance from the left side of the environment that the enemies can spawn

#constants for boss object
BOSS_DAMAGE = 5
BOSS_MAX_HEALTH = 100
BOSS_NUM_OF_SHELLS = 8
BOSS_CHARGE = 6
BOSS_FIRE_DELAY = 90

BOSS_START_X = 800
BOSS_MIN_Y = 100
BOSS_MAX_Y = 500
BOSS_MIN_MAX_X_BUFFER = 500

#score constants, values in score
SCORE_ENEMY_DEATH = 10 #score for killing enemy
SCORE_BONUS_PICKUP = 30 #score for picking up bonus pickup
SCORE_BONUS_FINISH = 50 #score for finishing the game
SCORE_BONUS_FULL_HEALTH = 200 #score for finishing with full health
SCORE_BONUS_PACIFIST = 100 #score for beating game without killing enemies
SCORE_BONUS_BOSS = 150 #score for killing boss

#score multipliers awarded once the game ends. Depending on the difficulty, the player's score will be multiplied by the following values
SCORE_FACTOR_EASY = 1
SCORE_FACTOR_MEDIUM  = 2
SCORE_FACTOR_HARD  = 4

#game volume
MUSIC_VOLUME = 0.1
SOUND_VOLUME = 0.7

SPLASH_SCREEN_WAIT = 2000 #in milliseconds

#setup in-game sound setup
if not pygame.mixer:
    print("problem with sound")
else:
    pygame.mixer.init()
    sndPlayerHurt = pygame.mixer.Sound("playerHurt.ogg")
    sndPlayerAttack = pygame.mixer.Sound("playerAttack.ogg")
    sndEnemyDeath = pygame.mixer.Sound("enemyDeath.ogg")
    sndEnemyAttack = pygame.mixer.Sound("enemyAttack.ogg")
    sndClickSound = pygame.mixer.Sound("clickSound.ogg")
    
    #setup the in-game music
    pygame.mixer.music.load('ArgonRefinery.mp3')
    pygame.mixer.music.play(-1, 0.0)#repeat
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    
    #set the volume and make adjustments from default for given sounds if required
    sndPlayerHurt.set_volume(SOUND_VOLUME)
    sndPlayerAttack.set_volume(SOUND_VOLUME)
    sndEnemyDeath.set_volume(SOUND_VOLUME)
    sndEnemyAttack.set_volume(SOUND_VOLUME + 0.5)
    sndClickSound.set_volume(SOUND_VOLUME)
    
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
        elif(self.difficulty == "hard" or self.difficulty == "boss" or self.difficulty == "endless"):
            self.invulnerabilityDuration = PLAYER_INVULNERABILITY_DURATION_HARD
            self.attackDuration = PLAYER_ATTACK_DURATION_HARD
        
        self.invulnerable = False #is player invulnerable
        self.invulnerabilityElapsed = 0
                
        self.attacking = False #is player attacking
        self.attackElapsed = 0
        
        self.fullyCharged = True #is player fully charged to attack
        self.attackDelay = 60 #delay between attacks
        self.damage = PLAYER_DAMAGE
        
        self.facing = "right" #current facing for player
        
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
        elif(self.dy <= -JUMP_SPEED):
            self.rect.bottom = PLAYER_BOTTOM_POS #player has landed
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
        sndPlayerAttack.play()
    
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
        elif(self.difficulty == "hard" or self.difficulty == "boss" or self.difficulty == "endless"):
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
        
        #check the attack states of lightning
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
        
        self.difficulty = difficulty
        
        #setup background images
        #depending on difficulty, select corresponding level
        if(self.difficulty == "easy"):
            self.image = pygame.image.load("level-1.jpg")
        elif(self.difficulty == "medium"):
            self.image = pygame.image.load("level-2.jpg")
        elif(self.difficulty == "hard"):
            self.image = pygame.image.load("level-3.jpg")
        elif(self.difficulty == "boss"  or self.difficulty == "endless"):
            self.image = pygame.image.load("boss-level.jpg")
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
        if (self.rect.right < SCREEN.get_width() + 10):
            if(self.difficulty == "endless"):
                self.reset()
            else:
                self.atEnd = True#at the end of the level
                self.rect.right = SCREEN.get_width()#don't let the background move any farther right
        else:
            self.rect.centerx -= self.dx
            self.atEnd = False
            
class Enemy(pygame.sprite.Sprite): 
    '''The enemy class defines everything about the enemies for the player. Enemies shoot at the player.
    They can be killed if they come in contact with Lightning when the player is attacking. '''
    def __init__(self, difficulty, centerx, bottom):
        pygame.sprite.Sprite.__init__(self)
        self.difficulty = difficulty #read in the difficulty
        
        #instantiate position parameters for environment, player
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
        elif(self.difficulty == "hard" or self.difficulty == "boss" or self.difficulty == "endless"):
            self.fireDelay = ENEMY_FIRE_DELAY_HARD
            self.charge = ENEMY_CHARGE_HARD
            self.damage = ENEMY_DAMAGE_HARD
            self.LOSMaxDistance = ENEMY_LOS_MAX_DISTANCE_HARD

        #determine other mechanics for firing
        self.readyToFire = True #is fully charged to fire
        self.ableToFire = False #is player in range 
        self.hasFired = False #keeps track if the enemy has fired
        self.fireElapsed = 0
        self.responseElapsed = 0
        self.dir = 180
        
        self.shell = Shell(self.difficulty) #create a shell object for each enemy
             
    def update(self):
        ''' The update method is called once per frame, which performs multiple actions. '''
        self.dx = 0 #reset the dx value
        
        if(self.hasFired):
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
        
        #calculate distance
        self.distance = math.sqrt((dx * dx) + (dy * dy))
        
        #if the player is within range
        if(self.distance < self.LOSMaxDistance):
            #set the image to aggressive
            self.image = pygame.image.load(self.enemyTypeAggressiveStr)
            
            #calculate shoot angles
            radians = math.atan2(dy, dx)
            self.dir = radians * 180 / math.pi
            self.dir += 180
            
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
        sndEnemyAttack.play()
        self.readyToFire = False
        self.hasFired = True
        
        #set the shell object to the X, Y of enemy, and setup other required variables
        self.shell.x = self.rect.centerx
        self.shell.y = self.rect.centery
        self.shell.speed = self.charge
        self.shell.dir = self.dir
        self.shell.update()
     
    def die(self):
        ''' Move enemy off screen when killed '''
        self.rect.center = (-100, -100)
        self.kill()


class Shell(pygame.sprite.Sprite):
    ''' The shell class is created by the enemy class. The shell is fired from the enemy, which is used 
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
        elif(self.difficulty == "hard" or self.difficulty == "boss" or self.difficulty == "endless"):
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
        
class Boss(pygame.sprite.Sprite):
    '''The boss class handles all of the actions/properties of the boss object. 
    The boss enemy appears in the boss level, and is very difficult to kill.
    Unlike a normal enemy, it shoots multiple projectiles, and requires several hits to kill.'''
    def __init__(self):
        '''Constructer for boss'''
        pygame.sprite.Sprite.__init__(self)
        
        #instantiate position parameters for environment, player
        self.environmentLeft = 0 
        self.environmentRight = 0
        self.playerPosX = 0
        self.playerPosY = 0
        
        #load the image
        self.image = pygame.image.load("player.png")
        self.image = pygame.transform.scale2x(self.image)
        
        #set starting coordinates, which are sent in
        self.rect = self.image.get_rect()
        self.originalx = BOSS_START_X
        self.originaly = BOSS_MIN_Y
        self.rect.centerx = self.originalx
        self.rect.bottom = self.originaly
        
        #movement variables for boss
        self.defaultdx = 5
        self.defaultdy = 5
        self.dx = self.defaultdx
        self.facingX = "right"
        self.facingY = "down"
        self.environmentMoveDir = "none"

        #set boss health, and create healthBar sprite
        self.health = BOSS_MAX_HEALTH
        self.healthPercent = self.health / PLAYER_MAX_HEALTH * 100
        self.healthBar = StatusBar(self.healthPercent, RED, YELLOW, GREEN_YELLOW, GREEN)
        self.living = True
        
        #create charge bar for player attacks
        self.chargePercent = 100
        self.chargeBar = StatusBar(self.chargePercent, DARK_BLUE, MID_LOW_BLUE, MID_HIGH_BLUE, BLUE)
        
        #fire properties for boss
        self.fireDelay = BOSS_FIRE_DELAY
        self.charge = BOSS_CHARGE
        self.damage = BOSS_DAMAGE
        
        #determine other mechanics for firing
        self.readyToFire = True #is fully charged to fire
        self.hasFired = False #keeps track if the enemy has fired
        self.fireElapsed = 0
        self.responseElapsed = 0
        self.dir = 0
        
        #instantiate boss shells
        self.shells = []
        for i in range(BOSS_NUM_OF_SHELLS):
            self.shells.append("0")
            self.shells[i] = Shell("boss") #create multiple shell objects for boss
             
    def update(self):
        ''' The update method is called once per frame, which performs multiple actions. '''
        #change the facing of the boss if hitting left or right side
        if(self.rect.centerx <= self.environmentLeft + BOSS_MIN_MAX_X_BUFFER):
            self.facingX = "right"
        elif(self.rect.centerx >= self.environmentRight - BOSS_MIN_MAX_X_BUFFER):
            self.facingX = "left"
            
        #change the facing of the boss if hitting top or bottom
        if(self.rect.centery <= BOSS_MIN_Y):
            self.facingY = "down"
        elif(self.rect.centery >= BOSS_MAX_Y):
            self.facingY = "up"

        self.updateHealth() #update the health of the boss object
        self.updateCharge() #update the charge bar of the boss object
        self.moveBoss() #move the boss object
        
        if(self.health <= 0): #if the boss is out of health, call the die method
            self.die()
            
        #update the shell objects
        if(self.hasFired):
            for i in range(BOSS_NUM_OF_SHELLS): 
                self.shells[i].update() 

        #determine if the boss can fire
        if(self.readyToFire): #boss is charged and ready to fire
            self.fire() #fire shells
        if(self.fireElapsed >= self.fireDelay): #charged for next attack
            self.fireElapsed = 0
            self.readyToFire = True
        elif(not self.readyToFire): #charge
            self.fireElapsed += 1
            
    def moveBoss(self):
        ''' This method handles everything to move the boss around the level '''
        #check the facing and environment move direction to determine delta X of boss object
        if(self.facingX == "right" and self.environmentMoveDir == "right"):
            self.dx = self.defaultdx - SCROLL_SPEED
        elif(self.facingX == "right" and self.environmentMoveDir == "left"):
            self.dx = SCROLL_SPEED + self.defaultdx
        elif(self.facingX == "right"):
            self.dx = self.defaultdx
        elif(self.facingX == "left" and self.environmentMoveDir == "right"):
            self.dx = -SCROLL_SPEED - self.defaultdx
        elif(self.facingX == "left" and self.environmentMoveDir == "left"):
            self.dx = SCROLL_SPEED - self.defaultdx
        elif(self.facingX == "left"):
            self.dx = -self.defaultdx
        self.rect.centerx += self.dx#move the boss object along the X-axis
        
        #check the current facing to determine the delta Y of the object
        if(self.facingY == "up"):
            self.dy = -self.defaultdy
        if(self.facingY == "down"):
            self.dy = self.defaultdy
        self.rect.centery += self.dy#move the boss object along the Y-axis

        self.environmentMoveDir = "none"#reset the environment move direction
            
    def updateHealth(self):
        ''' Manages the health bar for the boss class '''
        #show and update the health bar
        self.healthPercent = self.health * 100 / BOSS_MAX_HEALTH
        self.healthBar = StatusBar(self.healthPercent, RED, YELLOW, GREEN_YELLOW, GREEN) #recreate healthbar object
        #position the health bar above the boss
        self.healthBar.rect.centerx = self.rect.centerx
        self.healthBar.rect.centery = self.rect.centery - 50
        
    def updateCharge(self):
        ''' Similar to the updateHealth function, this method keeps track of, and displays the boss' charge percent.
        The charge bar is displayed below the boss. The boss will shoot again once the charge bar is at its peak.'''        
        if(not self.readyToFire):
            #show charge bar and update charge percentage
            self.chargePercent = self.fireElapsed * 100 / self.fireDelay
            self.chargeBar = StatusBar(self.chargePercent, DARK_BLUE, MID_LOW_BLUE, MID_HIGH_BLUE, BLUE)
            #display chargebar below boss
            self.chargeBar.rect.centerx = self.rect.centerx
            self.chargeBar.rect.centery = self.rect.centery + 50
       
    def moveLeft(self):
        ''' Move boss left '''
        self.moving = "right"

    def moveRight(self):
        ''' Move boss right '''
        self.moving = "left"
        
    def fire(self):
        ''' Fire shell objects for boss '''
        sndEnemyAttack.play()
        self.readyToFire = False
        self.hasFired = True
        
        #set the shell objects to the X, Y of boss, and setup other required variables for each shell
        for i in range(BOSS_NUM_OF_SHELLS):
            self.shells[i].x = self.rect.centerx
            self.shells[i].y = self.rect.centery
            self.shells[i].speed = self.charge
            self.shells[i].dir = i * (360 / BOSS_NUM_OF_SHELLS)
            self.shells[i].update()
     
    def die(self):
        ''' Move enemy off screen when killed '''
        self.living = False
        self.rect.center = (-100, -100)
        self.kill()     
        
class Gameplay():
    ''' This class brings all of the other classes together to create
        the game.  '''
    def game(self, difficulty, score): # the game difficulty and score are passed to method game
        pygame.display.set_caption("Orbituary")
        
        background = pygame.Surface(size = (800, 600))
        background.fill((0, 0, 0))
        background = background.convert()
        SCREEN.blit(background, (0, 0))
        
        previousScore = score   # previous score is a placeholder for the previous levels score
        bossLevel = False#instantiate a boss variable to determine if boss is on this level
        endGame = False #determine if the game is at its end
        roundScore = 0
        
        player = Player(difficulty) #instantiate Player and pass difficult
        lightning = Lightning(difficulty) #instantiate Lightning
        environment = Environment(difficulty) #instantiate Environment
        scoreboard = Scoreboard(previousScore) #instantiate Scoreboard and pass score
        pickup = Pickup(environment.rect.centerx, 300)
        
        enemiesKilled = 0 # initialize enemies killed to zero
            
        enemy = [] # instantiate enemy array
        shells = [] #instantiate a shell array
        
        # set the number of enemies based on difficulty
        if(difficulty == "easy"):
            numberOfEnemies = NUM_OF_ENEMIES_EASY
        elif(difficulty == "medium"):
            numberOfEnemies = NUM_OF_ENEMIES_MEDIUM
        elif(difficulty == "hard"):
            numberOfEnemies = NUM_OF_ENEMIES_HARD
        elif(difficulty == "boss"):
            numberOfEnemies = NUM_OF_ENEMIES_BOSS
            #create and setup the boss enemy if on boss difficulty
            boss = Boss()
            bossSprites = pygame.sprite.OrderedUpdates(boss, boss.shells)
            bossLevel = True
        elif(difficulty == "endless"):
            numberOfEnemies = NUM_OF_ENEMIES_ENDLESS
            
        #organize the sprites into groups
        environmentSprites = pygame.sprite.OrderedUpdates(environment)
        friendSprites = pygame.sprite.OrderedUpdates(player, lightning, scoreboard, pickup)
        statusSprites =  pygame.sprite.OrderedUpdates(player.healthBar, player.chargeBar)
        enemySprites = pygame.sprite.OrderedUpdates()

        # set where the enemies are to spawn
        averageEnemySpread = (environment.rect.right - ENEMY_START_X_BUFFER * 2) / numberOfEnemies
        # for each enemy
        for i in range(numberOfEnemies):
            enemy.append("0")
            shells.append("0")
            #The following creates the enemies and determines where they are placed in the level
            enemyStartX = ENEMY_START_X_BUFFER + i * (random.randrange(averageEnemySpread - ENEMY_SPREAD_VARIANCE_VALUE, averageEnemySpread + ENEMY_SPREAD_VARIANCE_VALUE))   
            enemyStartY = random.randrange(ENEMY_SPAWN_HEIGHT_MIN, ENEMY_SPAWN_HEIGHT_MAX)
            enemy[i] = Enemy(difficulty, enemyStartX, enemyStartY)
            shells[i] = enemy[i].shell
            
        #instantiate the clock
        clock = pygame.time.Clock()
        
        #the following is the primary game loop. All of the in-game happens within this loop
        keepGoing = True
        while keepGoing:
            pygame.mouse.set_visible(False)#hide the mouse
            clock.tick(FRAMES_PER_SECOND)#set the clock's FPS (30 by default)

            #update the status sprites
            statusSprites = pygame.sprite.OrderedUpdates(player.healthBar, player.chargeBar)
            if(bossLevel and boss.living): #update any boss status sprites and send environment position details
                statusSprites.add(boss.healthBar)
                statusSprites.add(boss.chargeBar)
                boss.environmentLeft = environment.rect.left
                boss.environmentRight = environment.rect.right
            
            #check to create more enemies if the game is on endless mode, once the background is reset
            if(environment.rect.left >= 0 and difficulty == "endless"): 
                pickup = Pickup(environment.rect.centerx, 300)
                enemy = []
                shells = []
                enemySprites.empty()
                # for each enemy
                for i in range(numberOfEnemies):
                    enemy.append("0")
                    shells.append("0")
                    #The following creates new enemies and determines their start positions
                    enemyStartX = ENEMY_START_X_BUFFER + i * (random.randrange(averageEnemySpread - ENEMY_SPREAD_VARIANCE_VALUE, averageEnemySpread + ENEMY_SPREAD_VARIANCE_VALUE))   
                    enemyStartY = random.randrange(ENEMY_SPAWN_HEIGHT_MIN, ENEMY_SPAWN_HEIGHT_MAX)
                    enemy[i] = Enemy(difficulty, enemyStartX, enemyStartY)
                    shells[i] = enemy[i].shell
                    
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
            enemyHitPlayer = pygame.sprite.spritecollideany(player, enemy) #enemy hits player directly
            shellHitPlayer = pygame.sprite.spritecollideany(player, shells) #enemy bullet hits player
            lightningHitEnemy = pygame.sprite.spritecollideany(lightning, enemy) #player lightning hits enemy
            playerHitPickup = pygame.sprite.collide_rect(player, pickup) #check if player hit pickup
            if(bossLevel): #setup boss level collisions
                bossHitPlayer = pygame.sprite.collide_rect(boss, player)#boss hits player
                lightningHitBoss = pygame.sprite.collide_rect(lightning, boss)#lightning hits boss
                bossShellHitPlayer = pygame.sprite.spritecollideany(player, boss.shells)#boss bullets hit player
            
            # if any enemy to player collision happens
            if((enemyHitPlayer or shellHitPlayer) and not player.invulnerable):
                player.invulnerable = True # make the player take no damage after being hit
                player.displayHealthElapsed = 0                 # for a short period of time
                player.displayHealth = True
                sndPlayerHurt.play()
                if(enemyHitPlayer): #if enemy collides with player
                    player.health -= enemyHitPlayer.damage #take away health
                if(shellHitPlayer): #if shell collides with player
                    player.health -= shellHitPlayer.damage #take away health
                    shellHitPlayer.reset() #reset shell

            if(lightningHitEnemy and player.attacking): #if lightning collides with enemy
                roundScore += SCORE_ENEMY_DEATH #add to round score
                sndEnemyDeath.play()
                enemiesKilled += 1 #add to enemies killed
                lightningHitEnemy.die() #kill the enemy
                
            #if player collided with pickup, give bonus score
            if(playerHitPickup):
                pickup.reset()
                roundScore += SCORE_BONUS_PICKUP
            
            if(bossLevel):  #check for boss level collisions
                if((bossHitPlayer or bossShellHitPlayer) and not player.invulnerable):
                    player.invulnerable = True # make the player take no damage after being hit
                    player.displayHealthElapsed = 0                 # for a short period of time
                    player.displayHealth = True
                    sndPlayerHurt.play()
                    if(bossHitPlayer):
                        player.health -= boss.damage #take away health
                    elif(bossShellHitPlayer):
                        player.health -= bossShellHitPlayer.damage
                        bossShellHitPlayer.reset()
                if(lightningHitBoss and player.attacking): #if player attacks the boss
                    boss.health -= player.damage
                    sndEnemyDeath.play()
                if(not boss.living):
                    endGame = True               
            
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
                if(bossLevel):
                    boss.moveLeft()
                    boss.environmentMoveDir = "left"
                    for i in range(BOSS_NUM_OF_SHELLS):
                        boss.shells[i].environmentMoveDir = "left"
            elif (keystate[pygame.K_RIGHT] or keystate[pygame.K_d]):
                #move everything right
                player.turnRight()
                environment.moveRight()
                if(not environment.atEnd): #ensure that stuff doesn't move when the environment is at the right side    
                    pickup.moveRight()
                    for i in range(numberOfEnemies):
                        enemy[i].moveRight()
                        enemy[i].shell.environmentMoveDir = "right"
                    if(bossLevel):
                        boss.moveRight()
                        boss.environmentMoveDir = "right"
                        for i in range(BOSS_NUM_OF_SHELLS):
                            boss.shells[i].environmentMoveDir = "right"
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
                        
            #if the player dies or they make it to the other side of the level on a regular level,
            if((environment.atEnd and not bossLevel) or player.health <= 0):
                endGame = True #send endgame to true
                
            if(endGame):#check game end conditions
                if(player.health <= 0): #if player is out of health
                    playing = "gameOver" #send gameOver
                elif(environment.atEnd or bossLevel):#player has reached the end of a level, or killed a boss
                    playing = "endGame"
                    roundScore += SCORE_BONUS_FINISH #add a bonus to play score if they finished the level
                    
                    if(bossLevel):
                        if(not boss.living):
                            roundScore += SCORE_BONUS_BOSS #add a bonus to play score if killed boss
                    
                    #add bonus score if the player finished with full health
                    if(player.health == PLAYER_MAX_HEALTH):
                        roundScore += SCORE_BONUS_FULL_HEALTH
                        
                    #add bonus score if the player kills no enemies
                    if(enemiesKilled == 0):
                        roundScore += SCORE_BONUS_PACIFIST
                    
                
                #multiply the score by the factor for the given difficulty, for this level only
                if(difficulty == "easy"):
                    roundScore *= SCORE_FACTOR_EASY
                elif(difficulty == "medium"):
                    roundScore *= SCORE_FACTOR_MEDIUM
                elif(difficulty == "hard" or difficulty == "boss" or difficulty == "endless"):
                    roundScore *= SCORE_FACTOR_HARD
                
                score = previousScore + roundScore #add the score the user had from previous levels to the score gained from the round
                
                keepGoing = False
                #return mouse cursor
                pygame.mouse.set_visible(True) 
                return playing, score
            
            scoreboard.score = previousScore + roundScore #update the scoreboard score
            
            #clear each sprite
            statusSprites.clear(SCREEN, background)
            friendSprites.clear(SCREEN, background)
            enemySprites.clear(SCREEN, background)
            environmentSprites.clear(SCREEN, background)
            if(bossLevel):
                bossSprites.clear(SCREEN, background)
    
            #update each sprite
            statusSprites.update()
            friendSprites.update()
            enemySprites.update()
            environmentSprites.update()
            if(bossLevel):
                bossSprites.update()
            
            #draw the sprites on the screen
            environmentSprites.draw(SCREEN)
            if(bossLevel):
                bossSprites.draw(SCREEN)
            friendSprites.draw(SCREEN)
            enemySprites.draw(SCREEN)
            statusSprites.draw(SCREEN)
            
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
        self.bossButton = Buttons.Button()
        self.endlessButton = Buttons.Button()
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
                    elif self.bossButton.pressed(pygame.mouse.get_pos()):
                        playing = "boss"
                    elif self.endlessButton.pressed(pygame.mouse.get_pos()):
                        playing = "endless"
                    elif self.quitButton.pressed(pygame.mouse.get_pos()):
                        playing = "quit"
            
            #creating buttons            
            #Parameters:                    surface, color,         x,   y,   length, height, width,  text,        text_color
            self.easyButton.create_button(  SCREEN,  DARK_GREEN,    100, 200, 200,    60,     0,      "Easy"     , WHITE)
            self.mediumButton.create_button(SCREEN,  DARK_BLUE,     100, 275, 200,    60,     0,      "Medium"   , WHITE)
            self.hardButton.create_button(  SCREEN,  DARK_RED,      100, 350, 200,    60,     0,      "Hard"     , WHITE)
            self.bossButton.create_button(  SCREEN,  WHITE,         100, 425, 200,    60,     0,      "Boss"     , BLACK)
            self.endlessButton.create_button(SCREEN, BLACK,         100, 500, 200,    60,     0,      "Endless"  , WHITE)
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
                            playing = "boss"
                        elif(difficulty == "boss"):
                            playing = "endless"
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
    
    def splashScreen(self):
        '''This method instantiates a background used for the splash screen, and holds it for a given period of time'''
        #create a background
        background = pygame.Surface(size = (800, 600))
        background.fill(YELLOW)
        background = background.convert()
        SCREEN.blit(background, (0, 0))
        
        #show splash screen
        self.image = pygame.image.load("splashscreen.jpg")
        SCREEN.blit(self.image, (0,0))
        
        #flip the display
        pygame.display.flip()
        
        #hold the splash screen for given time
        pygame.time.delay(SPLASH_SCREEN_WAIT)
        

def main():
    '''The main method is the primary method called when the game is first launched,
    and determines the order in which other primary methods are called '''
    playing = "menu" #the playing variable determines which screen will be displayed next
    
    gameplay = Gameplay() #create a gameplay object
    menus = Menu() #create a method object
    score = 0
    
    menus.splashScreen()#display splash screen
    while playing != "quit":
        if(playing == "menu"):
            playing = menus.mainMenu()
        elif(playing == "easy" or playing == "medium" or playing == "hard" or playing == "boss" or playing == "endless"):
            difficulty = playing
            playing, score = gameplay.game(difficulty, score)
        elif(playing == "endGame" or playing == "gameOver"):
            playing = menus.endMenu(score, playing, difficulty)
            
            #reset the score if the game has ended
            if(playing == "menu"):
                score = 0
        else:
            playing = "quit"

if __name__ == "__main__": #call main
    main()
