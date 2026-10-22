# GA Toolbox and CVRP Assignment

## Project structure

- `ga_toolbox/chromosomes.py`: binary, integer, and float chromosomes.
- `ga_toolbox/settings.py`: GA defaults and configuration validation (`GAConfig`).
- `ga_toolbox/base_classes.py`: interfaces for the genetic operators.
- `ga_toolbox/selection.py`: tournament and roulette-wheel selection operators.
- `ga_toolbox/genetic_algorithm.py`: the reusable GA loop.
- `tests/`: tests for chromosomes and the GA engine.
- `cvrp/`: the CVRP implementation (problem, cost, fitness).

## Run tests

From the project root (use `python3` on Mac/Linux, `python` on Windows):

```bash
python3 -m tests.test_chromosomes
python3 -m tests.test_genetic_algorithm
```

## Team interface (agreed contract)

Every operator must follow these rules:
- Never modify the inputs. Return NEW chromosomes (use `copy()`).
- Use the `random` module for randomness (the engine seeds it).
- No CVRP code inside `ga_toolbox/`.

| Class | File | Method |
|---|---|---|
| Chromosome | `ga_toolbox/chromosomes.py` | `.genes`, `.fitness`, `.feasible`, `.copy()`, `.is_valid()`, `Class.random(length, **kwargs)` |
| Selection | `ga_toolbox/selection.py` | `select(population, n, maximize)` -> list of n chromosomes |
| Crossover | `ga_toolbox/crossover.py` | `crossover(parent1, parent2)` -> `(child1, child2)` |
| Mutation | `ga_toolbox/mutation.py` | `mutate(chromosome, rate)` -> new chromosome |
| Replacement | `ga_toolbox/replacement.py` | `replace(population, offspring, maximize)` -> new population, same size |

Import the base classes with `from ga_toolbox.base_classes import Selection` (or Crossover, Mutation, Replacement).
`maximize=False` means lower fitness is better (CVRP minimizes distance).

Use `TournamentSelection(tournament_size=3)` or `RouletteSelection()` from
`ga_toolbox`. Both return copies, support minimization and maximization, and
prefer feasible chromosomes over infeasible ones when any feasible candidates
are available.

## Use the toolbox

```python
from ga_toolbox import GAConfig, GeneticAlgorithm

ga = GeneticAlgorithm(init_fn, fitness_fn, feasibility_fn,
                      selection, crossover, mutation, replacement, config=GAConfig())
best, history = ga.run()
```

- `init_fn()` returns a new random chromosome.
- `fitness_fn(chromosome)` returns a number (the cost).
- `feasibility_fn(chromosome)` returns True or False.
- `run()` returns the best chromosome and the best fitness at each generation.

## Infeasible solutions: penalty method

The engine checks feasibility, and adds `config.infeasible_penalty` to the fitness of infeasible
chromosomes, so any feasible solution ranks above any infeasible one. The CVRP fitness function
may also add a penalty proportional to the violation (excess load, extra routes) so the GA can
move gradually toward feasible solutions. The engine only adds the constant penalty; do not add
the same constant again in `fitness_fn`.

Always check `best.feasible` before printing the final CVRP answer.

## Elitism

The engine keeps the best `config.elitism_count` chromosomes of each generation
(`_apply_elitism`). Replacement classes therefore only decide how offspring and parents are merged.

## CVRP data (from the assignment's example)

17 locations (depot = node 0, customers 1 to 16), 4 vehicles, capacity 15,
a ready-made 17x17 distance matrix (no coordinates), and the demands list from the example page.
