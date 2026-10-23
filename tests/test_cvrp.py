import pytest
from cvrp.problem import CVRPProblem
from cvrp.fitness import CVRPFitness
from cvrp.output import format_solution

MATRIX = [
[0,548,776,696,582,274,502,194,308,194,536,502,388,354,468,776,662],
[548,0,684,308,194,502,730,354,696,742,1084,594,480,674,1016,868,1210],
[776,684,0,992,878,502,274,810,468,742,400,1278,1164,1130,788,1552,754],
[696,308,992,0,114,650,878,502,844,890,1232,514,628,822,1164,560,1358],
[582,194,878,114,0,536,764,388,730,776,1118,400,514,708,1050,674,1244],
[274,502,502,650,536,0,228,308,194,240,582,776,662,628,514,1050,708],
[502,730,274,878,764,228,0,536,194,468,354,1004,890,856,514,1278,480],
[194,354,810,502,388,308,536,0,342,388,730,468,354,320,662,742,856],
[308,696,468,844,730,194,194,342,0,274,388,810,696,662,320,1084,514],
[194,742,742,890,776,240,468,388,274,0,342,536,422,388,274,810,468],
[536,1084,400,1232,1118,582,354,730,388,342,0,878,764,730,388,1152,354],
[502,594,1278,514,400,776,1004,468,810,536,878,0,114,308,650,274,844],
[388,480,1164,628,514,662,890,354,696,422,764,114,0,194,536,388,730],
[354,674,1130,822,708,628,856,320,662,388,730,308,194,0,342,422,536],
[468,1016,788,1164,1050,514,514,662,320,274,388,650,536,342,0,764,194],
[776,868,1552,560,674,1050,1278,742,1084,810,1152,274,388,422,764,0,798],
[662,1210,754,1358,1244,708,480,856,514,468,354,844,730,536,194,798,0],
]
DEMANDS = [0,1,1,2,4,2,4,8,8,1,2,1,2,4,4,8,8]
BEST_GENES = [12, 11, 15, 13, 14, 16, 10, 9, 8, 6, 2, 5, 1, 4, 3, 7]


def make_problem():
    return CVRPProblem(MATRIX, DEMANDS, [15, 15, 15, 15], depot=0)


# ---------- Problem data ----------

def test_google_instance_dimensions():
    p = make_problem()
    assert len(p.customers) == 16
    assert p.num_vehicles == 4
    assert sum(p.demands) == 60


# ---------- Decoding ----------

def test_decode_and_feasible_permutation():
    p = make_problem()
    genes = list(range(1, 17))
    routes = p.decode(genes)
    # every route starts and ends at the depot
    assert all(route[0] == 0 and route[-1] == 0 for route in routes)
    # every customer appears exactly once
    assert sorted(node for route in routes for node in route[1:-1]) == genes
    # is_feasible agrees with our own manual check
    manual_check = len(routes) <= 4 and all(p.get_route_load(r) <= 15 for r in routes)
    assert p.is_feasible(genes) == manual_check


def test_decode_has_no_empty_routes():
    p = make_problem()
    routes = p.decode(list(range(1, 17)))
    assert all(len(route) > 2 for route in routes)


def test_decode_best_solution_gives_four_full_routes():
    p = make_problem()
    routes = p.decode(BEST_GENES)
    assert len(routes) == 4
    assert [p.get_route_load(r) for r in routes] == [15, 15, 15, 15]


# ---------- Constraints ----------

def test_duplicate_missing_unknown_rejected():
    p = make_problem()
    assert not p.is_feasible([1, 1] + list(range(3, 17)))   # duplicate
    assert not p.is_feasible(list(range(1, 16)))            # missing
    assert not p.is_feasible(list(range(1, 16)) + [99])     # unknown


def test_capacity_excess_detected_directly():
    p = make_problem()
    overloaded_route = [[0, 7, 8, 15, 0]]   # load = 8 + 8 + 8 = 24, capacity 15
    violations = p.violations_from_routes(overloaded_route)
    assert violations["capacity_excess"] == 9
    assert violations["extra_vehicles"] == 0


def test_extra_vehicles_detected_directly():
    p = make_problem()
    five_routes = [[0, i, 0] for i in range(1, 6)]   # 5 routes, only 4 vehicles
    assert p.violations_from_routes(five_routes)["extra_vehicles"] == 1


def test_best_solution_is_feasible():
    p = make_problem()
    assert p.is_feasible(BEST_GENES)


# ---------- Fitness ----------

def test_fitness_of_best_solution_is_its_distance():
    p = make_problem()
    assert CVRPFitness(p).fitness(BEST_GENES) == 6208


def test_fitness_does_not_crash_on_unknown_customer():
    p = make_problem()
    value = CVRPFitness(p).fitness(list(range(1, 16)) + [99])
    assert value >= 10000


def test_infeasible_fitness_is_worse_than_feasible():
    p = make_problem()
    evaluator = CVRPFitness(p)
    broken = [1, 1] + list(range(3, 17))
    assert evaluator.fitness(broken) > evaluator.fitness(BEST_GENES)


# ---------- Output ----------

def test_output_rejects_infeasible():
    p = make_problem()
    with pytest.raises(ValueError):
        format_solution(p, [1, 1] + list(range(3, 17)))


def test_output_format_matches_google_style():
    p = make_problem()
    text = format_solution(p, BEST_GENES)
    lines = text.split("\n")
    assert lines[0] == "Objective: 6208"
    assert "Route for vehicle 0:" in text
    assert " 12 Load(2)" in text           
    assert "Load of the route: 15" in text
    assert "Total Distance of all routes: 6208m" in text
    assert "Total Load of all routes: 60" in text