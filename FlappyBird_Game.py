import datetime
import time
import random
import pickle
import pygame 
import argparse

class Gameplay :
    def __init__(self):
        self.play_duration =datetime.timedelta()
        self.no_of_jumps = 0
        self.score= 0
        self.stage=1
        self.start_time=datetime.datetime.now()
        self.bird= Bird()
        self.obstacles=[]
        self.paused=False
        self.count=0
        self.key=random.randrange(40,80)
        self.end=False
        
    def Quit(self):
        if self.count:
            self.play_duration+=self.endtime-self.start_time
        self.count=0
        text=Text()
        text.write("Time spent:%d.%ds"%(self.play_duration.seconds,self.play_duration.microseconds//10000),width//2-64,height//2+20)

    def Paused(self,pressed):
        text=Text()
        text.write("Game Paused",width//2-48,height//2-56)
        if not self.paused:
            self.pstart=datetime.datetime.now()
        self.paused=True
        if pressed[pygame.K_SPACE]:
            self.paused=False
            self.pend=datetime.datetime.now()
            self.play_duration-=self.pend-self.pstart

    def inplay(self,pressed):
        global jumping
        if pressed[pygame.K_p] or self.paused :
            self.Paused(pressed)
        else:
            self.count+=1
            if pressed[pygame.K_SPACE] or jumping:
                jumping=self.bird.jump(pressed[pygame.K_SPACE])
            else:
                self.bird.change_pos()
            if len(self.obstacles) < 3 and self.count==self.key:
                self.count=0
                self.key=random.randrange(60,120)
                obst=obstacle()
                self.obstacles.append(obst)
            for obst in self.obstacles:
                obst.move()
                pos=obst.getpos()
                if collision(self.bird.getpos(),(29,20),pos,(52,320)) or self.bird.getpos()[1]+20>height-112:
                    self.redraw()
                    self.endgame()
                    break
                if pos[0]+52<100 and pos[0]+52>=100-speed:
                    self.score+=1
                if pos[0]<= -52:
                    self.obstacles.remove(obst)
        self.redraw()

    def endgame(self):
        self.end=True
        self.endtime=datetime.datetime.now()
        time.sleep(0.8)

    def redraw (self):
        self.bird.draw()
        for obst in self.obstacles:
            obst.draw() 
    def ended(self):
        return self.end

class user :
    def __init__(self):
        self.name=input("Enter player name:")
        #check if user already exists
        if self.name in usernames:
            self.playerId,self.Age,self.Highscore=Player_data[self.name]
            print(self.playerId,self.Age,self.Highscore)
        else:
            self.playerId= random.randrange(1000000,10000000)
            self.Age=input("Enter player age:")
            self.Highscore=0
            Player_data[self.name]=(self.playerId,self.Age,self.Highscore)
        self.game=Gameplay()
        self.count=0

    def result(self,key):
        self.game.Quit()
        game_over=pygame.image.load("gameover.png")
        screen.blit(game_over,(width//2-96,height//2-80))
        text=Text()
        text.write("SCORE:%d"%(self.game.score),width//2-36,height//2-20)
        if self.Highscore<self.game.score:
            self.Highscore=self.game.score
            Player_data[self.name]=(self.playerId,self.Age,self.Highscore)
        text.write("Highscore:%d"%self.Highscore,width//2-45,height//2)

    def play(self,pressed):
        if not self.game.ended():
            self.game.inplay(pressed)
            text=Text(20)
            text.write("SCORE:%d"%(self.game.score),5,5)
        else:
            self.result(pressed[pygame.K_SPACE])
            if pressed[pygame.K_SPACE]:
                self.count+=1
                if self.count==3:
                    self.resume(pressed)
                    self.count=0
            if pressed[pygame.K_q] or pressed[pygame.K_ESCAPE]:
                global flag
                flag=False
        
    def resume (self,pressed):
        self.game=Gameplay()
        self.play(pressed)

    
class Admin(user):
    def __init__(self):
        user.__init__(self)
        self.users=len(usernames)

    def add_user(self):
        new_palyer= user()
        self.users+=1

    def rm_user (self, player):
        del(Player_data[player])
        self.users-=1

    def performance(self):
         pass

class obstacle :
    def __init__(self):
        self.x=width
        self.gap=random.randrange(90,130)
        if args.admin:
            self.gap=150
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
        if birdtype== "default":
            self.up=pygame.image.load("up.png")
            self.mid=pygame.image.load("mid.png")
            self.down=pygame.image.load("down.png")
            
    def getpos(self):
        return (self.x,self.y)

    def change_pos(self):
        self.y+=4.5
        self.count+=1
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
            return True
        else:
            self.jumpheight=6
            return False

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

def collision(bcord,bdim,ocord,odim):
    if bcord[0]+bdim[0]>ocord[0] and bcord[0]+5< ocord[0]+odim[0]:
        if not(bcord[1]+5>ocord[2]+odim[1] and bcord[1]+bdim[1]<ocord[1]):
            return True

width=288
height=512
pickle_in= open("Player.pickle","rb")
Player_data=pickle.load(pickle_in)
pickle_in.close()
usernames=Player_data.keys()
speed=3
jumping =False
flag=True

def main():
    decstr="""Flappy Bird Game:\n
    Press SPACE to JUMP/RESUME\n
    Press P to PAUSE\n
    Press Q/ESC to QUIT"""
    parser=argparse.ArgumentParser(description=decstr)
    parser.add_argument("--admin","-a",action="store_true",required=False)
    global args
    args=parser.parse_args()
    done = False
    global flag
    while not done:
        flag=True
        pygame.init()
        if args.admin:
            player=Admin()
            while True:
                cmnd=input("\nWhat would you like to do?\n1)Remove user\n2)Add user\n3)Play\n4)Quit\nCommand:")
                print("\n")
                cmnd=int(cmnd)
                if cmnd==1:
                    for username in usernames:
                        print(username)
                    player.rm_user(input("Username:"))
                if cmnd==2:
                    for username in usernames:
                        print(username)
                    player.add_user()
                if cmnd==3:
                    break
                if cmnd==4:
                    done=True
                    flag=False
                    break
        else:
            player= user()
        global screen
        pygame.display.set_caption('Flappy Bird')
        screen = pygame.display.set_mode((width,height))
        pygame.mixer.music.load('Eminem - Godzilla (Lyrics) ft. Juice WRLD.mp3')
        pygame.mixer.music.play(-1)
        bg=pygame.image.load("background.png")
        ground=pygame.image.load("ground.png")
        start_img=pygame.image.load("gamestart.png")
        clock=pygame.time.Clock()
        started=False
        x=0
        while (not done) and flag:
            for event in pygame.event.get():
                if event.type== pygame.QUIT:
                    done =True
                    flag=False
            screen.blit(bg,(0,0))
            if (not started):
                screen.blit(start_img,(184-width//2+10,267-height//2))
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE]:
                started=True
            if started:
                player.play(pressed)
            x-=speed
            if x<=width-336:
                x=0
            screen.blit(ground,(x,height-112))
            pygame.display.update()
            clock.tick(60)

        pygame.display.quit()
        pygame.quit()
        pygame.quit()
    pickle_out=open("Player.pickle","wb")
    pickle.dump(Player_data,pickle_out)
    pickle_out.close()

if __name__ == '__main__':
    main()