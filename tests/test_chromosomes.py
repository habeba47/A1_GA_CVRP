from ga_toolbox.chromosomes import BinaryChromosome, IntegerChromosome, FloatChromosome
from ga_toolbox.settings import GAConfig

b = BinaryChromosome.random(8)
i = IntegerChromosome.random(5, low=1, permutation=True)
f = FloatChromosome.random(4, low=-5, high=5)
print(b.genes, i.genes, f.genes)
assert b.is_valid() and i.is_valid() and f.is_valid()

c = i.copy()
c.genes[0] = 99
assert i.genes[0] != 99
assert not c.is_valid()

GAConfig()
try:
    GAConfig(mutation_rate=1.5)
except ValueError as e:
    print("OK:", e)
print("chromosome tests passed")

for bad_args in (
    {"population_size": 10, "generations": -1},
    {"population_size": 10, "tournament_size": 0},
    {"population_size": 10, "infeasible_penalty": -1},
):
    try:
        GAConfig(**bad_args)
        raise AssertionError(f"Expected invalid configuration to fail: {bad_args}")
    except ValueError:
        pass

for create in (
    lambda: BinaryChromosome.random(-1),
    lambda: IntegerChromosome.random(3, low=5, high=2),
    lambda: FloatChromosome.random(3, low=2.0, high=1.0),
):
    try:
        create()
        raise AssertionError("Expected invalid chromosome arguments to fail")
    except ValueError:
        pass

assert not BinaryChromosome([0, True, 1]).is_valid()
assert not IntegerChromosome([1, 1, 2], low=1, high=3, permutation=True).is_valid()
assert not FloatChromosome([float("nan")], low=0.0, high=1.0).is_valid()
print("edge-case tests passed")

assert IntegerChromosome([6, 5, 7], low=5, permutation=True).is_valid()
print("permutation construction test passed")
