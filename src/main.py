import random
import itertools
import matplotlib.pyplot as plt

DEBUG = False

def debug(message, debugging=DEBUG):
    if debugging:
        print(message)

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

def get_expected_payoff(focal_strat, strats, s: float):
    """Gets the expected payoff of a strategy given the strategies of all agents.
    Args:
        focal_strat: The focal player's strategy.
        strats ([]): All players' strategies, including the focal player's.
        s (float): The payoff for losing.`
    Returns:
        float: Expected payoff of the focal player's strategy.
    """
    opp_strats = strats[:]
    opp_strats.remove(focal_strat)
    payoffs = [get_payoff(focal_strat, opp_strat, s) for opp_strat in opp_strats]

    return sum(payoffs)/len(payoffs)

def p_switch(A, B, w, s):
    """Get the probability that agent A switches to agent B's strategy given their payoffs and other parameters.
    Args:
        A: The focal agent's strategy.
        B: An opposing agent's strategy.
        w: Parameter changes how influential the expected payoff difference is.
        s: Used to calculate the maximum possible payoff difference of 1 + s.
    Returns:
        float: Probability that the agent playing strategy B switches to strategy A.
    """
    return 1/2 + w * (get_expected_payoff(A, agents, s) - get_expected_payoff(B, agents, s)) / (2 * (1 + s))

# Parameters

strats = ["R", "P", "S"]
N = 1500 # Population size
init_agents = [strats[i % 3] for i in range(N)] # Initial conditions - even split of all strategies
runtime = 1000 # Number of epochs
ws = [0.0, 0.5, 1.0] # 0 <= w <= 1
ss = [0.25, 1.0, 4.0]

# Evolution

fig, axes = [None, None], [None, None]
for i in range(2):
    fig[i], axes[i] = plt.subplots(
        nrows=len(ws),
        ncols=len(ss),
        figsize=(8.5, 8.5),
        sharex=True,
        sharey=True,
        gridspec_kw={"wspace": 0.1, "hspace": 0.1},
    )

for w_i in range(len(ws)):
    for s_i in range(len(ss)):
        w, s = ws[w_i], ss[s_i]
        print(f"Running setup {w_i*len(ws) + s_i + 1}/{len(ws)*len(ss)} (w = {w}, s = {s}) for {runtime} epochs...")
        agents = init_agents[:]

        results = { # Index is time
            "R": [], # Number of agents playing R
            "P": [], # Number of agents playing P
            "S": [] # Number of agents playing S
        }

        for i in range(runtime):
            A = agents.pop(random.randint(0, len(agents)) - 1) # To prevent selection of the same agent for B
            B = agents[random.randint(0, len(agents)) - 1]
            agents.append(A)

            if A != B:
                p = p_switch(A, B, w, s)

                if p > random.random():
                    agents.remove(B) # Death of a strategy B
                    agents.append(A) # Replication of strategy A
                
            results["R"].append(agents.count("R"))
            results["P"].append(agents.count("P"))
            results["S"].append(agents.count("S"))

        # Time series

        axes[0][w_i, s_i].plot(results["R"], label="R")
        axes[0][w_i, s_i].plot(results["P"], label="P")
        if w_i == len(ws) - 1: axes[0][w_i, s_i].set_xlabel(f"s = {s:.2f}") # Only label if it is in the bottom row
        if s_i == 0: axes[0][w_i, s_i].set_ylabel(f"w = {w:.2f}") # Only label if it is in the leftmost column
        fig[0].supxlabel("Time (epochs)")
        fig[0].supylabel("Number of Agents")
        fig[0].suptitle("Evolution of Rock-Paper-Scissors Strategies Over Time", y=0.95, fontsize=20)

        # Phase plane

        axes[1][w_i, s_i].plot(
            results["R"],
            results["P"],
            markevery=[0, -1],
            marker='.',
            markerfacecolor='k',
            markeredgecolor='k'
        )
        if w_i == len(ws) - 1: # Only label if it is the bottom row
            axes[1][w_i, s_i].set_xlabel(f"s = {s:.2f}")
        if s_i == 0: # Only label if it is the leftmost column
            axes[1][w_i, s_i].set_ylabel(f"w = {w:.2f}")
        fig[1].supxlabel("Number of Agents Playing R")
        fig[1].supylabel("Number of Agents Playing P")
        fig[1].suptitle(f"Phase Plane of Evolution of Rock-Paper-Scissors Strategies", y=0.95, fontsize=20)

fig[0].savefig(f"results\\birth-death\\time_series.jpg")

fig[1].savefig(f"results\\birth-death\\phase_plane.jpg")