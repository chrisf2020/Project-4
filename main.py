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
# Used https://en.wikipedia.org/wiki/AC-3_algorithm wikipedia linked to help implement AC-3 algorithm.
#
# AI USAGE: Used AI Gemini 3.8 for Function Documentation.
#
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