# *******************************************************************************
# Author: Christopher Frias
# Major: Computer Science
# Creation Date: November 2, 2026
# Due Date: November 8, 2026
# Course: CPSC 447
# Professor Name: Dr. Schwesinger
# Assignment: #4
# Filename: main.py
# Purpose: agent made for benchmarking a game for adversarial search algorithms.
#
# Used https://en.wikipedia.org/wiki/AC-3_algorithm wikipedia link to help implement AC-3 algorithm.
# Used https://en.wikipedia.org/wiki/Backtracking algorithm wikipedia link to help implement Backtracking algorithm.
#
# AI USAGE: Used AI Gemini 3.8 for Function Documentation.
#
# *****************************************************************************



from collections import deque
 
 
#######################################################################
# function: arc_reduce
# purpose: removes values of x that have no support in y
# params: domains - dict of variable id to list of values (modified in place), x - variable to prune, y - neighbor variable
# returns: True if any value was removed from the domain of x
#######################################################################
def arc_reduce(domains, x, y):
    changed = False
 
    for vx in list(domains[x]):
        #inequality constraint so vy supports vx when they differ
        supported = False
        for vy in domains[y]:
            if vx != vy:
                supported = True
                break
 
        if not supported:
            domains[x].remove(vx)
            changed = True
 
    return changed
 
 
#######################################################################
# function: ac3
# purpose: enforces arc consistency on the domains using the ac-3 algorithm
# params: problem - the parsed Problem, domains - dict of variable id to list of values (modified in place), arcs - optional list of (x, y) arcs to start with, defaults to every arc
# returns: tuple (consistent, revisions) where consistent is False if a domain became empty
#######################################################################
def ac3(problem, domains, arcs=None):
    #unary constraints are already applied by the parser since domains are per variable
    if arcs is None:
        arcs = [(x, y) for x in sorted(problem.neighbors) for y in sorted(problem.neighbors[x])]
 
    worklist = deque(arcs)
    queued = set(arcs)
    revisions = 0
 
    while worklist:
        x, y = worklist.popleft()
        queued.discard((x, y))
 
        revisions += 1
        if arc_reduce(domains, x, y):
            #empty domain means no valid assignment
            if not domains[x]:
                return False, revisions
 
            #x shrank so every other arc pointing at x needs rechecking
            for z in sorted(problem.neighbors[x]):
                if z != y and (z, x) not in queued:
                    worklist.append((z, x))
                    queued.add((z, x))
 
    return True, revisions

#######################################################################
# function: backtrack
# purpose: recursive backtracking search, assigns variables in the given order and stops at the first full assignment
# params: problem - the parsed Problem, order - list of variable ids in assignment order, index - position in order of the variable to assign, assignment - dict of assigned variable id to register (modified in place), stats - dict with nodes_visited and backtracks counters
# returns: True if the assignment was completed, False if this branch is a dead end
#######################################################################
def backtrack(problem, order, index, assignment, stats):
    #accept when every variable has a register
    if index == len(order):
        return True
 
    var = order[index]
    for value in problem.domains[var]:
        stats["nodes_visited"] += 1
 
        if consistent(problem, assignment, var, value):
            assignment[var] = value
            if backtrack(problem, order, index + 1, assignment, stats):
                return True
 
            #subtree failed so undo and try the next value
            del assignment[var]
            stats["backtracks"] += 1
 
    return False
 
 
#######################################################################
# function: backtrack_naive
# purpose: runs plain backtracking with lexicographic variable order and ascending value order
# params: problem - the parsed Problem
# returns: tuple (assignment, stats) where assignment is a dict or None if unsatisfiable
#######################################################################
def backtrack_naive(problem):
    order = sorted(problem.domains)
    assignment = {}
    stats = {"nodes_visited": 0, "backtracks": 0}
 
    if backtrack(problem, order, 0, assignment, stats):
        return assignment, stats
 
    return None, stats