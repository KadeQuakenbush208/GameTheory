import random
import itertools
import matplotlib.pyplot as plt

DEBUG = False

def debug(message, debugging=DEBUG):
    if debugging:
        print(message)

def p_switch(A, B, w, s):
    """Get the probability that agent A switches to agent B's strategy given their payoffs and other parameters.
    Args:
        A: Agent A's strategy.
        B: Agent B's strategy.
        w: Parameter changes how influential the expected payoff difference is.
        s: Used to calculate the maximum possible payoff difference of 1 + s.
    Returns:
        float: Probability that agent A switches to agent B's strategy
    """
    return 1/2 + w * (get_expected_payoff(A, agents, s) - get_expected_payoff(B, agents, s)) / (2 * (1 + s))

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
        s (float): The payoff for losing
    Returns:
        float: Expected payoff of the focal player's strategy
    """
    opp_strats = strats[:]
    opp_strats.remove(focal_strat)
    payoffs = [get_payoff(focal_strat, opp_strat, s) for opp_strat in opp_strats]

    return sum(payoffs)/len(payoffs)

strats = ["R", "P", "S"]
N = 1500 # Population size
runtime = 100000 # Number of epochs
ws = [0.25, 0.5, 0.75]
ss = [0.75, 1.5, 3]

for permut in [(w, s) for w in ws for s in ss]:
    print(f"Running setup w = {permut[0]}, s = {permut[1]}...")
    agents = [strats[i % 3] for i in range(N)]
    w = permut[0]
    s = permut[1]

    results = { # Index is time
        "R": [], # Number of agents playing R
        "P": [], # Number of agents playing P
        "S": [] # Number of agents playing S
    }

    for i in range(runtime):
        A = random.choice(agents)
        B = random.choice(agents)

        if A != B:
            p = p_switch(A, B, w, s)
            debug(f"Probability that agent A switches their strategy ({A}) to B's ({B}): {p}")

            if p > random.random():
                agents.remove(A) # Death of agent A's strategy
                agents.append(B) # Replication of agent B's strategy
                debug("Agent A has switched strategies")
            else:
                pass
                debug("Agent A has not switched strategies")
        else:
            # print(f"No switch: both agents are using the same strategy ({A})")
            pass
            
        results["R"].append(agents.count("R"))
        results["P"].append(agents.count("P"))
        results["S"].append(agents.count("S"))

    plt.plot(results["R"], label="R")
    plt.plot(results["P"], label="P")
    plt.xlabel("Time (epochs)")
    plt.ylabel("Number of Agents")
    plt.title(f"Evolution of Rock-Paper-Scissors Strategies Over Time\n(w = {w}, s = {s})")
    plt.legend()
    # plt.ylim(0, N)
    plt.savefig(f"results\\birth-death\\time_series\\w-{w},s-{s}.jpg")
    plt.clf()

    plt.plot(results["R"], results["P"])
    plt.xlabel("Number of Agents Playing R")
    plt.ylabel("Number of Agents Playing P")
    plt.title(f"Phase Plane of Evolution of Rock-Paper-Scissors Strategies\n(w = {w}, s = {s})")
    # plt.xlim(0, N)
    # plt.ylim(0, N)
    plt.savefig(f"results\\birth-death\\phase_plane\\w-{w},s-{s}.jpg")
    plt.clf()