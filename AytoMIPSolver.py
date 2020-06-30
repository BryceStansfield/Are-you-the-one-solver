# This file formulates and solves the problem as a MIP
from ortools.sat.python import cp_model
import ortools
import logging
import json

logging.basicConfig(filename='whyisntthisworking.log', level=logging.DEBUG)

class AytoMIPSolver:
    """ Solves the Ayto problem as a MIP"""
    def __init__(self, participants, potential_matches=None):
        """Args:
            participants (list of strings): The names of the particpants this season.
            param2 (list of 2-tuples of indicies from participants or None, optional): Which participants can match this season?
                                                                            None for a complete graph"""

        ### DATA
        self.particpants = participants
        
        # Have we been supplied a list of potential matches already?
        if(potential_matches == None):
            potential_matches = []
            for x in range(0, len(participants)):
                for y in range(x+1, len(participants)):
                    potential_matches.append((x,y,))

        ### Setting up the solver
        self.model =  cp_model.CpModel()

        # Variables
        self.M = {(x,y): self.model.NewIntVar(0, 1, "{} <3 {}".format(participants[x],participants[y],)) for (x,y,) in potential_matches}    # Matches

        # Constraints
        self.oneMatch = {x: self.model.Add(sum([self.M[min(x,y),max(x,y)] for y in range(0, len(participants)) if x!=y]) == 1) for x in range(0, len(participants))}
        
        ### Recorder
        self.recorder = SolutionRecorder(participants, self.M)
        return

    def lights(self, matches, num_lights):
        """ Adds the relevant constraint to the model after a light ceremony,
            Args:
                matches (list of 2-tuples of indicies from participants): Which matches were together at the ceremony?
                num_lights (int): How many lights were on?"""
        self.model.Add(sum(self.M[min(m), max(m)] for m in matches) == num_lights)
        return

    def truth_room(self, couple, verdict):
        self.model.Add(self.M[min(couple), max(couple)] == verdict)
        return
    
    def solve(self):
        self.recorder.reset()
        solver = cp_model.CpSolver()
        solver.SearchForAllSolutions(self.model, self.recorder)
        return self.recorder.Solutions()


# Read https://developers.google.com/optimization/cp/queens
class SolutionRecorder(cp_model.CpSolverSolutionCallback):
    """Records intermediate solutions."""

    def __init__(self, participants, MVars):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__participants = participants
        self.__MVars = MVars
        self.__solution_count = 0
        self.__in_sol_count = {(participants[x],participants[y],):0 for x in range(0, len(participants)) for y in range(x+1, len(participants))}
        self.__solutions = []
    

    def OnSolutionCallback(self):
        self.__solution_count += 1
        matches_in_sol = []
        for m_key in self.__MVars.keys():
            logging.getLogger(__name__).debug(m_key)
            if int(self.Value(self.__MVars[m_key])) == 1:
                matches_in_sol.append((self.__participants[m_key[0]],self.__participants[m_key[1]],))
                self.__in_sol_count[self.__participants[m_key[0]],self.__participants[m_key[1]]] += 1
        self.__solutions.append(matches_in_sol)
        return

    def reset(self):
        self.__solution_count = 9
        self.__in_sol_count = {(self.__participants[x],self.__participants[y],):0 for x in range(0, len(self.__participants)) for y in range(x+1, len(self.__participants))}
        self.__solutions = []
    
    def Solutions(self):
        return self.__solution_count, self.__in_sol_count, self.__solutions
    

