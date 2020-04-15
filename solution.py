import search
import sys

### ASARProblem ###


class ASARProblem(search.Problem):
    "derives from the abstract class search.Problem"

    ### Constructor ###
    def __init__(self):

        self.A = {}             # airports
        self.P = []             # airplane
        self.L = []             # legs
        self.C = {}             # class
        self.initial = []       # initial state

    ### Initialization ###
    def initialization(self):
        "Defines the initial state. Each plane have a list for the airports of departure and arrival, times of departure and legs done"

        for planes in range(len(self.P)):
            aux = []
            aux.append(tuple())                 # for the airports of departure
            aux.append(tuple())                 # for the airports of arrival
            aux.append(tuple())                 # for the times
            aux.append(tuple())                 # for the legs done
            self.initial.append(tuple(aux))
        self.initial.append((0.0))
        self.initial = tuple(self.initial)

        return None

    ### Actions ###
    def actions(self, state):
        "returns a list (or a generator) of operators applicable to state s"

        allowed_actions = []
        done = []
        no_fly = 0

        state = list(state)
        for i in range(len(state)-1):
            state[i] = list(state[i])
            done += state[i][3]         # list of all the legs already done

        # Haven't occured flights
        if done == []:
            allowed_actions = self.noLegDone()  # list of actions applicable to the actual state

        # Have occured flights
        else:
            all_legs = range(len(self.L))
            undone_legs = list(set(all_legs).difference(done))   # indexes of the legs that haven't been done
            allowed_actions = self.legsDone(state, undone_legs)  # list of actions applicable to the actual state

        return allowed_actions

    ###  NoLegDone ###
    def noLegDone(self):
        "returns a list of allowed actions in the case that no legs have yet been done"

        allowed_actions = []
        # checks all legs
        for i in range(len(self.L)):
            # each leg can be done by various planes
            for j in range(len(self.C)):
                # verifies if the flight is possible in terms of oppening and closing airports times
                if self.check_fly(self.A[self.L[i][j][2]][0], self.A[self.L[i][j][1]][0], self.L[i][j][3], self.A[self.L[i][j][2]][1], self.C[self.L[i][j][4]]):
                    plane = self.L[i][j][4]
                    # search for a valid plane to do the action
                    for k in range(len(self.P)):
                        if plane in self.P[k]:
                            allowed_actions.append(self.L[i][j]+[k])
                            break

        return allowed_actions

    ### LegsDone ###
    def legsDone(self, state, undone):
        "returns a list of allowed actions when at least one leg have already been done"

        allowed_actions = []

        state = list(state)
        for i in range(len(state)-1):
            state[i] = list(state[i])
       
        # checks all undone legs
        for i in undone:
            plane = []
            # each leg can be done by various planes
            for j in range(len(self.P)):
                # if a plane of the same model have already got the same leg to do
                if self.P[j][1] in plane:
                    continue
                # different classes of planes in the legs
                for x in range(len(self.C)):
                    # verifies if is the correct plane for that action
                    if self.L[i][x][4] == self.P[j][1]:
                        state[j][1] = list(state[j][1])
                        # verifies if the plane haven't flight yet
                        if state[j][1] == []:
                            # verifies if the flight is possible in terms of oppening and closing airports times
                            if self.check_fly(self.A[self.L[i][x][2]][0], self.A[self.L[i][x][1]][0], self.L[i][x][3], self.A[self.L[i][x][2]][1], self.C[self.L[i][x][4]]):
                                plane.append(self.P[j][1])
                                allowed_actions.append(self.L[i][x]+[j])

                        # # verifies if the plane is in the correct airport
                        elif state[j][1][-1] == self.L[i][x][1]:
                            state[j][2] = list(state[j][2])
                            # verifies if the flight is possible in terms of oppening and closing airports times
                            if self.check_fly(self.A[self.L[i][x][2]][0], state[j][2][-1], self.L[i][x][3], self.A[self.L[i][x][2]][1], self.C[self.L[i][x][4]]):
                                plane.append(self.P[j][1])
                                allowed_actions.append(self.L[i][x]+[j])

        return allowed_actions

    ### Check_Fly ###
    def check_fly(self, initial, actual, duration, end, rotation):
        "Checks if a flight is possible in terms of oppening and closing airports times"
        
        time = self.timer(actual, duration, rotation)
        time2 = self.timer(actual, duration)
        
        ini_hour = int(initial[0:2])
        ini_min = int(initial[2:4])
        actual_hour = int(time[0:2])
        actual_min = int(time[2:4])
        end_hour = int(end[0:2])
        end_min = int(end[2:4])
        early_hour = int(time2[0:2])
        early_min = int(time2[2:4])

        if end_hour > actual_hour and early_hour > ini_hour:
            return True
        elif end_hour == actual_hour and end_min > actual_min:
            return True
        elif ini_hour == early_hour and early_min > ini_min:
            return True
            
        return False

    ### Result ###
    def result(self, state, action):
        "returns the state resulting from applying action a to state s"

        i = action[-1]
        state = list(state)
        state[i] = list(state[i])

        # Airport departure
        state[i][0] = list(state[i][0])
        state[i][0].append(action[1])
        state[i][0] = tuple(state[i][0])
        # Airport arrival
        state[i][1] = list(state[i][1])
        state[i][1].append(action[2])
        state[i][1] = tuple(state[i][1])
        # Time
        if state[i][2] == tuple():
            state[i][2] = list(state[i][2])
            state[i][2].append(self.A[action[1]][0])
            state[i][2].append(self.timer(state[i][2][-1], action[3], self.C[action[4]]))
            state[i][2] = tuple(state[i][2])
        else:
            state[i][2] = list(state[i][2])
            state[i][2].append(self.timer(state[i][2][-1], action[3], self.C[action[4]]))
            state[i][2] = tuple(state[i][2])
        # Leg index
        state[i][3] = list(state[i][3])
        state[i][3].append(action[0])
        state[i][3] = tuple(state[i][3])
        # Profit
        state[-1] = state[-1] + float(action[5])

        state[i] = tuple(state[i])
        state = tuple(state)
        return state

    ### Goal_Test ###
    def goal_test(self, state):
        "returns True if state s is a goal state, and False otherwise"

        done = []
        backToInit = 0
        state = list(state)
        
        for i in range(len(state)-1):
            state[i] = list(state[i])
            done += state[i][3]     # list of all legs already done
            state[i][0] = list(state[i][0])
            state[i][1] = list(state[i][1])
            if state[i][0] == []:
                continue
            elif state[i][0][0] == state[i][1][-1]:
                backToInit = 1      # verifies if all planes finish in their initial airport
            else:
                backToInit = 0

        if len(done) == len(self.L) and backToInit:
            return True
        else:
            return False

    ### Path_Cost ###
    def path_cost(self, c, state1, action, state2):
        "returns the path cost of state s2, reached from state s1 by applying action a, knowing that the path cost of s1 is c"

        cost = 1/float(action[5])
        return c+cost

    ### Heuristic ###
    def heuristic(self, node):
        "returns the heuristic of node n"

        heur = 0
        done = []
        state = list(node.state)
        for i in range(len(state)-1):
            state[i] = list(state[i])
            done += state[i][3]     # list of all legs already done
        
        all_legs = range(len(self.L))
        legs_left = list(set(all_legs).difference(set(done)))
        
        for i in legs_left:
            max = 0
            for k in range(len(self.L[i])):
                if int(self.L[i][k][5]) > max:
                    max = int(self.L[i][k][5])
            heur += 1/max
        
        return heur

    ### Load ###
    def load(self, fh):
        "loads a problem from a (opened) file object f"

        i = 0
        aux3 = []
        for ln in fh.readlines():
            if ln[0] == 'A':
                aux = ln[1:].split()
                self.A[aux[0]] = aux[1:]
            elif ln[0] == 'P':
                aux = ln[1:].split()
                self.P.append(aux)
            elif ln[0] == 'L':
                aux3 = []
                aux = ln.split()
                aux1 = [i]+aux[1:6]
                aux2 = [i]+aux[1:4]+aux[6:]
                aux3.append(aux1)
                aux3.append(aux2)
                self.L.append(aux3)
                i = i+1
            elif ln[0] == 'C':
                aux = ln[1:].split()
                self.C[aux[0]] = aux[1]

        self.initialization()   # initializes the initial state of the problem
        return None

    ### Save ###
    def save(self, fh, goal):
        "saves a solution state s to a (opened) file object f"

        if goal == None:
            fh.write("Infeasible")
        else:
            state = goal
            plane = 0
            for i in state:
                if i == state[-1]:
                    profit = "P %.1f" % (i)
                    fh.write(profit)
                elif i[0] != tuple():
                    str = "S"+" "+self.P[plane][0]
                    for j in range(len(i[0])):
                        str += " " + i[2][j] + " " + i[0][j] + " " + i[1][j]
                    fh.write(str+"\n")
                    plane += 1
                else:
                    plane += 1

        return None

    ### Timer ###
    def timer(self, current_time, leg_time, rot_time='0000'):
        "Updates current time accordingly with action taken"

        new_hour = int(current_time[0:2])+int(leg_time[0:2])+int(rot_time[0:2])
        new_minute = int(current_time[2:4])+int(leg_time[2:4])+int(rot_time[2:4])
        new_hour += new_minute//60
        new_minute = new_minute % 60
        
        if new_hour < 10:
            new_hour = str(0) + str(new_hour)
        if new_minute < 10:
            new_minute = str(0)+str(new_minute)

        current_time = str(new_hour) + str(new_minute)

        return current_time
