from model import *
from SolutionDrawer import *

class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []


class CustomerInsertion(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.cost = 10 ** 9

class RelocationMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = None

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9

class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9

class TwoOptMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = 10 ** 9


class Solver:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None
        self.searchTrajectory = []

    def solve(self):
        self.SetRoutedFlagToFalseForAllCustomers()
        self.ApplyNearestNeighborMethod()
        self.ReportSolution(self.sol)
        self.VND()
        # self.LocalSearch(2)
        self.ReportSolution(self.sol)
        self.BetterSolution(0)
        self.ReportSolution(self.sol)
        self.BetterSolution(1)
        self.ReportSolution(self.sol)
        return self.sol

    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False


    def ApplyNearestNeighborMethod(self):
        modelIsFeasible = True
        self.sol = Solution()
        for i in range(0,26):         
            rt = Route(self.depot, self.capacity)
            self.sol.routes.append(rt)
        insertions = 0

        while (insertions < len(self.customers)):
            bestInsertion = CustomerInsertion()

            self.IdentifyBestInsertion(bestInsertion)

            if (bestInsertion.customer is not None):
                self.ApplyCustomerInsertion(bestInsertion)
                insertions += 1

        self.TestSolution()


    def IdentifyBestInsertion(self, best_insertion):
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                for rt in self.sol.routes:
                    if rt.load + candidateCust.demand <= rt.capacity:
                            lastNodePresentInTheRoute = rt.sequenceOfNodes[-2]
                            # Cost removed is zero because the cost of a vehicle the way back to depository is zero
                            costAdded = self.distanceMatrix[lastNodePresentInTheRoute.ID][candidateCust.ID]
                            trialCost = costAdded 
                            if trialCost < best_insertion.cost:
                                best_insertion.customer = candidateCust
                                best_insertion.route = rt
                                best_insertion.cost = trialCost 
                    else:
                        continue


    def ApplyCustomerInsertion(self, insertion):  
        insCustomer = insertion.customer
        rt = insertion.route
        #before the second depot occurrence
        insIndex = len(rt.sequenceOfNodes) - 1 
        rt.sequenceOfNodes.insert(insIndex, insCustomer) 

        beforeInserted = rt.sequenceOfNodes[-3] 

        costAdded = self.distanceMatrix[beforeInserted.ID][insCustomer.ID] #+ self.distanceMatrix[insCustomer.ID][self.depot.ID]
        # costRemoved = self.distanceMatrix[beforeInserted.ID][self.depot.ID] # We do not need to calculate the distance from the last node to deposit
        costRemoved = 0 
        rt.cost += costAdded - costRemoved
        self.sol.cost += costAdded - costRemoved

        rt.load += insCustomer.demand

        insCustomer.isRouted = True


    def ReportSolution(self, sol):
            max_cost=0
            for i in range(0, len(sol.routes)):
                rt = sol.routes[i]
                for j in range (0, len(rt.sequenceOfNodes)):
                    print(rt.sequenceOfNodes[j].ID, end=' ')
                print(rt.cost)
                trial_cost = rt.cost
                if trial_cost > max_cost:
                    max_cost = trial_cost
            print ('Total time is:', self.sol.cost)
            print ('Max time is:', max_cost)

################################ End of Nearest Neighbor method ################################
# The main idea is the systematic change of the move type (e.g. relocation, swap, twoopt) during the search in the solution space.
# transition from one solution to another using specific moves

################################ LOCAL SEARCH FUNCTIONS #########################################
# will be used after the termination of VND in order to try improve our best solution doing changes only in the route with the maximum cost each time
    
    def BetterSolution(self, operator):
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        BetterSearchIterator =0
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        # self.InitializeOperators(rm, sm, top)
        RMCostmove = rm.moveCost 
        SMCostmove = sm.moveCost 
        iter=0
        while terminationCondition is False:

                self.InitializeOperators(rm, sm, top)
                SolDrawer.draw(BetterSearchIterator, self.sol, self.allNodes)  

                if operator == 0:
                    self.BestReloc(rm)
                    if rm.originRoutePosition is not None:
                        if rm.moveCost != RMCostmove:
                            RMCostmove = rm.moveCost
                            iter+=1
                            self.ApplyRelocationMove(rm)
                            if iter ==10: 
                                terminationCondition = True
                        else:
                            terminationCondition = True

                elif operator == 1:
                    self.BestSwap(sm)
                    if sm.positionOfFirstRoute is not None:
                        if sm.moveCost != SMCostmove:
                            SMCostmove = sm.moveCost
                            self.ApplySwapMove(sm)
                            iter +=1
                            if iter == 20:
                                terminationCondition =True
                        else:
                            terminationCondition = True
                    else: 
                        terminationCondition = True 
                        print("No improvement using Swaps")

                self.TestSolution()
                print("new max cost", self.GetMaximumCost(self.sol))
                print("last best max cost",self.GetMaximumCost(self.bestSolution) )
                if (self.GetMaximumCost(self.sol) < self.GetMaximumCost(self.bestSolution)):
                    self.bestSolution = self.cloneSolution(self.sol)

                BetterSearchIterator = BetterSearchIterator + 1
                print(BetterSearchIterator, self.sol.cost)

        self.sol = self.bestSolution

    def BestReloc(self,rm):
                mc=0
                for i in range(0, len(self.sol.routes)):
                    route = self.sol.routes[i]
                    trialmc = route.cost                   
                    if trialmc > mc:
                        mc = trialmc
                        originRouteIndex = i 
                    # Take its time as rt1 the route with the maximum cost     
                    rt1:Route = self.sol.routes[originRouteIndex]
                    for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):

                        for targetRouteIndex in range (0, len(self.sol.routes)):
                            rt2:Route = self.sol.routes[targetRouteIndex]
                            for targetNodeIndex in range (0, len(rt2.sequenceOfNodes) - 1):

                                if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex 
                                                                            or targetNodeIndex == originNodeIndex - 1):
                                    continue

                                A = rt1.sequenceOfNodes[originNodeIndex - 1]
                                B = rt1.sequenceOfNodes[originNodeIndex]
                                C = rt1.sequenceOfNodes[originNodeIndex + 1]

                                F = rt2.sequenceOfNodes[targetNodeIndex]
                                G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                                if rt1 != rt2:
                                    if rt2.load + B.demand > rt2.capacity:
                                        continue

                                costAdded = self.distanceMatrix[A.ID][C.ID] + self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID]
                                costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[B.ID][C.ID] + self.distanceMatrix[F.ID][G.ID]

                                originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - self.distanceMatrix[B.ID][C.ID]
                                targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - self.distanceMatrix[F.ID][G.ID]

                                moveCost = costAdded - costRemoved

                                if (originRtCostChange < 0):
                                    self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm)


    def BestSwap(self, sm):
            mc=0
            for i in range(0, len(self.sol.routes)):
                route = self.sol.routes[i]
                trialmc = route.cost                   
                if trialmc > mc:
                    mc = trialmc  
                    firstRouteIndex = i 
                # Take its time as rt1 the route with the maximum cost     
                rt1:Route = self.sol.routes[firstRouteIndex]
                for firstNodeIndex in range (1, len(rt1.sequenceOfNodes) - 1):
                    # first swapped node is cdetermined
                    for secondRouteIndex in range(firstRouteIndex, len(self.sol.routes)):
                        rt2: Route = self.sol.routes[secondRouteIndex]
                        startOfSecondNodeIndex = 1
                        if rt1 == rt2:
                            startOfSecondNodeIndex = firstNodeIndex + 1
                        for secondNodeIndex in range (startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                            a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                            b1 = rt1.sequenceOfNodes[firstNodeIndex]
                            c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                            a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                            b2 = rt2.sequenceOfNodes[secondNodeIndex]
                            c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                            moveCost = None
                            costChangeFirstRoute = None
                            costChangeSecondRoute = None

                            if rt1 == rt2:
                                if firstNodeIndex == secondNodeIndex - 1:
                                    # case of consecutive nodes swap
                                    costRemoved = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][b2.ID] + \
                                                self.distanceMatrix[b2.ID][c2.ID]
                                    costAdded = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][b1.ID] + \
                                                self.distanceMatrix[b1.ID][c2.ID]
                                    moveCost = costAdded - costRemoved
                                    costChangeFirstRoute = moveCost
                                    costChangeSecondRoute = moveCost                                    
                                else:

                                    costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                    costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                                    costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                    costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                                    moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                                    costChangeFirstRoute = moveCost
                                    costChangeSecondRoute = moveCost          
                            else:
                                if rt1.load - b1.demand + b2.demand > self.capacity:
                                    continue
                                if rt2.load - b2.demand + b1.demand > self.capacity:
                                    continue

                                costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                                costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]

                                costChangeFirstRoute = costAdded1 - costRemoved1
                                costChangeSecondRoute = costAdded2 - costRemoved2

                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                            if (costChangeFirstRoute < 0 ):
                                self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                    moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)


    def LocalSearch(self, operator):
            self.bestSolution = self.cloneSolution(self.sol) 
            terminationCondition = False
            localSearchIterator = 0

            rm = RelocationMove()
            sm = SwapMove()
            top = TwoOptMove()

            while terminationCondition is False:

                self.InitializeOperators(rm, sm, top)
                # SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

                # Relocations
                if operator == 0:
                    self.FindBestRelocationMove(rm)
                    if rm.originRoutePosition is not None:
                        if rm.moveCost < 0:
                            self.ApplyRelocationMove(rm)
                        else:
                            terminationCondition = True
                # Swaps
                elif operator == 1:
                    self.FindBestSwapMove(sm)
                    if sm.positionOfFirstRoute is not None:
                        if sm.moveCost < 0:
                            self.ApplySwapMove(sm)
                        else:
                            terminationCondition = True
                # 2Opt
                elif operator == 2:
                    self.FindBestTwoOptMove(top)
                    if top.positionOfFirstRoute is not None:
                        if top.moveCost < 0:
                            print(top.moveCost)
                            self.ApplyTwoOptMove(top)
                        else:
                            terminationCondition = True

                self.TestSolution()
                print("new max cost", self.GetMaximumCost(self.sol))
                print("last best max cost",self.GetMaximumCost(self.bestSolution) )
                if (self.sol.cost < self.bestSolution.cost and self.GetMaximumCost(self.sol) < self.GetMaximumCost(self.bestSolution)):
                    self.bestSolution = self.cloneSolution(self.sol)

                localSearchIterator = localSearchIterator + 1
                print(localSearchIterator, self.sol.cost)

            self.sol = self.bestSolution

    def GetMaximumCost(self, sol):
        max_cost = 0
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            if max_cost < rt.cost:
                max_cost = rt.cost
        return(max_cost)

    def cloneSolution(self, sol: Solution):
            cloned = Solution()   
            for i in range (0, len(sol.routes)):
                rt = sol.routes[i]
                clonedRoute = self.cloneRoute(rt)
                cloned.routes.append(clonedRoute)
            cloned.cost = self.sol.cost
            return cloned

    def cloneRoute(self, rt:Route):
            cloned = Route(self.depot, self.capacity)
            cloned.cost = rt.cost
            cloned.load = rt.load
            cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
            return cloned

    def InitializeOperators(self, rm, sm, top):
        rm.Initialize()
        sm.Initialize()
        top.Initialize()
 
########### RELOCATION MOVES ###########

    def FindBestRelocationMove(self, rm):
                mc=0
                for i in range(0, len(self.sol.routes)):
                    route = self.sol.routes[i]
                    trialmc = route.cost                   
                    if trialmc > mc:
                        mc = trialmc  
                for originRouteIndex in range(0, len(self.sol.routes)):
                    rt1:Route = self.sol.routes[originRouteIndex]
                    for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):

                        for targetRouteIndex in range (0, len(self.sol.routes)):
                            rt2:Route = self.sol.routes[targetRouteIndex]
                            for targetNodeIndex in range (0, len(rt2.sequenceOfNodes) - 1):

                                if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex 
                                                                            or targetNodeIndex == originNodeIndex - 1):
                                    continue

                                A = rt1.sequenceOfNodes[originNodeIndex - 1]
                                B = rt1.sequenceOfNodes[originNodeIndex]
                                C = rt1.sequenceOfNodes[originNodeIndex + 1]

                                F = rt2.sequenceOfNodes[targetNodeIndex]
                                G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                                if rt1 != rt2:
                                    if rt2.load + B.demand > rt2.capacity:
                                        continue

                                costAdded = self.distanceMatrix[A.ID][C.ID] + self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID]
                                costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[B.ID][C.ID] + self.distanceMatrix[F.ID][G.ID]

                                originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - self.distanceMatrix[B.ID][C.ID]
                                targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - self.distanceMatrix[F.ID][G.ID]

                                moveCost = costAdded - costRemoved

                                if (moveCost < rm.moveCost and rt1.cost + originRtCostChange < mc and rt2.cost + targetRtCostChange < mc ):
                                    self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm)

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm:RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    def ApplyRelocationMove(self, rm: RelocationMove):

            oldCost = self.CalculateTotalCost(self.sol) 

            originRt = self.sol.routes[rm.originRoutePosition]
            targetRt = self.sol.routes[rm.targetRoutePosition]

            B = originRt.sequenceOfNodes[rm.originNodePosition]

            if originRt == targetRt:
                del originRt.sequenceOfNodes[rm.originNodePosition]
                if (rm.originNodePosition < rm.targetNodePosition):
                    targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B) 
                else:
                    targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B) 
                originRt.cost += rm.moveCost
            else:
                del originRt.sequenceOfNodes[rm.originNodePosition]
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
                originRt.cost += rm.costChangeOriginRt
                targetRt.cost += rm.costChangeTargetRt
                originRt.load -= B.demand
                targetRt.load += B.demand

            self.sol.cost += rm.moveCost

            newCost = self.CalculateTotalCost(self.sol)
            #debuggingOnly
            if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
                print('Cost Issue')

    def CalculateTotalCost(self, sol):
        c = 0
        for i in range (0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range (0, len(rt.sequenceOfNodes) - 1): 
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                c += self.distanceMatrix[a.ID][b.ID]
        return c

########### SWAP MOVES ##################

    def FindBestSwapMove(self, sm):
            mc=0
            for i in range(0, len(self.sol.routes)):
                route = self.sol.routes[i]
                trialmc = route.cost                   
                if trialmc > mc:
                    mc = trialmc  
            for firstRouteIndex in range(0, len(self.sol.routes)):
                rt1:Route = self.sol.routes[firstRouteIndex]
                for firstNodeIndex in range (1, len(rt1.sequenceOfNodes) - 1):
                    # first swapped node is cdetermined
                    for secondRouteIndex in range(firstRouteIndex, len(self.sol.routes)):
                        rt2: Route = self.sol.routes[secondRouteIndex]
                        startOfSecondNodeIndex = 1
                        if rt1 == rt2:
                            startOfSecondNodeIndex = firstNodeIndex + 1
                        for secondNodeIndex in range (startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                            a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                            b1 = rt1.sequenceOfNodes[firstNodeIndex]
                            c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                            a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                            b2 = rt2.sequenceOfNodes[secondNodeIndex]
                            c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                            moveCost = None
                            costChangeFirstRoute = None
                            costChangeSecondRoute = None

                            if rt1 == rt2:
                                if firstNodeIndex == secondNodeIndex - 1:
                                    # case of consecutive nodes swap
                                    costRemoved = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][b2.ID] + \
                                                self.distanceMatrix[b2.ID][c2.ID]
                                    costAdded = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][b1.ID] + \
                                                self.distanceMatrix[b1.ID][c2.ID]
                                    moveCost = costAdded - costRemoved
                                    costChangeFirstRoute = moveCost
                                    costChangeSecondRoute = moveCost                                    
                                else:

                                    costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                    costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                                    costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                    costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                                    moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                                    costChangeFirstRoute = moveCost
                                    costChangeSecondRoute = moveCost          
                            else:
                                if rt1.load - b1.demand + b2.demand > self.capacity:
                                    continue
                                if rt2.load - b2.demand + b1.demand > self.capacity:
                                    continue

                                costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                                costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]

                                costChangeFirstRoute = costAdded1 - costRemoved1
                                costChangeSecondRoute = costAdded2 - costRemoved2

                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                            if (moveCost < sm.moveCost and rt1.cost + costChangeFirstRoute < mc and rt2.cost + costChangeSecondRoute < mc ):
                                self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                    moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost

    def ApplySwapMove(self, sm):

        oldCost = self.CalculateTotalCost(self.sol)
        rt1 = self.sol.routes[sm.positionOfFirstRoute]
        rt2 = self.sol.routes[sm.positionOfSecondRoute]
        b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
        rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
        rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

        if rt1 == rt2:
            rt1.cost += sm.moveCost
        else:
            rt1.cost += sm.costChangeFirstRt
            rt2.cost += sm.costChangeSecondRt
            rt1.load = rt1.load - b1.demand + b2.demand
            rt2.load = rt2.load + b1.demand - b2.demand

        self.sol.cost += sm.moveCost

        newCost = self.CalculateTotalCost(self.sol)
        # debuggingOnly
        if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
            print('Cost Issue')

########### 2 OPT MOVES ################

    def FindBestTwoOptMove(self, top):
        for rtInd1 in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[rtInd1]
            for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                # first node is determined
                A = rt1.sequenceOfNodes[nodeInd1]
                B = rt1.sequenceOfNodes[nodeInd1 + 1]

                for rtInd2 in range(rtInd1, len(self.sol.routes)):

                    rt2: Route = self.sol.routes[rtInd2]
                    start2 = 0 #inter-route move
                    if rt1 == rt2:
                        start2 = nodeInd1 + 2 #intra-route move
                     
                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):

                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue
                            costAdded = self.distanceMatrix[A.ID][K.ID] + self.distanceMatrix[B.ID][L.ID]
                            costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]
                            moveCost = costAdded - costRemoved

                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and  nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue

                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue
                            costAdded = self.distanceMatrix[A.ID][L.ID] + self.distanceMatrix[K.ID][B.ID]
                            costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]

                            moveCost = costAdded - costRemoved

                        if moveCost < top.moveCost:
                            self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top)

    def CapacityIsViolated(self, rt1, nodeInd1, rt2, nodeInd2):

        rt1FirstSegmentLoad = 0
        for i in range(0, nodeInd1 + 1):
            n = rt1.sequenceOfNodes[i]
            rt1FirstSegmentLoad += n.demand
        rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad

        rt2FirstSegmentLoad = 0
        for i in range(0, nodeInd2 + 1):
            n = rt2.sequenceOfNodes[i]
            rt2FirstSegmentLoad += n.demand
        rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

        if (rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity):
            return True
        if (rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity):
            return True

        return False

    def StoreBestTwoOptMove(self, rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top):
        top.positionOfFirstRoute = rtInd1
        top.positionOfSecondRoute = rtInd2
        top.positionOfFirstNode = nodeInd1
        top.positionOfSecondNode = nodeInd2
        top.moveCost = moveCost

    def ApplyTwoOptMove(self, top):
        rt1:Route = self.sol.routes[top.positionOfFirstRoute]
        rt2:Route = self.sol.routes[top.positionOfSecondRoute]

        if rt1 == rt2:

            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])

            rt1.sequenceOfNodes[top.positionOfFirstNode + 1 : top.positionOfSecondNode + 1] = reversedSegment

            rt1.cost += top.moveCost

        else:

            relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1 :]

            relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1 :]

            del rt1.sequenceOfNodes[top.positionOfFirstNode + 1 :]
            del rt2.sequenceOfNodes[top.positionOfSecondNode + 1 :]

            rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2)
            rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1)

            self.UpdateRouteCostAndLoad(rt1)
            self.UpdateRouteCostAndLoad(rt2)

        self.sol.cost += top.moveCost
     
        self.TestSolution()

    def UpdateRouteCostAndLoad(self, rt: Route):
        tc = 0
        tl = 0
        for i in range(0, len(rt.sequenceOfNodes) - 1):
            A = rt.sequenceOfNodes[i]
            B = rt.sequenceOfNodes[i+1]
            tc += self.distanceMatrix[A.ID][B.ID]
            tl += A.demand 
        rt.load = tl
        rt.cost = tc

    def VND(self):
        self.bestSolution = self.cloneSolution(self.sol)
        VNDIterator = 0
        kmax = 2
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        k = 0
        draw = True

        while k <= kmax:
            self.InitializeOperators(rm, sm, top)
            if k == 2:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                    print("reloc")
                    # if draw:
                        # SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.cost)
                    k = 0
                else:
                    k += 1
            elif k == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None and sm.moveCost < 0:
                    self.ApplySwapMove(sm)
                    print("swap")
                    # if draw:
                        # SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.cost)
                    k = 0
                else:
                    k += 1
            elif k == 0:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None and top.moveCost < 0:
                    self.ApplyTwoOptMove(top)
                    print("2opt")
                    # if draw:
                        # SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.cost)
                    k = 0
                else:
                    k += 1

            print("new max cost", self.GetMaximumCost(self.sol))
            print("last best max cost",self.GetMaximumCost(self.bestSolution))
            if (self.sol.cost < self.bestSolution.cost and self.GetMaximumCost(self.sol) < self.GetMaximumCost(self.bestSolution)):
                self.bestSolution = self.cloneSolution(self.sol)

        SolDrawer.draw('final_vnd', self.bestSolution, self.allNodes)
        SolDrawer.drawTrajectory(self.searchTrajectory)


    def TestSolution(self):
        totalSolCost = 0
        for r in range (0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtCost = 0
            rtLoad = 0
            for n in range (0 , len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtCost += self.distanceMatrix[A.ID][B.ID]
                rtLoad += A.demand 
            if abs(rtCost - rt.cost) > 0.0001:
                print ('Route Cost problem')
                print(abs(rtCost - rt.cost))

            if rtLoad != rt.load:
                print ('Route Load problem')
                print(rtLoad-rt.load)

            totalSolCost += rt.cost

        if abs(totalSolCost - self.sol.cost) > 0.0001:

            print('Solution Cost problem')
            print(totalSolCost)
            print(self.sol.cost)
            raise ValueError("Wrong Cost")
        else:
            print('all ok')