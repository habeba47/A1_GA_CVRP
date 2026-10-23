# GA Toolbox and CVRP

Soft Computing, Assignment 1 (Cairo University, Faculty of Computers and Artificial Intelligence).

A genetic algorithm (GA) toolbox written from scratch in Python (no GA libraries), and a program that uses it to solve the Capacitated Vehicle Routing Problem (CVRP).

## Quick start

From the project root (use `python` instead of `python3` on Windows):

```bash
python3 -m cvrp.run_cvrp
```

This runs the GA on the assignment's example (17 locations, 4 vehicles, capacity 15) and prints the routes. With the default seed it finds a feasible solution with a total distance of **6208**, and all 4 vehicles are fully loaded (15 out of 15). It takes about 15 seconds.

## Project structure

```
ga_toolbox/            the reusable GA toolbox (no CVRP code inside)
  chromosomes.py       binary, integer (with permutation mode), float chromosomes
  settings.py          GAConfig: all hyperparameters with defaults and validation
  base_classes.py      interfaces: Selection, Crossover, Mutation, Replacement
  selection.py         TournamentSelection, RouletteSelection
  crossover.py         MultiPointCrossover, OrderCrossover
  mutation.py          BinaryMutation, IntegerMutation, UniformFloatingPointMutation, SwapMutation
  replacement.py       GenerationalReplacement, SteadyStateReplacement
  genetic_algorithm.py the GA engine (main loop, elitism, infeasible handling)
cvrp/                  the CVRP application
  problem.py           data, decoding chromosome -> routes, feasibility check
  cost.py              route cost and total distance
  fitness.py           fitness function (distance + penalties)
  output.py            prints the solution in the required format
  run_cvrp.py          main script: wires the toolbox to the CVRP
data/example.py        the example instance (distance matrix, demands, capacities)
tests/                 tests for every module
```

## Run the tests

```bash
python3 -m tests.test_chromosomes
python3 -m tests.test_genetic_algorithm
python3 -m tests.test_selection
python3 -m tests.test_crossover
python3 -m tests.test_mutation
python3 -m tests.test_replacement
python3 -m pytest tests/test_cvrp.py      # needs: pip install pytest
```

## Using the toolbox

```python
from ga_toolbox import (GAConfig, GeneticAlgorithm, IntegerChromosome,
                        TournamentSelection, OrderCrossover, SwapMutation,
                        GenerationalReplacement)

ga = GeneticAlgorithm(
    init_fn=lambda: IntegerChromosome.random(10, low=1, permutation=True),
    fitness_fn=my_fitness,          # chromosome -> number (the cost)
    feasibility_fn=my_feasibility,  # chromosome -> True / False
    selection=TournamentSelection(tournament_size=3),
    crossover=OrderCrossover(),
    mutation=SwapMutation(),
    replacement=GenerationalReplacement(),
    config=GAConfig(),              # optional, defaults are used if omitted
)
best, history = ga.run()
```

- `init_fn()` returns a new random chromosome.
- `fitness_fn(chromosome)` returns a finite number.
- `feasibility_fn(chromosome)` returns `True` or `False`.
- `run()` returns the best chromosome and a list with the best fitness found so far at each generation (`history[0]` is the initial population, so its length is `generations + 1`).

To reuse the toolbox for another problem, only these three functions and the choice of operators change. The GA code stays the same.

### Chromosomes

| Class | Genes | Notes |
|---|---|---|
| `BinaryChromosome` | 0 or 1 | |
| `IntegerChromosome` | integers in `[low, high]` | `permutation=True` makes the genes a permutation of `low .. low+length-1` (each value exactly once). This is how CVRP represents the visiting order of customers. |
| `FloatChromosome` | real numbers in `[low, high]` | |

Every chromosome has `.genes`, `.fitness`, `.feasible`, `.copy()`, `.is_valid()` and `Class.random(length, **kwargs)`.

### Configuration (`GAConfig`)

All values have defaults and are validated when the config is created (a wrong value raises `ValueError`).

| Parameter | Default | Meaning |
|---|---|---|
| `population_size` | 100 | chromosomes per generation |
| `generations` | 300 | number of generations |
| `crossover_rate` | 0.9 | probability that two parents are crossed |
| `mutation_rate` | 0.1 | passed to the mutation operator (see note below) |
| `elitism_count` | 2 | best chromosomes kept unchanged each generation |
| `tournament_size` | 3 | group size for tournament selection |
| `maximize` | `False` | `False` = lower fitness is better (CVRP minimizes distance) |
| `seed` | `None` | random seed for reproducible runs |
| `infeasible_penalty` | 100000.0 | added to the cost of infeasible solutions |
| `steady_state_replacement_count` | 2 | children inserted per generation by `SteadyStateReplacement` |

**Meaning of `mutation_rate`.** For `BinaryMutation`, `IntegerMutation` and `UniformFloatingPointMutation` it is the probability that **each gene** is mutated. For `SwapMutation` it is the probability that **the whole chromosome** gets one swap.

### Operators

| Type | Class | What it does |
|---|---|---|
| Selection | `TournamentSelection(tournament_size)` | picks the best of a random group |
| Selection | `RouletteSelection(infeasible_share)` | probability proportional to quality, works for minimization, gives infeasible chromosomes only a small share |
| Crossover | `MultiPointCrossover(num_points)` | swaps segments between cut points (binary, float, integer; repairs permutations) |
| Crossover | `OrderCrossover()` | for permutations: keeps a segment from one parent and fills the rest in the other parent's order |
| Mutation | `BinaryMutation` | bit flip |
| Mutation | `IntegerMutation` | moves a gene inside `[low, high]` (not for permutations) |
| Mutation | `UniformFloatingPointMutation` | moves a gene inside `[low, high]` |
| Mutation | `SwapMutation` | swaps two genes (keeps permutations valid) |
| Replacement | `GenerationalReplacement` | offspring replace the old population |
| Replacement | `SteadyStateReplacement` | only the best `steady_state_replacement_count` offspring replace the worst chromosomes |

### Contract for operators

- Never modify the inputs. Return new chromosomes (use `copy()`).
- Use the `random` module for randomness (the engine seeds it from `config.seed`).
- No CVRP code inside `ga_toolbox/`.

| Interface | Method |
|---|---|
| `Selection` | `select(population, n, maximize)` returns a list of `n` chromosomes |
| `Crossover` | `crossover(parent1, parent2)` returns `(child1, child2)` |
| `Mutation` | `mutate(chromosome, rate)` returns a new chromosome |
| `Replacement` | `replace(population, offspring, config)` returns the next population (same size) |

## How the engine works

Each generation:

1. **Selection** picks two parents.
2. **Crossover** (with probability `crossover_rate`) creates two children, otherwise the children are copies of the parents.
3. **Mutation** is applied to each child, then the child is evaluated.
4. This repeats until there are `population_size` offspring.
5. **Replacement** builds the next population from the old population and the offspring.
6. **Elitism**: the best `elitism_count` chromosomes of the old population are put back in place of the worst new ones, so the best solution is never lost.

## Infeasible solutions: penalty method

- A chromosome with invalid genes (for example a broken permutation) is marked infeasible and gets the worst possible fitness. The user's functions are not called for it.
- For a valid chromosome the engine calls `feasibility_fn`. If it returns `False`, the engine adds `config.infeasible_penalty` to the cost. The engine also ranks any feasible chromosome above any infeasible one.
- The engine adds this constant penalty itself, so `fitness_fn` must **not** add it again. `fitness_fn` may add its own penalty proportional to the violation (for example the excess load) so the GA is guided toward feasible solutions.
- Always check `best.feasible` before using the final answer. `run_cvrp.py` only prints the routes when it is `True`.

## CVRP modeling

- **Representation:** an `IntegerChromosome` with `permutation=True`. The genes are the customers 1 to 16, each exactly once, in visiting order. The depot is node 0.
- **Decoding** (`CVRPProblem.decode`): customers are taken in chromosome order and put in the first route that still has enough capacity. If none fits, a new route starts. Every route begins and ends at the depot.
- **Feasibility** (`CVRPProblem.is_feasible`): every customer appears exactly once, no route exceeds its capacity, and the number of routes does not exceed the number of vehicles.
- **Fitness** (`CVRPFitness.fitness`): total distance of all routes, plus `penalty_weight` times (extra vehicles + capacity excess). A chromosome with missing, duplicated or unknown customers gets a much larger penalty.
- **Output** (`cvrp/output.py`): prints each vehicle's route with the load after each stop, the distance and load of each route, and the totals. It refuses to print an infeasible solution.

## Data

The example instance in `data/example.py`: 17 locations (depot = node 0, customers 1 to 16), 4 vehicles of capacity 15, a ready-made 17 x 17 distance matrix (no coordinates), and the demands list.