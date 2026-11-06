import unittest
 
from parser import Problem
from main import arc_reduce, ac3
 
 
class TestArcReduce(unittest.TestCase):
 
    #######################################################################
    # function: test_arc_reduce_removes_unsupported
    # purpose: checks a value with no different value in y is removed from x
    #######################################################################
    def test_arc_reduce_removes_unsupported(self):
        domains = {"x": ["R0", "R1"], "y": ["R0"]}
        changed = arc_reduce(domains, "x", "y")
        self.assertTrue(changed)
        self.assertEqual(domains["x"], ["R1"])
        self.assertEqual(domains["y"], ["R0"])
 
    #######################################################################
    # function: test_arc_reduce_no_change
    # purpose: checks nothing is removed when every value in x has support in y
    #######################################################################
    def test_arc_reduce_no_change(self):
        domains = {"x": ["R0", "R1"], "y": ["R0", "R1"]}
        changed = arc_reduce(domains, "x", "y")
        self.assertFalse(changed)
        self.assertEqual(domains["x"], ["R0", "R1"])
 
 
class TestAc3(unittest.TestCase):
 
    #######################################################################
    # function: test_ac3_spec_example
    # purpose: checks the spec example is made arc consistent with the expected domains and revision count
    #######################################################################
    def test_ac3_spec_example(self):
        problem = Problem(
            ["R0", "R1", "R2", "R3"],
            {"v0": ["R0", "R1", "R2", "R3"], "v1": ["R0"], "v2": ["R0", "R1", "R2", "R3"], "v3": ["R1", "R2", "R3"]},
            {"v0": {"v1", "v2"}, "v1": {"v0", "v2"}, "v2": {"v0", "v1", "v3"}, "v3": {"v2"}},
        )
        domains = {v: list(d) for v, d in problem.domains.items()}
        consistent, revisions = ac3(problem, domains)
        self.assertTrue(consistent)
        self.assertEqual(revisions, 9)
        self.assertEqual(domains, {"v0": ["R1", "R2", "R3"], "v1": ["R0"], "v2": ["R1", "R2", "R3"], "v3": ["R1", "R2", "R3"]})
 
    #######################################################################
    # function: test_ac3_detects_failure
    # purpose: checks two neighbors forced to the same register make ac3 report failure
    #######################################################################
    def test_ac3_detects_failure(self):
        problem = Problem(["R0"], {"a": ["R0"], "b": ["R0"]}, {"a": {"b"}, "b": {"a"}})
        domains = {v: list(d) for v, d in problem.domains.items()}
        consistent, revisions = ac3(problem, domains)
        self.assertFalse(consistent)
        self.assertEqual(domains["a"], [])

class TestBacktrack(unittest.TestCase):
 
    #######################################################################
    # function: test_backtrack_finds_assignment
    # purpose: checks backtrack fills the assignment and counts a rejected try as a node
    #######################################################################
    def test_backtrack_finds_assignment(self):
        problem = Problem(["R0", "R1"], {"a": ["R0", "R1"], "b": ["R0", "R1"]}, {"a": {"b"}, "b": {"a"}})
        assignment = {}
        stats = {"nodes_visited": 0, "backtracks": 0}
        result = backtrack(problem, ["a", "b"], 0, assignment, stats)
        self.assertTrue(result)
        self.assertEqual(assignment, {"a": "R0", "b": "R1"})
        self.assertEqual(stats, {"nodes_visited": 3, "backtracks": 0})
 
    #######################################################################
    # function: test_backtrack_dead_end
    # purpose: checks backtrack returns False on an unsatisfiable triangle and leaves the assignment empty
    #######################################################################
    def test_backtrack_dead_end(self):
        problem = Problem(
            ["R0", "R1"],
            {"a": ["R0", "R1"], "b": ["R0", "R1"], "c": ["R0", "R1"]},
            {"a": {"b", "c"}, "b": {"a", "c"}, "c": {"a", "b"}},
        )
        assignment = {}
        stats = {"nodes_visited": 0, "backtracks": 0}
        result = backtrack(problem, ["a", "b", "c"], 0, assignment, stats)
        self.assertFalse(result)
        self.assertEqual(assignment, {})
        self.assertEqual(stats, {"nodes_visited": 10, "backtracks": 4})
 
 
class TestBacktrackNaive(unittest.TestCase):
 
    #######################################################################
    # function: test_backtrack_naive_spec_example
    # purpose: checks backtrack_naive solves the spec example with the expected assignment and stats
    #######################################################################
    def test_backtrack_naive_spec_example(self):
        problem = Problem(
            ["R0", "R1", "R2", "R3"],
            {"v0": ["R0", "R1", "R2", "R3"], "v1": ["R0"], "v2": ["R0", "R1", "R2", "R3"], "v3": ["R1", "R2", "R3"]},
            {"v0": {"v1", "v2"}, "v1": {"v0", "v2"}, "v2": {"v0", "v1", "v3"}, "v3": {"v2"}},
        )
        assignment, stats = backtrack_naive(problem)
        self.assertEqual(assignment, {"v0": "R1", "v1": "R0", "v2": "R2", "v3": "R1"})
        self.assertEqual(stats, {"nodes_visited": 8, "backtracks": 1})
 
 
 
if __name__ == "__main__":
    unittest.main()