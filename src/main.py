import sys
import random
import math
import matplotlib.pyplot as plt

DEBUG = True

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

def expected_payoff(focal_strat, population_strats, s: float):
    """Calculates the expected payoff of a strategy given the strategies of all agents.
    Args:
        focal_strat: Focal player's strategy.
        strats ([]): All players' strategies, including the focal player's.
        s (float): Payoff for losing.
    Returns:
        float: Expected payoff of the focal player's strategy.
    """
    opp_strats = population_strats[:]
    opp_strats.remove(focal_strat)

    # Count the number of occurrences of each strategy, then get the payoff for each unique strategy
    payoffs_sum = sum(get_payoff(focal_strat, opp_strat, s) * opp_strats.count(opp_strat) for opp_strat in set(opp_strats))

    return payoffs_sum / len(opp_strats)

def p_switch(B, A, population_strats, w, s):
    """Calculate the probability that agent A switches to agent B's strategy given their payoffs and other parameters.
    Args:
        B: Focal agent's strategy.
        A: An opposing agent's strategy.
        w: Decides how influential the expected payoff difference is, such that 0.5 - w/2 <= p <= 0.5 + w/2
        s: Payoff for losing.
    Returns:
        float: Probability that the agent playing strategy B switches to strategy A.
    """
    return 1/2 + w * (expected_payoff(A, population_strats, s) - expected_payoff(B, population_strats, s)) / (2 * (1 + s))

# Parameters & initialisations

STRATS = ["R", "P", "S"]
N = 1500 # Population size
init_population_strats = [STRATS[i % len(STRATS)] for i in range(N)] # Initial conditions - even split of all strategies
RUNTIME = 150000 # Number of epochs
ws = [0.05, 0.5, 0.95] # Selection strength, 0 <= w <= 1
ss = [0.5, 1.0, 2.0] # Cost of losing

fig, axs = [None, None], [None, None]
for i in range(2):
    fig[i], axs[i] = plt.subplots(
        nrows=len(ws),
        ncols=len(ss),
        figsize=(8.5, 8.5),
        sharex=True,
        sharey=True,
        gridspec_kw={"wspace": 0.1, "hspace": 0.1}
    )

# Evolution

for w_i in range(len(ws)):
    for s_i in range(len(ss)):
        w, s = ws[w_i], ss[s_i]
        print(f"Running setup {w_i*len(ws) + s_i + 1}/{len(ws)*len(ss)} (w = {w}, s = {s}) for {RUNTIME:,} epochs...")
        population_strats = init_population_strats[:]

        results = { # Index is time
            "R": [], # Number of agents playing R
            "P": [], # Number of agents playing P
            "S": [] # Number of agents playing S
        }

        for i in range(RUNTIME):
            A = population_strats.pop(random.randint(0, len(population_strats)) - 1) # Popped to prevent selection of the same agent for B
            B = population_strats[random.randint(0, len(population_strats)) - 1]
            population_strats.append(A)

            if A != B:
                p = p_switch(B, A, population_strats, w, s) # Probability that a strategy B is changed to A

                if p > random.random():
                    population_strats.remove(B) # Death of a strategy B
                    population_strats.append(A) # Replication of strategy A
                
            results["R"].append(population_strats.count("R"))
            results["P"].append(population_strats.count("P"))
            results["S"].append(population_strats.count("S"))

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
        fig[0].supxlabel("Time (epochs)")
        fig[0].supylabel("Number of Agents")
        fig[0].suptitle("Evolution of Rock-Paper-Scissors Strategies Over Time", y=0.95, fontsize=20)

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
        fig[1].supxlabel("Number of Agents Playing R")
        fig[1].supylabel("Number of Agents Playing P")
        fig[1].suptitle(f"Phase Plane of Evolution of Rock-Paper-Scissors Strategies", y=0.95, fontsize=20)

fig[0].savefig(f"results\\birth-death\\time_series.jpg")

fig[1].savefig(f"results\\birth-death\\phase_plane.jpg")