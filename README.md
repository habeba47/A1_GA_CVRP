# GA Toolbox and CVRP Assignment

## Project structure

- `ga_toolbox/chromosomes.py`: binary, integer, and float chromosomes.
- `ga_toolbox/settings.py`: GA defaults and configuration validation.
- `ga_toolbox/base_classes.py`: interfaces for genetic operators.
- `ga_toolbox/genetic_algorithm.py`: the reusable GA loop.
- `tests/`: tests for chromosomes and the GA engine.
- `cvrp/`: reserved for the CVRP implementation.

## Run tests

From the project root:

```bash
python -m tests.test_chromosomes
python -m tests.test_genetic_algorithm
```

## Use the toolbox

```python
from ga_toolbox import GAConfig, GeneticAlgorithm
```

Provide an initialization function, fitness function, feasibility function, and concrete selection, crossover, mutation, and replacement objects. `run()` returns the best chromosome and its fitness history.

The engine ranks feasible chromosomes above infeasible chromosomes and applies `infeasible_penalty` to infeasible fitness values. Avoid adding the same penalty twice unless that is intentional.

CVRP integration will be added after the team finishes the problem-specific components.
