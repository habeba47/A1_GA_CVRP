import copy
import math
import random
from abc import ABC, abstractmethod


def _check_length(length):
    if isinstance(length, bool) or not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative integer")


def _check_bounds(low, high):
    if isinstance(low, bool) or isinstance(high, bool):
        raise ValueError("bounds must be numbers")
    if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
        raise ValueError("bounds must be numbers")
    if not math.isfinite(low) or not math.isfinite(high) or low > high:
        raise ValueError("bounds must be finite and low must not exceed high")


class Chromosome(ABC):
    """Base class for every chromosome type.

    Stores the genes, the fitness (None until evaluated by the GA) and
    whether the solution is feasible. Operators must never change a
    chromosome in place: they work on copies made with copy().
    """

    def __init__(self, genes):
        self.genes = list(genes)
        self.fitness = None
        self.feasible = True

    def copy(self):
        """Return an independent copy (new gene list, same settings)."""
        new_chromosome = copy.copy(self)
        new_chromosome.genes = self.genes.copy()
        return new_chromosome

    def __len__(self):
        return len(self.genes)

    @classmethod
    @abstractmethod
    def random(cls, length, **kwargs):
        """Create a random chromosome with `length` genes."""

    @abstractmethod
    def is_valid(self):
        """True if the genes follow the rules of this representation."""


class BinaryChromosome(Chromosome):
    """Genes are 0 or 1."""

    @classmethod
    def random(cls, length, **kwargs):
        _check_length(length)
        return cls([random.randint(0, 1) for _ in range(length)])

    def is_valid(self):
        return all(type(gene) is int and gene in (0, 1) for gene in self.genes)


class IntegerChromosome(Chromosome):
    """Integer genes in [low, high].

    With permutation=True the genes are a permutation of
    low, low+1, ..., low+length-1 (each value exactly once), which is
    useful for routing problems such as CVRP.
    """

    def __init__(self, genes, low=0, high=1, permutation=False):
        genes = list(genes)
        if permutation is True:
            high = low + len(genes) - 1 if genes else low
        _check_bounds(low, high)
        if type(low) is not int or type(high) is not int:
            raise ValueError("integer bounds must be integers")
        if type(permutation) is not bool:
            raise ValueError("permutation must be a boolean")
        super().__init__(genes)
        self.low = low
        self.high = high
        self.permutation = permutation

    @classmethod
    def random(cls, length, low=0, high=1, permutation=False, **kwargs):
        _check_length(length)
        if type(permutation) is not bool:
            raise ValueError("permutation must be a boolean")
        _check_bounds(low, high)
        if type(low) is not int or type(high) is not int:
            raise ValueError("integer bounds must be integers")

        if permutation:
            genes = list(range(low, low + length))
            random.shuffle(genes)
            high = low + length - 1 if length else low
        else:
            genes = [random.randint(low, high) for _ in range(length)]
        return cls(genes, low, high, permutation)

    def is_valid(self):
        if not all(type(gene) is int for gene in self.genes):
            return False
        if self.permutation:
            return sorted(self.genes) == list(range(self.low, self.low + len(self.genes)))
        return all(self.low <= gene <= self.high for gene in self.genes)


class FloatChromosome(Chromosome):
    """Real-number genes in [low, high]."""

    def __init__(self, genes, low=0.0, high=1.0):
        _check_bounds(low, high)
        super().__init__(genes)
        self.low = float(low)
        self.high = float(high)

    @classmethod
    def random(cls, length, low=0.0, high=1.0, **kwargs):
        _check_length(length)
        _check_bounds(low, high)
        return cls([random.uniform(low, high) for _ in range(length)], low, high)

    def is_valid(self):
        return all(
            not isinstance(gene, bool)
            and isinstance(gene, (int, float))
            and math.isfinite(gene)
            and self.low <= gene <= self.high
            for gene in self.genes
        )
