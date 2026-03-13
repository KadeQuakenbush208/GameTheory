import sys
import random
import math
import matplotlib.pyplot as plt

DEBUG = True

# ---------- Functions ----------

def debug(message, debugging=DEBUG):
    """Prints the given message prepended with [DEBUG] if debugging.
    Args:
        message: The message to print
        debugging (bool): Only prints the message if this is true.
    """
    if debugging:
        print(f"[DEBUG] {message}")

def get_payoff(A, B, s: float):
    """Get the payoff for an game of non-zero-sum rock-paper-scissors.
    Args:
        A: Focal player's strategy. Must be "R", "P", or "S".
        B: Opponent's strategy. Must be "R", "P", or "S".
        s: Payoff for losing.
    Returns:
        float/int: Payoff for the focal player
    """
    payoffs = {
        "R": {
            "R": 0,
            "P": -s,
            "S": 1
            },
        "P": {
            "R": 1,
            "P": 0,
            "S": -s
            },
        "S": {
            "R": -s,
            "P": 1,
            "S": 0
            }
    }

    return payoffs[A][B]

def expected_payoff(focal_strat, population_strats, s: float | int):
    """Calculates the expected payoff of a strategy given the strategies of all agents.
    Args:
        focal_strat: Focal player's strategy.
        population_strats ([]): All players' strategies, including the focal player's.
        s (float/int): Payoff for losing.
    Returns:
        float: Expected payoff of the focal player's strategy.
    """
    opp_strats = population_strats[:]
    opp_strats.remove(focal_strat)

    # Count the number of occurrences of each strategy, then get the payoff for each unique strategy
    payoffs_sum = sum(get_payoff(focal_strat, opp_strat, s) * opp_strats.count(opp_strat) for opp_strat in set(opp_strats))

    return payoffs_sum / len(opp_strats)

def p_switch(B, A, population_strats, w: float, s: float | int):
    """Calculates the probability that agent A switches to agent B's strategy given their payoffs and other parameters, like so: `p = 1/2 + w(π_A - π_B) / 2Δπ_max`.
    Args:
        B: Focal agent's strategy.
        A: An opposing agent's strategy.
        w (float): Decides how influential the expected payoff difference is, such that 0.5 - w/2 <= p <= 0.5 + w/2
        s (float/int): Payoff for losing.
    Returns:
        float: Probability that the agent playing strategy B switches to strategy A.
    """
    pi_A = expected_payoff(A, population_strats, s)
    pi_B = expected_payoff(B, population_strats, s)
    max_pi_diff = 1 + s

    return 0.5 + w * (pi_A - pi_B) / (2 * max_pi_diff)

def def_seasonal_birth_factor(wavelength: float = 1.0, min: float = 0.0):
    """Creates a sinusoidal function meant to depict seasonally fluctuating birth rates with a peak in "spring".

    The standard model used for this is `B(t) = B_0 + Asin(2πt/Τ + φ)`, where:
    - `B(t)`: Birth rate at time `t`
    - `B_0`: Average birth rate
    - `A`: Amplitude of seasonal variation
    - `T`: Length of one cycle/year
    - `φ`: Phase shift, which dictates when birth rates peak (`φ = π/2 - 2πt_peak / T`)
    Args:
        wavelength (float): Wavelength of the function, indicating the length of a cycle.
        min (float): The minimum possible value this function can return in `[0.0, 1.0)`, such that `1 - min` = the amplitude of the wave.
    Returns:
        function: A function that returns a value between `[min, 1.0]` given a `t`.
    """
    # Invariants are precomputed

    B_0 = 0.5 + min/2
    A = 0.5 - min/2
    T = wavelength
    phi = 0 # Peaks at t = T/4 => φ = π/2 - 2π/T * T/4 = 0

    omega = math.tau / T # τ = 2π

    def seasonal_birth_factor(t: int | float) -> float:
        """Calculates a value that oscillates with `t`. The minimum of this function is at `t = n * wavelength` for any integer `n` and the previously given `wavelength`.
        Args:
            t (int/float): Variable that indicates time.
        Returns:
            float: A value in `[min, 1.0]`.
        """
        return B_0 + A * math.sin(omega * T + phi)

    return seasonal_birth_factor

def def_seasonal_death_factor(wavelength: float = 1.0, min: float = 0.0):
    """Creates a sinusoidal function meant to depict seasonally fluctuation death rates with a peak in "winter".

    The standard model used for this is `D(t) = D_0 + Asin(2πt/Τ + φ)`, where:
    - `D(t)`: Death rate at time `t`
    - `D_0`: Average death rate
    - `A`: Amplitude of seasonal variation
    - `T`: Length of one cycle/year
    - `φ`: Phase shift, which dictates when death rates peak (`φ = π/2 - 2πt_peak / T`)
    Args:
        wavelength (float): Wavelength of the function, indicating the length of a cycle.
        min (float): The minimum possible value this function can return in `[0.0, 1.0)`, such that `1 - min` = the amplitude of the wave.
    Returns:
        function: A function that returns a value between `[min, 1.0]` given a `t`.
    """
    # Invariants are precomputed

    D_0 = 0.5 + min/2
    A = 0.5 - min/2
    T = wavelength
    phi = math.pi / 2 # Peaks at t = 0 => φ = π/2 - 2π/T * 0 = π/2

    omega = math.tau / T # τ = 2π

    def seasonal_death_factor(t: int | float) -> float:
        """
        Calculates a value that oscillates with `t`. The minimum of this function is at `t = n * wavelength - wavelength/4` for any integer `n` and the previously given `wavelength`.
        Args:
            t (int/float): Variable that indicates time.
        Returns:
            float: A value between `[min, 1.0]`.
        """
        return D_0 + A * math.sin(omega * t + phi)

    return seasonal_death_factor

# ---------- Parameters & initialisations ----------

# Experiment specification

RUNTIME = 150000 # Number of epochs
FLUCTUATING_SEASONS = False # Enables/disables variable birth/death rates based on simulated seasons

# Population and runtime specification

STRATS = ["R", "P", "S"]
N = 1500 # Population size
init_population_strats = [STRATS[i % len(STRATS)] for i in range(N)] # Initial conditions - even split of all strategies

# Selection factors

ws = [0.05, 0.5, 0.95] # Selection strength, 0 <= w <= 1
ss = [0.5, 1.0, 2.0] # Cost of losing

cycle_len = RUNTIME // 4 # The length of one seasonal cycle
min_season_factor = 0.01 # Specifies the minimum value the factor used for simulating seasons can take on

# Graph initialisation

plot_count = 3 if FLUCTUATING_SEASONS else 2
fig, axs = [None] * plot_count, [None] * plot_count
for i in range(plot_count):
    fig[i], axs[i] = plt.subplots(
        nrows=len(ws),
        ncols=len(ss),
        figsize=(8.5, 8.5),
        sharex=True,
        sharey=True,
        gridspec_kw={"wspace": 0.1, "hspace": 0.1}
    )

# ---------- Evolution ----------

for w_i in range(len(ws)):
    for s_i in range(len(ss)):
        w, s = ws[w_i], ss[s_i]
        print(f"Running setup {w_i*len(ws) + s_i + 1}/{len(ws)*len(ss)} (w = {w}, s = {s}) with a{" seasonally fluctuating" if FLUCTUATING_SEASONS else "n initial"} population of {N:,} for {RUNTIME:,} epochs...")
        population_strats = init_population_strats[:]

        results = { # Index is time
            "R": [], # Number of agents playing R
            "P": [], # Number of agents playing P
            "S": [] # Number of agents playing S
        }
        normalised_results = {
            "R": [], # Proportion of agents playing R with respect to R + P
            "P": [] # Proportion of agents playing P with respect to R + P
        }

        # Precompute the functions needed for calculating seasonal fluctuation factors for efficiency, since they are invariant with respect to the current `w` and `s` parameters
        seasonal_birth_factor = def_seasonal_birth_factor(cycle_len, min_season_factor)
        seasonal_death_factor = def_seasonal_death_factor(cycle_len, min_season_factor)

        for i in range(RUNTIME):
            A = population_strats.pop(random.randint(0, len(population_strats)) - 1) # Popped to prevent selection of the same agent for B
            B = population_strats[random.randint(0, len(population_strats)) - 1]
            population_strats.append(A)

            # Strategy comparison

            if A != B:
                p = p_switch(B, A, population_strats, w, s) # Probability that a strategy B is changed to A

                if FLUCTUATING_SEASONS:
                    # Births are considered independent of deaths, so they are assessed separately
                    if p * seasonal_birth_factor(i) > random.random():
                        population_strats.append(A) # Replication of strategy A
                    if p * seasonal_death_factor(i) > random.random():
                        population_strats.remove(B) # Death of a strategy B
                else:
                    if p > random.random():
                        population_strats.append(A) # Replication of strategy A
                        population_strats.remove(B) # Death of strategy B
            
            # Population distribution recording

            R_count = population_strats.count("R")
            P_count = population_strats.count("P")
            S_count = population_strats.count("S")

            results["R"].append(R_count)
            results["P"].append(P_count)
            results["S"].append(S_count)
            
            if FLUCTUATING_SEASONS: # Also record normalised results if considering fluctuating seasons
                population_total = R_count + P_count

                normalised_results["R"].append(R_count / population_total if population_total != 0 else 0)
                normalised_results["P"].append(P_count / population_total if population_total != 0 else 0)

        # Time series plot

        axs[0][w_i, s_i].plot(results["R"], label="R")
        axs[0][w_i, s_i].plot(results["P"], label="P")
        axs[0][w_i, s_i].legend(
            loc="upper left",
            borderpad=0.3,
            labelspacing=0.05,
            fontsize="small",
            handlelength=1.5  
        )
        if w_i == len(ws) - 1: axs[0][w_i, s_i].set_xlabel(f"s = {s:.2f}") # Only label if it is in the bottom row
        if s_i == 0: axs[0][w_i, s_i].set_ylabel(f"w = {w:.2f}") # Only label if it is in the leftmost column

        # Also plot normalised results if considering fluctuating seasons
        if FLUCTUATING_SEASONS:
            axs[2][w_i, s_i].plot(normalised_results["R"], label="R")
            axs[2][w_i, s_i].plot(normalised_results["P"], label="P")
            axs[2][w_i, s_i].legend(
                loc="upper left",
                borderpad=0.3,
                labelspacing=0.05,
                fontsize="small",
                handlelength=1.5  
            )
            if w_i == len(ws) - 1: axs[2][w_i, s_i].set_xlabel(f"s = {s:.2f}") # Only label if it is in the bottom row
            if s_i == 0: axs[2][w_i, s_i].set_ylabel(f"w = {w:.2f}") # Only label if it is in the leftmost column

        # Phase plane plot

        axs[1][w_i, s_i].plot(
            results["R"],
            results["P"],
            markevery=[0, -1],
            marker='.',
            markerfacecolor='k',
            markeredgecolor='k'
        )
        axs[1][w_i, s_i].set_xlim(-0.05*N, 1.05*N)
        axs[1][w_i, s_i].set_ylim(-0.05*N, 1.05*N)
        if w_i == len(ws) - 1: # Only label if it is the bottom row
            axs[1][w_i, s_i].set_xlabel(f"s = {s:.2f}")
        if s_i == 0: # Only label if it is the leftmost column
            axs[1][w_i, s_i].set_ylabel(f"w = {w:.2f}")

# ---------- Plot labelling and saving ----------

if FLUCTUATING_SEASONS:
    fig[0].supxlabel("Time (epochs)")
    fig[0].supylabel("Number of Agents")  
    fig[0].suptitle("Evolution of Rock-Paper-Scissors Strategies Over Time\nwith Seasonally Fluctuating Birth and Death Rates", y=0.975, fontsize=20)

    fig[1].supxlabel("Number of Agents Playing R")
    fig[1].supylabel("Number of Agents Playing P")
    fig[1].suptitle(f"Phase Plane of Evolution of Rock-Paper-Scissors Strategies\nwith Seasonally Fluctuating Birth and Death Rates", y=0.975, fontsize=20)

    fig[2].supxlabel("Time (epochs)")
    fig[2].supylabel("Proportion of Agents")  
    fig[2].suptitle("Evolution of Rock-Paper-Scissors Strategies Over Time with\nSeasonally Fluctuating Birth and Death Rates (Normalised)", y=0.975, fontsize=19)

    fig[0].savefig(f"results\\seasonally_fluctuating\\time_series.jpg")
    fig[1].savefig(f"results\\seasonally_fluctuating\\phase_plane.jpg")
    fig[2].savefig(f"results\\seasonally_fluctuating\\time_series-normalised.jpg")
else:
    fig[0].supxlabel("Time (epochs)")
    fig[0].supylabel("Number of Agents")
    fig[0].suptitle("Evolution of Rock-Paper-Scissors Strategies Over Time\nwith a Fixed Population Size", y=0.975, fontsize=20)

    fig[1].supxlabel("Number of Agents Playing R")
    fig[1].supylabel("Number of Agents Playing P")
    fig[1].suptitle(f"Phase Plane of Evolution of Rock-Paper-Scissors Strategies\nwith Fixed Population Size", y=0.975, fontsize=20)

    fig[0].savefig(f"results\\fixed\\time_series.jpg")
    fig[1].savefig(f"results\\fixed\\phase_plane.jpg")