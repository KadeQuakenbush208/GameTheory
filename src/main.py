import random

def p_switch(A, B, w, pi):
    # p = 1/2 + w * (pi[A] - pi[B]) / (2 * (
    pass

def get_payoff(A, B, s: float):
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

strats = ["R", "P", "S"]
N = 10
s_vals = [0.7]

agents = []
for i in range(N): agents.append(strats[i % 3])

print(get_payoff("R", "P"))