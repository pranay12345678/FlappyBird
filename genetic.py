import random
population=[]
n=6
score=[]
cipher="alg fwjoer ht kds fkix kicesi avabbx as unfmpzg bb koi ehagsmethvk epw qfyvwihvk aqkzu vj ekwdl ,pgtrzuk vasd mvqf hyl tqbbk vj yhfbpri yci tspxm kv aqkyzuk vh glyzkos, rsp umoiampz kzal cg vfuium vznl uvvfvp vxotoit mfppri mc dhog fcelc hhf ypw htazsc cyhvy jkgrzuk qnh threxf yhh phh cljv awd tyea hzti"
max_score=cipher.count(' ')
simplified_cipher=cipher.replace(',','')
file=open("wiki-100k.txt")
words=file.read()
def decrypt(key,p=0):
    global simplified_cipher
    global n
    count=0
    score1=0
    text=[]
    word=[]
    for i in range(len(simplified_cipher)):
        if not (simplified_cipher[i]==" "):
            x=(ord(simplified_cipher[i])-ord(key[count%n])+26)%26       
            x+=ord('a')
            x=chr(x)
            count+=1
            word.append(x)
        else:
            w="".join(word)
            if w in words:
                score1+=1
            if p:
                text.append(word)
            word=[]
    if p:
        return text
    return score1

def initial_pop(size):
    global population
    global n
    population=[]
    for j in range(size):
        member=[]
        for i in range(n):
            member.append(chr(random.randrange(97,123)))
        population.append(member)

def fitness():
    global score
    score=[]
    for i in range(len(population)):
        key=population[i]
        score.append(decrypt(key))

def new_pop(size,k):
    global population
    global score
    new_population = []
    for i in range(int(size/2)):
        parent = random.choices(population,weights=[s**2 for s in score],k=2) 
        new_population.append(parent[0][:k]+parent[1][k:])
        new_population.append(parent[1][:k]+parent[0][k:])
    return new_population

def mutation(percentage):
    global population
    for j in range(len(population)):
        for i in range(len(population[j])):
            if(random.uniform(0,1) < percentage):
                population[j][i] = chr(random.randrange(97,123))

def evolve(size):
    global population
    global score
    global n
    initial_pop(size)
    fitness()
    i=1
    key=population[score.index(max(score))]
    for k in range(1000):
        if max(score) == max_score:
            return key
        population = new_pop(size,int(n/2))
        mutation(0.1)
        fitness()
        key=population[score.index(max(score))]
        print("gen:",i,"best:",key,"max score:",max(score))
        i += 1
    return key
print(max_score)
key=evolve(52)
print(*key)
text=decrypt(key,1)
for i in range(len(text)):
    print(*text[i],sep='',end=' ')
