from ga_toolbox import BinaryMutation, UniformFloatingPointMutation, IntegerMutation, SwapMutation, Mutation, GAConfig
from ga_toolbox import Chromosome, BinaryChromosome, IntegerChromosome, FloatChromosome

def test_mutation(chromosome: Chromosome, mutator_class: Mutation, mutation_rate: float, test_name: str):
    print(test_name)
    mutator = mutator_class()
    res = mutator.mutate(chromosome, mutation_rate)
    print(f"\toriginal Chromosome: {chromosome.genes}\n\tMutated Chromosome: {res.genes}")
    return res

test_mutation(BinaryChromosome.random(10), BinaryMutation, 0.9, "Binary Mutation:")
test_mutation(IntegerChromosome.random(10, 0, 100), IntegerMutation, 0.9, "Integer Mutation:")
test_mutation(FloatChromosome.random(5, 0, 100), UniformFloatingPointMutation, 0.9, "Float Mutation:")
test_mutation(IntegerChromosome.random(10, 0, 100), SwapMutation, 0.9, "Swap Mutation:")
test_mutation(IntegerChromosome.random(10, 0, 100, permutation=True), SwapMutation, 0.9, "Swap Mutation (with Permutation):")
try:
    test_mutation(IntegerChromosome.random(10, 0, 100, permutation=True), IntegerMutation, 0.9, "Test Permutation on Integer Chromosomes: ")
    AssertionError("Should have returned an error")
except ValueError as e:
    print("\tif this is printed == Success")
