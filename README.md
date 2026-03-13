# Usage Instructions

## Global parameters

Various global parameters can be tweaked, including:

- `N`: Population size - recommended at around 1500
- `RUNTIME`: Number of epochs the program runs for - recommended at at least 100,000
- `ws`: Values of `w` in [0.0, 1.0] that are used when calculating the probability of a strategy switch/birth/death; controls the volatility of a strategy population's trajectory
- `ss`: Values of `s` greater than 0.0 that specify the cost of a loss; controls how stable a strategy population is about a central fixed point

## Modes

This project has three main setups it can use:

1. Fixed population size, strategies can only be swapped
2. Variable population size, strategy births and deaths occur independently, birth/death rates are influenced by a factor that simulates seasons
3. The same as (2), with the addition of population density/sparsity that simulates resource scarcity/abundance, respectively, with the option to add leeway

### Mode 1

To enable Mode 1, in `main.py`, set `FLUCTUATING_SEASONS = False` and `LIMITING_ENVIRONMENT = False`.

The results will be saved to `/results/fixed`.

### Mode 2

To enable Mode 2, in `main.py`, set `FLUCTUATING_SEASONS = True` and `LIMITING_ENVIRONMENT = False`. This modes simulates seasons, such that birth and death rates peak in the equivalent of "spring" (`i = n * cycle_len / 4`) and "winter" (`i = n * cycle_len`), respectively, for all integers `n`.

This mode has some additional parameters that can be adjusted in `main.py`:

- `cycle_len`: Length of one cycle/year; wavelength of the sine wave used when calculating probability
- `min_season_factor`: Minimum the additional probability factor can be set to - lower values results in a lower amplitude

The results will be saved to `/results/seasons`.

### Mode 3

To enable Mode 3, in `main.py`, set `FLUCTUATING_SEASONS = True` and `LIMITING_ENVIRONMENT = True`. This mode simulates a global environment whose resources are limited, which in turn limits how great the global population can grow.

This mode has some additional parameters that can be adjusted in `main.py`:

- `carrying_capacity`: Soft global population maximum - the global population size tends to stabilise at `carrying_capacity / 2`
- `leeway`: How strict the carrying capacity is, in [0.0, 1.0]; allows the global population size to fluctuate more - recommended closer to 0.0

The results will be saved to `/results/seasons_and_crowding`.