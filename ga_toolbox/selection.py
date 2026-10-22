import math
import random

from ga_toolbox.base_classes import Selection


def _check_args(population, n):
    if len(population) == 0:
        raise ValueError("population cannot be empty")
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")


def _is_better(first, second, maximize):
    if bool(first.feasible) != bool(second.feasible):
        return bool(first.feasible)
    if maximize:
        return first.fitness > second.fitness
    return first.fitness < second.fitness


class TournamentSelection(Selection):

    def __init__(self, tournament_size=3):
        if isinstance(tournament_size, bool) or not isinstance(tournament_size, int) \
                or tournament_size < 1:
            raise ValueError("tournament_size must be a positive integer")
        self.tournament_size = tournament_size

    def select(self, population, n, maximize):
        _check_args(population, n)
        size = min(self.tournament_size, len(population))

        chosen = []
        for _ in range(n):
            contestants = random.sample(population, size)  # no repeats inside one tournament
            winner = contestants[0]
            for challenger in contestants[1:]:
                if _is_better(challenger, winner, maximize):
                    winner = challenger
            chosen.append(winner.copy())
        return chosen


class RouletteSelection(Selection):

    def __init__(self, infeasible_share=0.1):
        if isinstance(infeasible_share, bool) or not isinstance(infeasible_share, (int, float)) \
                or not 0 <= infeasible_share <= 1:
            raise ValueError("infeasible_share must be a number between 0 and 1")
        self.infeasible_share = infeasible_share

    def select(self, population, n, maximize):
        _check_args(population, n)
        weights = self._weights(population, maximize)
        if sum(weights) <= 0:  # e.g. every chromosome is invalid
            weights = [1.0] * len(population)
        picks = random.choices(population, weights=weights, k=n)  # with replacement
        return [pick.copy() for pick in picks]

    def _weights(self, population, maximize):
        sign = 1.0 if maximize else -1.0  # after this, a larger score is always better
        scores = [sign * c.fitness for c in population]

        feasible = [i for i, c in enumerate(population)
                    if c.feasible and math.isfinite(scores[i])]
        infeasible = [i for i, c in enumerate(population)
                      if not c.feasible and math.isfinite(scores[i])]

        weights = [0.0] * len(population)
        for indices, mass in ((feasible, 1.0), (infeasible, self.infeasible_share)):
            if not indices:
                continue
            low = min(scores[i] for i in indices)
            high = max(scores[i] for i in indices)
            eps = 0.01 * (high - low) or 1.0
            raw = [scores[i] - low + eps for i in indices]
            total = sum(raw)
            for i, value in zip(indices, raw):
                weights[i] = mass * value / total
        return weights