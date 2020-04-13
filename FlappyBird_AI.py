import datetime
import time
import random
import pickle
import pygame 
import argparse
import tensorflow


width=288
height=512
speed=3
bdim=(29,20)
odim=(52,320)
population=[]
score=[]
max_score=50

class machine:
    def __init__(self):
        self.score=0
        self.bird=Bird()

    def play(self):
        if self.bird.alive:
            self.bird.draw()

    def inc_score(self):
        if self.bird.alive:
            self.score+=1

    def death(self):
        self,bird.alive=False


class obstacle :
    def __init__(self):
        self.x=width
        #define a gap between the pipes and create it
        self.gap=random.randrange(90,130)
        self.y1=random.randrange(31+self.gap,height-(112+31))
        self.y2=self.y1-self.gap-320
        self.velocity=speed
        self.inv=pygame.image.load("inv_pipe.png")
        self.pipe=pygame.image.load("pipe.png")

    def move(self):
        self.x-=self.velocity

    def getpos(self):
        return self.x,self.y1,self.y2
 
    def draw(self):
        screen.blit(self.pipe,(self.x,self.y1))
        screen.blit(self.inv,(self.x,self.y2))

class Bird :
    def __init__(self,birdtype="default"):
        global height
        self.birdtype=birdtype
        self.x=100
        self.y=height//2
        self.count=0
        self.jumpheight=4
        self.alive=True
        if birdtype== "default":
            self.up=pygame.image.load("up.png")
            self.mid=pygame.image.load("mid.png")
            self.down=pygame.image.load("down.png")
            
    def getpos(self):
        return (self.x,self.y)

    def change_pos(self):
        self.y+=4.5
        self.count+=1
        #count is used only to animate the bird
        if self.count>= 12:
            self.count=0

    def jump(self,key):
        if key:
            self.jumpheight=4
        if self.jumpheight>=0 and self.y>0:
            self.y-=(self.jumpheight**2)*0.55
            self.jumpheight-=1
            if self.count>= 12:
                self.count=0
        else:
            self.jumpheight=4

    def draw(self):
        if self.count//3 ==0:
            screen.blit(self.mid,(self.x,int(self.y)))
        elif self.count//3 ==1:
            screen.blit(self.down,(self.x,int(self.y)))
        elif self.count//3 ==2:
            screen.blit(self.mid,(self.x,int(self.y)))
        else:
            screen.blit(self.up,(self.x,int(self.y)))
    
class Text:
    def __init__(self,size=25):
        self.font= pygame.font.Font(None,size)
        
    def write(self,str,x=0,y=0):
        self.text= self.font.render(str,True,(255,255,255))
        screen.blit(self.text,(x,y))

def collision(bcord,ocord):
    #check if bird hit the ground
    if bcord[1]+20>height-112:
        return True
    #check if bird hit a obstacle
    if bcord[0]+bdim[0]>ocord[0] and bcord[0]+5< ocord[0]+odim[0]:
        if not(bcord[1]+5>ocord[2]+odim[1] and bcord[1]+bdim[1]<ocord[1]):
            return True

def init_pop(size):
    for i in range(size):
        member= machine()
        population.append(member)

def new_pop(size):
    pass
def mutation(chance):
    pass

def fitness():
    #the function starts the game and each machine tries to score
    #the game ends when all birds have died
    global screen
    pygame.display.set_caption('Flappy Bird AI')
    screen = pygame.display.set_mode((width,height))
    pygame.mixer.music.load('Eminem - Godzilla (Lyrics) ft. Juice WRLD.mp3')
    pygame.mixer.music.play(-1)
    bg=pygame.image.load("background.png")
    ground=pygame.image.load("ground.png")
    start_img=pygame.image.load("gamestart.png")
    clock=pygame.time.Clock()
    x=0
    count=0
    key=random.randrange(60,120)
    obstacles=[]
    while not done:
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                done =True
        count+=1
        #add obstacles to the game
        if len(obstacles) < 3 and count==key:
                count=0
                key=random.randrange(60,120)
                obst=obstacle()
                obstacles.append(obst)
        #move and remove the obstacles
        for obst in obstacles:
                obst.move()
                if pos[0]<= -odim[0]:
                    obstacles.remove(obst)
        #move every bird,check for collision,increase the score of birds
        for member in population:
            member.play()
            for obst in obstacles:
                pos=obst.getpos()
                if collision(member.bird.getpos(),pos):
                    member.death()
                if pos[0]+odim[0]<100 and pos[0]+odim[0]>=100-speed:
                    member.inc_score()
        #check if any bird is left
        for member in population:
            if member.bird.alive:
                break
            done=True
        #for moving ground
        x-=speed
        if x<=width-336:
            x=0
        screen.blit(bg,(0,0))
        screen.blit(ground,(x,height-112))
        for obst in obstacles:
            obst.draw() 
        pygame.display.update()
        clock.tick(60)

    pygame.display.quit()
    pygame.quit()
    pygame.quit()

def main():
    size=30
    init_pop(size)
    fitness()
    for k in range(25):
        if max(score) == max_score:
            print("Finish")
            return 
        population = new_pop(size)
        mutation(0.1)
        fitness()

if __name__ == '__main__':
    main()