import struct
import random 
import math
import time

def generatePhenotype(min, max):
    return random.uniform(min,max)

def float_to_bin(num):
    return bin(struct.unpack('!I', struct.pack('!f', num))[0])[2:].zfill(32)

def bin_to_float(binary):
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]
    
def to_chromosomeXY(x, y): # 64 bits
    return x+y

def createPopulation(population_, max): # bikin populasi acak
    i = len(population_)
    while(i != max):
        d = dict()
        d['c'] = to_chromosomeXY(float_to_bin(generatePhenotype(-5,5)),float_to_bin(generatePhenotype(-5,5)))
        d['x'] = bin_to_float(d['c'][0:32])
        d['y'] = bin_to_float(d['c'][32:64])
        d['v'] = formula(d['x'],d['y'])
        population_.append(d)

        i += 1
    return population_

def crossover(population, max_population): # diambil salah satu kromosom dari populasi dengan i, lalu di crossover dengan kromosom lainnya
    list_cross = stochasticWheel(max_population, 5) #population already sorted
    # [3, 5]
    length = len(population[0]['c'])
    a = random.randint(0, (length-1))
    b = random.randint(a, (length-1))
    buffer1 = population[list_cross[0]]['c'][a:b] # target2
    buffer2 = population[list_cross[1]]['c'][a:b] # target1
    population[list_cross[0]]['c'] = population[list_cross[0]]['c'][0:a] + buffer2 + population[list_cross[0]]['c'][b:64]
    population[list_cross[1]]['c'] = population[list_cross[1]]['c'][0:a] + buffer1 + population[list_cross[1]]['c'][b:64]
    population[list_cross[0]]['x'] = bin_to_float(population[list_cross[0]]['c'][0:32]) # re-calculate x
    population[list_cross[1]]['y'] = bin_to_float(population[list_cross[1]]['c'][32:64]) # re-calculate y
    return population # v will be re-calculate in fitness

def stochasticWheel(length, k_value): # probabilitas atau parent selection
    weight = [] # chances
    priority = [] # index
    for i in range(1, length+1):
        weight.append((i/length)) 
        priority.append(i-1)
    # weight will be looks like this [1/length,2/length,3/length,......,n/length]
    # priority will be looks like this [0, 1, 2, 3, 4,...., length]
    #[0, 1, 2, 3, 4, 5]
    #[1/6, 2/6, ......]
    return (random.choices(priority, weights=weight, k=k_value))
#
def formula(x,y):
    return(((math.cos(x) + math.sin(y))*(math.cos(x) + math.sin(y)))/((x*x) + (y*y) + 0.00000000000000001))
 
def fitness(popu, max_pop): # masukin nilai x, y buat dapet nilai v
    global r
    for i in range(0, max_pop):
        data = popu[i]['c']
        x = data[0:32]
        y = data[32:64]    
        x, y = bin_to_float(x), bin_to_float(y)
        if(((x < -5) or (x > 5)) or ((y < -5) or (y > 5))):
            #print("Remake")
            data = to_chromosomeXY(float_to_bin(generatePhenotype(-5,5)),float_to_bin(generatePhenotype(-5,5)))
            x = data[0:32]
            y = data[32:64]
            x, y = bin_to_float(x), bin_to_float(y)
            r += 1
        
        d = dict()
        d['v'] = formula(x,y)
        d['c'] = data
        d['x'] = x
        d['y'] = y
        popu[i] = d
    return popu

def mutation(population, max_population):
    length = len(population[0]['c'])
    a = stochasticWheel(max_population, 5)[0]
    rand = random.randint(0, length-2)
    if population[a]['c'][rand] == '0':
        population[a]['c'] = population[a]['c'][:rand] + '1' + population[a]['c'][rand:]
    else:
        population[a]['c'] = population[a]['c'][:rand] + '0' + population[a]['c'][rand:]
    population[a]['x'] = bin_to_float(population[a]['c'][0:32]) # re-calculate x
    population[a]['y'] = bin_to_float(population[a]['c'][32:64]) # re-calculate y
    return population # v will be re-calculate in fitness
   
def chrom_evaluation(population): # sorting and replace the bad one (last index)
    x = generatePhenotype(-5,5)
    y = generatePhenotype(-5,5)
    population[-1]['c'] = to_chromosomeXY(float_to_bin(x),float_to_bin(y)) # Replace the bad one
    population[-1]['x'] = x
    population[-1]['y'] = y
    population[-1]['v'] = formula(x,y)
    population = sorting_value(population)
    return population

def survivor(last, population):
    if population[0]['v'] > last['v']:
        #print(f'Take last {last}\nCurrent {population[0]}')
        population[0] = last
    #else:
        #print(f'Take Current {population[0]}\nlast {last}')
    return population

def sorting_value(value): # sorting dari yg paling dekat 0
    value = sorted(value, key=lambda i: abs(i['v'])-0)
    return value

def evolution(initial_population, max_population : int, max_generation : int):
    global all_generation, r
    evaluate = initial_population
    last = initial_population[0]
    m = 0
    c = 0
    evaluate = sorting_value(evaluate)
    for x in range(0, max_generation):
        #print(f'UNFIX : {evaluate[0]}')
        if(random.choices([0,1], weights=[0.9,0.1], k=5)[0] == 0):
            c += 1
            evaluate = crossover(evaluate, max_population)
        if(random.choices([0,1], weights=[0.9,0.1], k=5)[0] == 1):
            m += 1
            evaluate = mutation(evaluate, max_population)
        evaluate = fitness(evaluate, max_population)
        evaluate = chrom_evaluation(evaluate)
        evaluate = survivor(last, evaluate)
        # isi sama mutasi
        # evaluation = ...........
        result = evaluate[0]
        print(f'\nGeneration {x+1}: \n{result}')
        print('{0:.100f}'.format(result['v']))
        last = result
        all_generation.append(last)

    print(f'\nCrossover = {c}\nMutation = {m}\nRemake = {r}')
    return last

def visualization_2d(): # visualize the generation growth in 2d
    global all_generation
    import matplotlib.pyplot as plt
    #x =[]
    #for i in total_simulation: x.append(i['x'])
    #y =[]
    #for i in total_simulation: y.append(i['y'])
    z =[]
    for i in all_generation: z.append(i['v'])
    i = []
    for v in range(0, max_gen): i.append(v+1)
    xdata = i
    ydata = z
    plt.plot(xdata, ydata)
    plt.title("Fitness Growth")
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness")
    plt.annotate('Minimum', xy=(xdata[-1],ydata[-1]), arrowprops=dict(facecolor='black', shrink=0.05))
    plt.show()

if __name__=="__main__":
    r = 0
    population = []
    all_generation = []
    max_pop = 6 # max kromosom dalam 1 populasi
    max_gen = 80 # max generasi
    population = createPopulation(population, max_pop)
    print(population)
    #print(f'Contoh Data-nya : {population[0]}\n\n')
    print('--------------------SIMULATION BEGIN!--------------------------')
    start = time.time()
    final_population = evolution(population, max_pop, max_gen)
    end = time.time()
    round_value = '{0:.100f}'.format(final_population['v'])
    print('--------------------SIMULATION STOP!---------------------------')

    print(f'Data Representation Example :\n{final_population}\nv = Heuristic value\nc = Chromosome\nx = X Value\ny = Y value')
    print(f"""\nConfiguration Details :
The amount of population per-generation = {max_pop}
Total Generation = {max_gen}
Domain Range = (-5 to 5)
Binary Precision = 64 bits""")
    print(f"""--------------------Smallest is-------------------------------
X = {final_population['x']} Y = {final_population['y']}
Binary : {final_population['c']}
Value : {final_population['v']}\nValue Rounded : {round_value} \n\nTime Duration = {end-start}s""")
    visualization_2d()