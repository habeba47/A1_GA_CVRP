from abc import ABC, abstractmethod


class Selection(ABC):
    @abstractmethod
    def select(self, population, n, maximize):
        pass


class Crossover(ABC):
    @abstractmethod
    def crossover(self, parent1, parent2):
        pass


class Mutation(ABC):
    @abstractmethod
    def mutate(self, chromosome, rate):
        pass


class Replacement(ABC):
    @abstractmethod
    def replace(self, population, offspring, maximize):
        pass
