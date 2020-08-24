from rl import *

class ExtendedAgent(Agent):

    def __init__():
        super().__init__()

    def evaluate_policy(self):
        """Unused"""
        delta = float('inf')
        theta = 0.0001
        while delta > theta:
            delta = 0
            non_death_states = [state for state in self.state_info.keys() if "DEATH" not in state]
            for state in non_death_states:
                v = self.state_info[state]["v"]
                self.bellman_update(state)
                delta = max([delta, abs(v - self.state_info[state]["v"])])
    
    def iterate_policy(self):
        """Unused"""
        pi_stable = False
        while not pi_stable:
            pi_stable = True
            for state in self.state_info:
                pi_old = [s["pi"] for s in self.state_info]
                self.q_greedify_policy(state)
                pi_new = [s["pi"] for s in self.state_info]
                if not np.array_equal(pi_old, pi_new):
                    pi_stable = False

    def post_process(self):
        delta = float('inf')
        theta = 0.0001
        while delta > theta:
            delta = 0
            # GENERALISE
            non_death_states = [state for state in self.state_info.keys() if "DEATH" not in state]
            for state in non_death_states:
                v = self.state_info[state]["v"]
                self.q_greedify_policy(state)
                self.bellman_update(state)
                delta = max([delta, abs(v - self.state_info[state]["v"])])

    def find_state(self, env):

        state_dict = {}

        # side-of-gap
        tube_coords = sorted([(t.x, t.y) for t in env.tubes], key=lambda x: abs(x[0]))
        try:
            closest_tubes = sorted([tube_coords[0], tube_coords[1]], key=lambda x: x[0])
            proportion_of_way = closest_tubes[0][0] / (
                closest_tubes[0][0] - closest_tubes[1][0]
            )
            state_dict["side-of-gap"] = "LEFT" if proportion_of_way < 0.5 else "RIGHT"
        except IndexError:
            closest_tubes = [None, tube_coords[0]]
            state_dict["side-of-gap"] = "LEFT"

        tube_height = closest_tubes[1][1]
        if tube_height - self.y > 78:
            state_dict["relative-height"] = "LOW"
        elif 0 < tube_height - self.y <= 78:
            state_dict["relative-height"] = "MIDLOW"
        elif 0 > tube_height - self.y >= -78:
            state_dict["relative-height"] = "MIDHIGH"
        else:
            state_dict["relative-height"] = "HIGH"

        # except NameError:
        #     # BAD - make this a single tube search instead
        #     state_dict["relative-height"] = "MIDHIGH"

        if self.energy > 100 - 1.5 * self.jump_cost:
            state_dict["energy-level"] = "HIGH"
        elif self.energy > 1.5 * self.jump_cost:
            state_dict["energy-level"] = "MID"
        else:
            state_dict["energy-level"] = "LOW"

        if self.y > 260:
            state_dict["absolute-height"] = "HIGH"
        elif self.y < -260:
            state_dict["absolute-height"] = "LOW"
        else:
            state_dict["absolute-height"] = "MID"

        state_dict["time-since-jump"] = self.time_since_jump

        return state_dict