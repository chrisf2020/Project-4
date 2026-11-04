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
#
# AI USAGE: Used AI Gemini 3.8 for Function Documentation.
#
# AI: Used for helping raise error messages and for helping with the test cases.
# *****************************************************************************



#######################################################################
# class: Problem
# purpose: holds a parsed register allocation csp
# fields:
#   physical - sorted list of physical register names (R0, R1, ...)
#   domains - dict mapping virtual register id to sorted list of allowed physical registers
#   neighbors - dict mapping virtual register id to set of interfering virtual register ids
#######################################################################
class Problem:
    def __init__(self, physical, domains, neighbors):
        self.physical = physical
        self.domains = domains
        self.neighbors = neighbors


#######################################################################
# function: parse_input
# purpose: reads the input file and builds a Problem from it
# params: path - path to the plain-text interference graph file
# returns: a Problem object
# raises: ValueError if the file is malformed
#######################################################################
def parse_input(path): 
    with open(path, "r") as f:
        lines = f.read().splitlines()

    physical = []
    domains = {}
    neighbors = {}
    edges = []
    section = None

    for number, raw in enumerate(lines, 1):
        line = raw.strip()

        #skip blank lines
        if not line:
            continue

        tokens = line.split()

        #section headers
        if tokens[0] == "PHYSICAL_REGISTERS":
            physical = sorted(set(tokens[1:]))
            section = "physical"
            continue
        if tokens[0] == "VIRTUAL_REGISTERS" and len(tokens) == 1:
            section = "virtual"
            continue
        if tokens[0] == "INTERFERENCES" and len(tokens) == 1:
            section = "interferences"
            continue

        #section bodies
        if section == "virtual":
            domains[tokens[0]] = sorted(set(tokens[1:]))
        elif section == "interferences":
            if len(tokens) != 2:
                raise ValueError("line " + str(number) + ": expected two virtual registers, got '" + line + "'")
            edges.append((tokens[0], tokens[1]))
        else:
            raise ValueError("line " + str(number) + ": unexpected content '" + line + "'")

    neighbors = build_neighbors(domains, edges)
    return Problem(physical, domains, neighbors)


#######################################################################
# function: build_neighbors
# purpose: turns the undirected edge list into an adjacency dict
# params: domains - dict of virtual register id to domain, edges - list of (u, v) tuples
# returns: dict mapping each virtual register id to a set of neighbor ids
# raises: ValueError if an edge names an undeclared virtual register
#######################################################################
def build_neighbors(domains, edges):
    neighbors = {v: set() for v in domains}

    for u, v in edges:
        if u not in domains or v not in domains:
            raise ValueError("interference '" + u + " " + v + "' uses an undeclared virtual register")

        #undirected so add both directions
        neighbors[u].add(v)
        neighbors[v].add(u)

    return neighbors