import random
import math


class Model:

# instance variables
    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.matrix = []
        self.capacity = -1

    def BuildModel(self):
        random.seed(5)
        depot = Node(0, 50, 50, 0, 0)                               
        self.allNodes.append(depot)

        self.capacity = 3000                                      
        totalCustomers = 200

        for i in range (0, totalCustomers):                      
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            dem = 100 * (1 + random.randint(1, 4)) # demand in kg 
            unloading_time = 15 # unloading time in minutes
            cust = Node(i + 1, x, y, dem, unloading_time)
            self.allNodes.append(cust)
            self.customers.append(cust)

        rows = len(self.allNodes)                          
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]    

        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                # This is the Time matrix calculated in Hours 
                # We added the unloading time in the Time matrix = 0.25 Hours 
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                if j==0 or i==j:
                    self.matrix[i][j] = 0.0
                else:
                    self.matrix[i][j] = dist/40 + 0.25 
    

class Node:
    def __init__(self, idd, xx, yy, dem, unloading_time):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.demand = dem
        self.unloadingTime = unloading_time
        self.isRouted = False

class Route:
    def __init__(self, dp, cap):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0.0 
        self.capacity = cap
        self.load = 0