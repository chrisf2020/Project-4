import os, tempfile, unittest
from parser import Problem, parse_input, build_neighbors

EXAMPLE = """PHYSICAL_REGISTERS R0 R1 R2 R3

VIRTUAL_REGISTERS
v0 R0 R1 R2 R3
v1 R0
v2 R0 R1 R2 R3
v3 R1 R2 R3

INTERFERENCES
v0 v1
v0 v2
v1 v2
v2 v3
"""


#######################################################################
# function: write_temp
# purpose: writes text to a temp file so parse_input can read it
# params: text - contents of the file
# returns: path of the temp file
#######################################################################
def write_temp(text): 
    handle, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(handle, "w") as f:
        f.write(text)
    return path


class TestParser(unittest.TestCase):

    #######################################################################
    # function: tearDown
    # purpose: removes any temp files created during a test
    #######################################################################
    def tearDown(self): 
        for path in getattr(self, "paths", []):
            os.remove(path)

    #######################################################################
    # function: parse
    # purpose: writes text to a temp file, tracks it for cleanup, and parses it
    # params: text - contents of the input file
    # returns: the parsed Problem
    #######################################################################
    def parse(self, text): 
        path = write_temp(text)
        self.paths = getattr(self, "paths", []) + [path]
        return parse_input(path)

    #######################################################################
    # function: test_spec_example
    # purpose: checks the example from the project spec against a hand-made Problem
    #######################################################################
    def test_spec_example(self): 
        expected = Problem(
            ["R0", "R1", "R2", "R3"],
            {"v0": ["R0", "R1", "R2", "R3"], "v1": ["R0"], "v2": ["R0", "R1", "R2", "R3"], "v3": ["R1", "R2", "R3"]},
            {"v0": {"v1", "v2"}, "v1": {"v0", "v2"}, "v2": {"v0", "v1", "v3"}, "v3": {"v2"}},
        )
        actual = self.parse(EXAMPLE)
        self.assertEqual(actual.physical, expected.physical)
        self.assertEqual(actual.domains, expected.domains)
        self.assertEqual(actual.neighbors, expected.neighbors)

    #######################################################################
    # function: test_domains_sorted_and_deduped
    # purpose: checks domains come back in ascending order with duplicates removed
    #######################################################################
    def test_domains_sorted_and_deduped(self): 
        problem = self.parse("PHYSICAL_REGISTERS R2 R0 R1\nVIRTUAL_REGISTERS\nv0 R2 R0 R2 R1\nINTERFERENCES\n")
        self.assertEqual(problem.physical, ["R0", "R1", "R2"])
        self.assertEqual(problem.domains["v0"], ["R0", "R1", "R2"])

    #######################################################################
    # function: test_neighbors_symmetric
    # purpose: checks an edge listed once shows up in both directions
    #######################################################################
    def test_neighbors_symmetric(self): 
        problem = self.parse("PHYSICAL_REGISTERS R0 R1\nVIRTUAL_REGISTERS\nv0 R0 R1\nv1 R0 R1\nINTERFERENCES\nv0 v1\n")
        self.assertIn("v1", problem.neighbors["v0"])
        self.assertIn("v0", problem.neighbors["v1"])

    #######################################################################
    # function: test_duplicate_edges
    # purpose: checks repeated and reversed edges do not create extra neighbors
    #######################################################################
    def test_duplicate_edges(self): 
        problem = self.parse("PHYSICAL_REGISTERS R0 R1\nVIRTUAL_REGISTERS\nv0 R0\nv1 R1\nINTERFERENCES\nv0 v1\nv1 v0\nv0 v1\n")
        self.assertEqual(problem.neighbors["v0"], {"v1"})
        self.assertEqual(problem.neighbors["v1"], {"v0"})

    #######################################################################
    # function: test_no_interferences
    # purpose: checks variables with no edges get empty neighbor sets
    #######################################################################
    def test_no_interferences(self): 
        problem = self.parse("PHYSICAL_REGISTERS R0\nVIRTUAL_REGISTERS\nv0 R0\nv1 R0\nINTERFERENCES\n")
        self.assertEqual(problem.neighbors, {"v0": set(), "v1": set()})

    #######################################################################
    # function: test_blank_lines_and_whitespace
    # purpose: checks extra blank lines and padding do not change the result
    #######################################################################
    def test_blank_lines_and_whitespace(self): 
        messy = "\n\n  PHYSICAL_REGISTERS   R0  R1 \n\n\nVIRTUAL_REGISTERS  \n  v0   R0 R1\n\nINTERFERENCES\n\n"
        problem = self.parse(messy)
        self.assertEqual(problem.physical, ["R0", "R1"])
        self.assertEqual(problem.domains, {"v0": ["R0", "R1"]})

    #######################################################################
    # function: test_empty_domain
    # purpose: checks a variable with no allowed registers still parses
    #######################################################################
    def test_empty_domain(self): 
        problem = self.parse("PHYSICAL_REGISTERS R0\nVIRTUAL_REGISTERS\nv0\nINTERFERENCES\n")
        self.assertEqual(problem.domains["v0"], [])

    #######################################################################
    # function: test_self_interference_kept
    # purpose: checks a self edge is stored so the solver can see it is unsat
    #######################################################################
    def test_self_interference_kept(self): 
        problem = self.parse("PHYSICAL_REGISTERS R0\nVIRTUAL_REGISTERS\nv0 R0\nINTERFERENCES\nv0 v0\n")
        self.assertIn("v0", problem.neighbors["v0"])

    #######################################################################
    # function: test_undeclared_variable
    # purpose: checks an edge naming an undeclared variable raises ValueError
    #######################################################################
    def test_undeclared_variable(self): 
        with self.assertRaises(ValueError):
            self.parse("PHYSICAL_REGISTERS R0\nVIRTUAL_REGISTERS\nv0 R0\nINTERFERENCES\nv0 v9\n")

    #######################################################################
    # function: test_malformed_interference
    # purpose: checks an interference line without exactly two ids raises ValueError
    #######################################################################
    def test_malformed_interference(self): 
        with self.assertRaises(ValueError):
            self.parse("PHYSICAL_REGISTERS R0\nVIRTUAL_REGISTERS\nv0 R0\nv1 R0\nINTERFERENCES\nv0 v1 v0\n")

    #######################################################################
    # function: test_content_before_section
    # purpose: checks stray content before any section header raises ValueError
    #######################################################################
    def test_content_before_section(self): 
        with self.assertRaises(ValueError):
            self.parse("v0 R0\nPHYSICAL_REGISTERS R0\n")

    #######################################################################
    # function: test_build_neighbors_direct
    # purpose: checks build_neighbors on hand-made domains and edges
    #######################################################################
    def test_build_neighbors_direct(self): 
        domains = {"a": ["R0"], "b": ["R0"], "c": ["R0"]}
        result = build_neighbors(domains, [("a", "b"), ("b", "c")])
        self.assertEqual(result, {"a": {"b"}, "b": {"a", "c"}, "c": {"b"}})


if __name__ == "__main__":
    unittest.main()