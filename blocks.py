"""
The building blocks of RL: the Bandit, the Agent, and a group of Agents (for running sweeps on the same set of Bandits)
"""

import numpy as np
from numpy.random import normal
import random
import matplotlib.pyplot as plt
from typing import List
from math import sqrt, log

class Bandit:
    """
    A single bandit
    """

    def __init__(self, q_true, reward_uncertainty, variation_step):

        self.q_true = q_true
        self.reward_uncertainty = reward_uncertainty
        self.variation_step = variation_step

        self.Q = None

    def __repr__(self):
        try:
            return f"Bandit: true q* {self.q_true}, variation {self.reward_uncertainty}. {self.group_idx} in group"

        except AttributeError:
            return (
                f"Bandit: true q* {self.q_true}, variation {self.reward_uncertainty}."
            )

    def return_value(self):

        self.latest_reward = normal(self.q_true, self.reward_uncertainty)
        self.change_mean()
        return self.latest_reward

    def change_mean(self):
        change_in_mean = normal(0, self.variation_step)
        self.q_true += change_in_mean
        


class Agent:
    def __init__(self, bandits, eps, alpha, step_method, Q0, c):

        # {Bandit: (Q,n)}
        self.bandits = {
            b: {"Q": Q0, "n": np.finfo(float).eps} for b in bandits  # for UCB initial
        }

        self.eps = eps
        self.t = 1
        self.average_score = 0
        self.optimal_choice_prop = 0
        self.alpha = alpha
        self.c = c

        if step_method in ["incremental", "constant"]:
            self.step_method = step_method
        else:
            raise ValueError(f"Step method {step_method} not recognised.")

    def update_Q(self, chosen_bandit):

        self.bandits[chosen_bandit]["n"] += 1

        n = self.bandits[chosen_bandit]["n"]
        Q = self.bandits[chosen_bandit]["Q"]

        if self.step_method == "incremental":
            self.bandits[chosen_bandit]["Q"] += (1 / n) * (
                chosen_bandit.latest_reward - Q
            )
        elif self.step_method == "constant":
            self.bandits[chosen_bandit]["Q"] += self.alpha * (
                chosen_bandit.latest_reward - Q
            )

    def make_choice(self, true_values):

        UCBlambda = lambda stats: stats["Q"] + self.c * sqrt(log(self.t) / stats["n"])

        # Get a bandit with highest Q (randomised from tie)
        top_Q = max(self.bandits.values(), key=UCBlambda)["Q"]
        greedy_choices = [
            bandit
            for bandit in list(self.bandits.keys())
            if self.bandits[bandit]["Q"] == top_Q
        ]
        greedy_choice = random.choice(greedy_choices)

        strat = "exploit" if random.random() > self.eps else "explore"
        if strat == "exploit":
            chosen_bandit = greedy_choice

        elif strat == "explore":
            chosen_bandit = random.choice(list(self.bandits.keys()))

        optimal_choice = np.amax(true_values)
        optimal_choice_bool = int(chosen_bandit.latest_reward == optimal_choice)
        assert optimal_choice_bool in [1, 0]

        self.update_Q(chosen_bandit)

        self.update_stats(chosen_bandit.latest_reward, optimal_choice_bool)

    def update_stats(self, latest_reward, optimal_choice):

        self.t += 1
        self.average_score += (1 / self.t) * (latest_reward - self.average_score)
        self.optimal_choice_prop += (1 / self.t) * (
            optimal_choice - self.optimal_choice_prop
        )

    def forward_run(self):
        """
        Gets new random values independently, so this wrapper only used for single Agent problems

        Seperating this from make_choices method to allow better support for GroupOfAgents.
        This is only called for a single agent problem
        """
        true_values = [bandit.return_value() for bandit in self.bandits]

        self.make_choice(true_values)
        return {
            "t": self.t,
            "average_score": self.average_score,
            "optimal_choice_prop": self.optimal_choice_prop,
        }


class GroupOfAgents:
    def __init__(
        self,
        k: float,
        epses: List[float],
        step_methods: List[str],
        q_var,
        q_mean,
        reward_uncertainty,
        alphas,
        Q0s,
        cs,
        variation_step,
    ):

        try:
            assert len(epses) == len(step_methods)
        except:
            ValueError("Mismatching number of parameters")

        self.num_agents = len(epses)
        self.k = k

        params = [
            {
                "eps": epses[i],
                "step_method": step_methods[i],
                "alpha": alphas[i],
                "Q0": Q0s[i],
                "c": cs[i],
            }
            for i in range(self.num_agents)
        ]

        self.bandits = [
            Bandit(
                q_true=normal(q_mean, q_var),
                reward_uncertainty=reward_uncertainty,
                variation_step=variation_step,
            )
            for a in range(k)
        ]

        self.agents = [Agent(self.bandits, **p) for p in params]

        for i, bandit in enumerate(self.bandits):
            bandit.group_idx = i

    def forward_run(self):
        true_values = [bandit.return_value() for bandit in self.bandits]

        [agent.make_choice(true_values) for agent in self.agents]
        return [
            {
                "t": agent.t,
                "average_score": agent.average_score,
                "optimal_choice_prop": agent.optimal_choice_prop,
            }
            for agent in self.agents
        ]
