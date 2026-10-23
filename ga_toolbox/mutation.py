import random
from .base_classes import Mutation
from abc import ABC, abstractmethod
from .crossover import _new_child
from .chromosomes import Chromosome, BinaryChromosome, FloatChromosome, IntegerChromosome

def _check_rate(rate):
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
        raise ValueError("rate must be a number between 0 and 1")

class Mutation(ABC):
    @abstractmethod
    def mutate(self, chromosome: Chromosome, mutation_rate: float):

class BinaryMutation(Mutation):
    def mutate(self, chromosome: BinaryChromosome, mutation_rate: float):
        
        _check_rate(mutation_rate)

        new_genes = chromosome.genes.copy()

        for idx in range(0, len(chromosome)):
            r = random.random()
            if r < mutation_rate: # bit flip
                if new_genes[idx] == 0:
                    new_genes[idx] = 1
                else:
                    new_genes[idx] = 0
        
        return _new_child(chromosome, new_genes)

class UniformFloatingPointMutation(Mutation):
    def mutate(self, chromosome: FloatChromosome, mutation_rate: float):

        _check_rate(mutation_rate)

        new_genes = chromosome.genes.copy()
        lower_bound, upper_bound = chromosome.low, chromosome.high
        for idx in range(0, len(new_genes)):
            r0 = random.random()

            if r0 < mutation_rate:
                delta_lower = new_genes[idx] - lower_bound
                delta_upper = upper_bound - new_genes[idx]
            
                r1 = random.random() # to choose which delta to use
                r2 = random.random() # the weight of the delta
            
                if r1 > 0.5: # use delta_upper
                    new_genes[idx] = new_genes[idx] + (delta_upper * r2)
                else: # use delta lower
                    new_genes[idx] = new_genes[idx] - (delta_lower * r2)

        return _new_child(chromosome, new_genes)

class IntegerMutation(Mutation):
    def mutate(self, chromosome: IntegerChromosome, mutation_rate: float):

        if chromosome.permutation: # should not be integer mutated
            raise ValueError("Error: a permutated chromosome cannot be mutated using this method.")

        _check_rate(mutation_rate)

        new_genes = chromosome.genes.copy()
        lower_bound, upper_bound = chromosome.low, chromosome.high
        for idx in range(0, len(new_genes)):
            r0 = random.random()

            if r0 < mutation_rate:
                delta_lower = new_genes[idx] - lower_bound
                delta_upper = upper_bound - new_genes[idx]
            
                r1 = random.random() # to choose which delta to use
                r2 = random.random() # the weight of the delta
            
                if r1 > 0.5: # use delta_upper
                    new_genes[idx] = new_genes[idx] + int(round(delta_upper * r2))
                else: # use delta lower
                    new_genes[idx] = new_genes[idx] - int(round(delta_lower * r2))

        return _new_child(chromosome, new_genes)

class SwapMutation(Mutation):
    def mutate(self, chromosome: Chromosome, mutation_rate: float):
        
        _check_rate(mutation_rate)

        new_genes = chromosome.genes.copy()
        r = random.random()

        if r < mutation_rate and len(new_genes) >= 2:
            i, j = random.sample(range(len(new_genes)), 2) # pick 2 indices 
            new_genes[i], new_genes[j] = new_genes[j], new_genes[i] # swap values

        return _new_child(chromosome, new_genes)
