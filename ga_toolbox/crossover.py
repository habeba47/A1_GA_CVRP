import random

from ga_toolbox.base_classes import Crossover


def _new_child(parent, genes):
    child = parent.copy()
    child.genes = genes
    child.fitness = None
    child.feasible = True
    return child


def _check_parents(parent1, parent2):
    if len(parent1) != len(parent2):
        raise ValueError("parents must have the same length")


def _repair_permutation(genes, reference):
    seen = set()
    repeated_positions = []
    for index, gene in enumerate(genes):
        if gene in seen:
            repeated_positions.append(index)
        else:
            seen.add(gene)
    missing = [gene for gene in reference if gene not in seen]
    for index, gene in zip(repeated_positions, missing):
        genes[index] = gene
    return genes


class MultiPointCrossover(Crossover):

    def __init__(self, num_points=2):
        if type(num_points) is not int or num_points < 1:
            raise ValueError("num_points must be an integer of at least 1")
        self.num_points = num_points

    def crossover(self, parent1, parent2):
        _check_parents(parent1, parent2)
        length = len(parent1)
        if length < 2:
            return parent1.copy(), parent2.copy()

        num_points = min(self.num_points, length - 1)
        cut_points = sorted(random.sample(range(1, length), num_points))

        genes1, genes2 = [], []
        start = 0
        swap = False
        for end in cut_points + [length]:
            source1, source2 = (parent2, parent1) if swap else (parent1, parent2)
            genes1.extend(source1.genes[start:end])
            genes2.extend(source2.genes[start:end])
            start = end
            swap = not swap

        if getattr(parent1, "permutation", False):
            genes1 = _repair_permutation(genes1, parent2.genes)
            genes2 = _repair_permutation(genes2, parent1.genes)

        return _new_child(parent1, genes1), _new_child(parent2, genes2)


class OrderCrossover(Crossover):

    def crossover(self, parent1, parent2):
        _check_parents(parent1, parent2)
        length = len(parent1)
        if length < 2:
            return parent1.copy(), parent2.copy()
        if sorted(parent1.genes) != sorted(parent2.genes):
            raise ValueError("order crossover needs parents that are permutations of the same genes")

        first, last = sorted(random.sample(range(length), 2))
        genes1 = self._build_child(parent1.genes, parent2.genes, first, last)
        genes2 = self._build_child(parent2.genes, parent1.genes, first, last)
        return _new_child(parent1, genes1), _new_child(parent2, genes2)

    @staticmethod
    def _build_child(donor, other, first, last):
        length = len(donor)
        child = [None] * length
        child[first:last + 1] = donor[first:last + 1]
        kept = set(child[first:last + 1])

        fill_order = [gene for gene in other[last + 1:] + other[:last + 1] if gene not in kept]
        positions = list(range(last + 1, length)) + list(range(0, first))
        for position, gene in zip(positions, fill_order):
            child[position] = gene
        return child