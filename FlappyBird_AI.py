import numpy as np
import random
import pygame 
from tensorflow import keras
import copy
import os
import pickle
import argparse

seed=10
random.seed(seed)
size=38
width=288
height=512
speed=3
bdim=(33,23)
odim=(52,320)
population=[]
max_score=0
score=[]

class machine:
    def __init__(self):
        self.score=0
        self.bird=Bird()
        self.frames=0
        self.fitness=0
        self.model = keras.Sequential()
        self.activate_model()
    #if bird is alive, the model continues to play
    #when the bird dies fitness score is calculated and saved
    def play(self,pos):
        if self.bird.alive:
            self.frames+=1
            input=np.array([self.bird.getpos()[1],pos[0]-self.bird.getpos()[0],pos[1]])
            input=np.reshape(input,(1,input.size))
            if self.model.predict(input)<=0.5:
                self.bird.jump(True)
            else:
                self.bird.change_pos()
            self.bird.draw()

    def activate_model(self):
        self.model.add(keras.layers.Dense(7, input_shape=(3,),activation='relu'))
        self.model.add(keras.layers.Dense(1,activation="sigmoid"))
        sgd = keras.optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        self.model.compile(loss="mean_squared_error", optimizer=sgd, metrics=["accuracy"])

    def inc_score(self):
        if self.bird.alive:
            self.score+=1
            self.frames=0

    def death(self):
        self.bird.alive=False
        self.fitness=self.score+(self.frames/100)

    def reset(self):
        self.score=0
        self.bird=Bird()
        self.frames=0
        self.fitness=0

class obstacle :
    def __init__(self):
        self.x=width
        #define a gap between the pipes and create it
        self.gap=random.randrange(90,130)
        self.y1=random.randrange(45+self.gap,height-(112+31))
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
        self.jumping=False
        if birdtype== "default":
            self.up=pygame.image.load("up.png")
            self.mid=pygame.image.load("mid.png")
            self.down=pygame.image.load("down.png")
            
    def getpos(self):
        return (self.x,self.y)

    def change_pos(self):
        if self.jumping:
            self.jump()
        else:
            self.y+=4.5
            self.count+=1
            #count is used only to animate the bird
            if self.count>= 12:
                self.count=0

    def jump(self,key=False):
        if key:
            self.jumpheight=4
        if self.jumpheight>=0 and self.y>0:
            self.y-=(self.jumpheight**2)*0.55
            self.jumpheight-=1
            if self.count>= 12:
                self.count=0
            self.jumping=True
        else:
            self.jumpheight=4
            self.jumping=False

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
    if bcord[0]+bdim[0]>=ocord[0] and bcord[0]<= ocord[0]+odim[0]:
        if bcord[1]<=ocord[2]+odim[1] or bcord[1]+bdim[1]>=ocord[1]:
            return True

def init_pop(size):
    global population
    population=[]
    for i in range(size):
        member= machine()
        population.append(member)

def new_pop(size):
    new_weights=[]
    count=0
    old_population = []
    global population
    # selecting two parents and initiating crossover and mutation
    for i in range(size//2):
        parent1 = random.uniform(0, 1)
        parent2 = random.uniform(0, 1)
        idx1 = -1
        idx2 = -1
        for idxx in range(len(score)):
            if score[idxx] >= parent1:
                idx1 = idxx
                break
        for idxx in range(len(score)):
            if score[idxx] >= parent2:
                idx2 = idxx
                break
        child1_weights,child2_weights = crossover(idx1,idx2)
        child1_weights = mutate(child1_weights)
        child2_weights = mutate(child2_weights)
        new_weights.append(child1_weights)
        new_weights.append(child2_weights)
    #picking good genes from last generation
    for i in range(len(population)):
        for j in range(0,len(population)-i-1):
            if population[j+1].fitness>population[j].fitness:
                population[j],population[j+1]=population[j+1],population[j]
    for i in range(5):
        weight=population[i].model.get_weights()
        member=machine()
        member.model.set_weights(weight)
        old_population.append(member) 
    #updating population and removing previous members
    for select in range(len(new_weights)):
        population[select].model.set_weights(new_weights[select])
        population[select].reset()

    for select in range(len(new_weights),len(population)):
        obj=population.pop()
        del(obj)
    population.extend(old_population) 

def mutate(weights):
    for i in range(4):
        for j in range(weights[i].shape[0]):
            #try because weights[1],weights[3] are 1D array
            try:
                for k in range(weights[i].shape[1]):
                    if random.uniform(0,1)<=0.1:
                        weights[i][j,k]*=1.3
                    elif random.uniform(0,1)<=(1/9.0):
                        weights[i][j,k]/=1.3
            except:
                if random.uniform(0,1)<=0.1:
                    weights[i][j]*=1.3
                elif random.uniform(0,1)<=(1/9.0):
                    weights[i][j]/=1.3
    return weights


def crossover(idx1,idx2):
    parent1_weights=population[idx1].model.get_weights()
    parent2_weights=population[idx2].model.get_weights()
    weights1=copy.deepcopy(parent1_weights)
    weights2=copy.deepcopy(parent2_weights)
    #randomly interchange some nodes btw the networks
    for i in range(0,4,2):
        for j in range(parent1_weights[i].shape[1]):
            if random.uniform(0,1)>0.5:
                weights1[i][:,j]=parent2_weights[i][:,j]
                weights2[i][:,j]=parent1_weights[i][:,j]
                weights1[i+1][j]=parent2_weights[i+1][j]
                weights2[i+1][j]=parent1_weights[i+1][j]
    return weights1,weights2


def fitness():
    #the function starts the game and each machine tries to score
    #the game ends when all birds have died
    pygame.init()
    global screen
    pygame.display.set_caption('Flappy Bird AI')
    screen = pygame.display.set_mode((width,height))
    bg=pygame.image.load("background.png")
    ground=pygame.image.load("ground.png")
    start_img=pygame.image.load("gamestart.png")
    clock=pygame.time.Clock()
    x=0
    count=0
    key=random.randrange(60,100)
    done=False
    global population
    obstacles=[]
    while not done:
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                done =True
        count+=1
        #for moving ground
        x-=speed
        if x<=width-336:
            x=0
        screen.blit(bg,(0,0))
        for obst in obstacles:
            obst.draw() 
        screen.blit(ground,(x,height-112))
        #add obstacles to the game
        if len(obstacles) < 3 and count==key:
            count=0
            key=random.randrange(60,100)
            obst=obstacle()
            obstacles.append(obst)
        if len(obstacles)==0:
            count=0
            key=random.randrange(60,100)
            obst=obstacle()
            obstacles.append(obst)
        #move and remove the obstacles
        for obst in obstacles:
            obst.move()
            pos=obst.getpos()
            if pos[0]<= -odim[0]:
                obstacles.remove(obst)
        #find obstacle to deal with first
        index=0
        for i in range(len(obstacles)):
            if obstacles[i].getpos()[0]+odim[0]>=100:
                index=i
                break
        pos=obstacles[index].getpos()
        #move every bird,check for collision,increase the score of birds
        global population
        for member in population:
            member.play(pos)
            if collision(member.bird.getpos(),pos):
                member.death()
            if pos[0]+odim[0]<=100+speed and pos[0]+odim[0]>100:
                member.inc_score()
        #check if any bird is left
        flag=True
        for member in population:
            if member.bird.alive:
                flag=False
        if flag:
            done=True
        pygame.display.update()
        clock.tick(60)
    pygame.display.quit()
    total_fitness=0
    global score
    score=[]
    for member in population:
        total_fitness += member.fitness
    #find maximum score in the generation
    for select in range(len(population)):
        score.append(population[select].fitness)
    global max_score
    max_score=max(score)
    #manipulating score for use in selection
    score=[]
    for select in range(len(population)): 
        score.append(population[select].fitness/total_fitness)
        if select > 0:
            score[select] +=score[select-1]
    return

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--trial","-t",action="store_true",required=False)
    args=parser.parse_args()
    global population
    if args.trial:
        pickle_in= open("Weights.pickle","rb")
        weights=pickle.load(pickle_in)
        pickle_in.close()
        for weight in weights:
            member=machine()
            member.model.set_weights(weight)
            population.append(member)
        fitness()
        os.system('cls||echo -e \\\\033c')
        return
    init_pop(size)
    fitness()
    os.system('cls||echo -e \\\\033c')
    print("GEN 0 completed,max score:%0.2f"%(max_score))
    for k in range(7): 
        new_pop(size)
        fitness()
        print("GEN %d completed,max score:%0.2f"%(k+1,max_score))
    choice=input("Save program?:")
    if  choice=="s":
        pickle_in= open("Weights.pickle","rb")
        weights=pickle.load(pickle_in)    
        for member in population:
            if member.fitness ==max_score:
                weights.append( member.model.get_weights())
        pickle_out=open("Weights.pickle","wb")
        pickle.dump(weights,pickle_out)
        pickle_out.close()

if __name__ == '__main__':
    main()