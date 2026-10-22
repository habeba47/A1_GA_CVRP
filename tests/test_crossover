import random

from ga_toolbox.chromosomes import BinaryChromosome, FloatChromosome, IntegerChromosome
from ga_toolbox.crossover import MultiPointCrossover, OrderCrossover

random.seed(1)

# Multi-point on binary and float chromosomes: inputs untouched, genes only come from parents.
for cls, kwargs in ((BinaryChromosome, {}), (FloatChromosome, {"low": -5, "high": 5})):
    for points in (1, 2, 3, 50):
        for _ in range(100):
            p1, p2 = cls.random(12, **kwargs), cls.random(12, **kwargs)
            g1, g2 = p1.genes.copy(), p2.genes.copy()
            c1, c2 = MultiPointCrossover(points).crossover(p1, p2)
            assert p1.genes == g1 and p2.genes == g2
            assert c1 is not p1 and c2 is not p2
            assert len(c1) == len(c2) == 12
            assert c1.is_valid() and c2.is_valid()
            for i in range(12):
                assert {c1.genes[i], c2.genes[i]} == {g1[i], g2[i]}
print("multi-point (binary/float) tests passed")

# Multi-point on permutations: children must stay valid permutations.
for points in (1, 2, 4):
    for _ in range(200):
        p1 = IntegerChromosome.random(16, low=1, permutation=True)
        p2 = IntegerChromosome.random(16, low=1, permutation=True)
        g1, g2 = p1.genes.copy(), p2.genes.copy()
        c1, c2 = MultiPointCrossover(points).crossover(p1, p2)
        assert p1.genes == g1 and p2.genes == g2
        assert c1.is_valid() and c2.is_valid()
        assert c1.permutation and c1.low == 1
print("multi-point (permutation) tests passed")

# Order crossover: valid permutations, inputs untouched, slice inherited from the donor parent.
for _ in range(300):
    p1 = IntegerChromosome.random(16, low=1, permutation=True)
    p2 = IntegerChromosome.random(16, low=1, permutation=True)
    g1, g2 = p1.genes.copy(), p2.genes.copy()
    c1, c2 = OrderCrossover().crossover(p1, p2)
    assert p1.genes == g1 and p2.genes == g2
    assert c1.is_valid() and c2.is_valid()
    shared1 = [i for i in range(16) if c1.genes[i] == g1[i]]
    shared2 = [i for i in range(16) if c2.genes[i] == g2[i]]
    assert shared1 and shared2  # each child keeps a slice of its donor

# Hand-checked example (slice positions 3..5).
assert OrderCrossover._build_child(
    [1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 3, 7, 8, 2, 6, 5, 1, 4], 3, 5
) == [7, 8, 2, 4, 5, 6, 1, 9, 3]
print("order crossover tests passed")

# Edge cases.
tiny = IntegerChromosome.random(1, low=1, permutation=True)
for op in (MultiPointCrossover(2), OrderCrossover()):
    a, b = op.crossover(tiny, tiny)
    assert a.genes == tiny.genes and a is not tiny
for bad in (lambda: MultiPointCrossover(0), lambda: MultiPointCrossover("2")):
    try:
        bad()
        raise AssertionError("Expected invalid num_points to fail")
    except ValueError:
        pass
print("crossover edge-case tests passed")