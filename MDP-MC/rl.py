from graphics_util import *
import numpy as np
from grakn.client import GraknClient

tubeimg = "tubes.gif"
wn.addshape(tubeimg)

class Tube(TurtleController):
    def __init__(self):

        tube = turtle.Turtle()
        tube.speed(0)
        tube.shape(tubeimg)
        tube.penup()
        tube.direction = "stop"
        tube.goto(270, randint(-200, 200))

        self.avi = tube

        self.x = self.avi.xcor()
        self.y = self.avi.ycor()


class Environment:
    def __init__(self, tube_v, g, death_reward, score_reward, low_energy_reward):

        self.tube_v = tube_v
        self.g = g

        self.death_reward = death_reward
        self.score_reward = score_reward
        self.low_energy_reward = low_energy_reward

        self.game_state = 1

        self.tubes = []

    def generate_new_tube(self):

        new_tube = Tube()
        self.tubes.append(new_tube)

    def move_tubes(self, agent):
        # Generate tube on RHS
        if agent.t % 25 == 0:
            self.generate_new_tube()

        # tubes cascade to LHS
        for i in range(len(self.tubes)):
            x = self.tubes[i].x
            self.tubes[i].setx(x - self.tube_v)

        for i, tube in enumerate(self.tubes):
            if tube.x < -300:
                del self.tubes[i]


class Agent(TurtleController):
    def __init__(self, jump_speed, jump_cost, stamina, discount_rate ,avi):

        self.jump_speed = jump_speed
        self.jump_cost = jump_cost
        self.stamina = stamina

        self.energy = 100
        self.t = 0
        self.time_since_jump = 0

        self.vertical_speed = 0
        self.avi = avi

        self.refresh_coords()

        self.start_state = {
            "side-of-gap": "START",
            "relative-height": "START",
            "energy-level": "START",
            "absolute-height": "START",
            "time-since-jump": 0,
        }
        self.death_state = {
            "side-of-gap": "DEATH",
            "relative-height": "DEATH",
            "energy-level": "DEATH",
            "absolute-height": "DEATH",
            "time-since-jump": 0,
        }

        self.S = []
        self.A = []
        self.R = []

        self.gamma = discount_rate

        self.A_script = ["JUMP", "FALL"]

        self.state_info = {
            "DEATH-DEATH-DEATH-DEATH-0": {
                "pi": 0,
                "v": 0,
                "count": 0,
                "transitions": {}
            },
            "START-START-START-START-0": {
                # Policy (probabiliity of jumping) at that state
                "pi": 0.5,
                # Value estimate
                "v": 0,
                # Number of times state has been accessed - same as one before
                "count": 0,
                # Counts of transitions - allows live probability movement
                "transitions": {a: {} for a in self.A_script}
            }
        }

        # More generally:
        #self.state_info["W-X-Y-Z-1"] = {
        {
            # Policy (probabiliity of jumping) at that state
            "pi": 0.69,
            # Value estimate
            "v": 123,
            # Number of times state has been accessed - same as one before
            "count": 189,
            # Counts and rewards of transitions - allows live probability movement
            "transitions": {
                "JUMP": { # Notice 1s
                    ("A-B-C-D-1", 2): 69, 
                    ("E-F-G-H-1", 5): 21, 
                    ("DEATH-DEATH-DEATH-DEATH-1", -0.2): 4, 
                },
                "FALL": {
                    ("A-B-C-D-23", -10): 56,
                    ("N-X-C-D-2", -5): 34,
                    ("E-E-H-O-3", 2): 5
                }
            }
        }


    def check_rewards(self, env):
        reward = 0
        env.game_state, reward = self.check_for_death(env, reward)
        self.player_score, reward = self.check_for_new_score(
            env, self.player_score, reward
        )
        reward = self.check_for_low_energy(env, reward)
        return reward

    def apply_policy(self, state):

        state_string = "-".join(str(x) for x in state.values())
        state_info = self.state_info.get(state_string)

        # Initialise state 
        if state_info == None:
            state_info = {
                # Policy (probabiliity of jumping) at that state
                "pi": 0.5,
                # Value estimate
                "v": 0,
                # Number of times state has been accessed - same as one before
                "count": 0,
                # Counts of transitions - allows live probability movement
                "transitions": {a: {} for a in self.A_script}
            }

            self.state_info[state_string] = state_info

        pi = state_info["pi"]

        if random() < pi:
            self.jump()
            return "JUMP"
        return "FALL"

    def jump(self):
        if self.energy >= self.jump_cost:
            self.avi.direction = "up"
            self.vertical_speed = self.jump_speed
            self.energy -= self.jump_cost
            self.time_since_jump = 0

    def regain_energy(self):
        if self.energy < 100:
            self.energy += self.stamina

    def check_for_new_score(self, env, player_score, reward):

        for i in range(len(env.tubes)):
            if abs(env.tubes[i].x - self.x) < 6 and abs(env.tubes[i].y - self.y) < 78:
                player_score += 1
                reward += env.score_reward

        return player_score, reward

    def check_for_death(self, env, reward):

        game_state = 1

        for i in range(len(env.tubes)):
            if abs(env.tubes[i].x - self.x) < 10 and abs(env.tubes[i].y - self.y) > 78:
                game_state = 0
                reward += env.death_reward

        if self.y < -300 or self.y > 310:
            game_state = 0
            reward += env.death_reward

        return game_state, reward

    def check_for_low_energy(self, env, reward):
        
        if self.energy <= 1.5 * self.jump_cost:
            reward += env.low_energy_reward
        
        return reward

    def implement_gravity(self, env):
        self.vertical_speed += 0.05 * env.g
        self.sety(self.y + self.vertical_speed)

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


    def update_state_info(self, s_t, s_prev, a_t, r_t):

        s_t = "-".join(str(x) for x in s_t.values())
        s_prev = "-".join(str(x) for x in s_prev.values())

        self.state_info[s_prev]["count"] += 1
        try:
            self.state_info[s_prev]["transitions"][a_t][(s_t, r_t)] += 1


        except KeyError:
            self.state_info[s_prev]["transitions"][a_t][(s_t, r_t)] = 1



    def bellman_update(self, state):
        """
        Change v(s) as per update to Bellman's equation:
        v(s) <-- Sum_a[pi(a|s)*SUM_sbar,r*p[(sbar,r|s,a)*(r+gamma*v(sbar))]]
        """

        new_v_s = 0
        state_dict = self.state_info[state]

        old_vs = state_dict["v"]

        # GENERALISE THIS AND pi OVERALL
        # fall cases:
        for sbar_and_r, t_count in state_dict["transitions"]["JUMP"].items():
            
            prob = t_count/state_dict["count"]
            v_sbar = self.state_info[sbar_and_r[0]]["v"]
            addition = state_dict["pi"] * prob * (sbar_and_r[1] + self.gamma*v_sbar)
            new_v_s += addition

        for sbar_and_r, t_count in state_dict["transitions"]["FALL"].items():
            
            prob = t_count/state_dict["count"]
            v_sbar = self.state_info[sbar_and_r[0]]["v"]
            addition = (1 - state_dict["pi"]) * prob * (sbar_and_r[1] + self.gamma*v_sbar)
            new_v_s += addition
        

        self.state_info[state]["v"] = new_v_s


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


    def q_greedify_policy(self, state):

        state_dict = self.state_info[state]

        action_returns = [0 for a in self.A_script]

        for i, a in enumerate(self.A_script):

            for sbar_and_r, t_count in state_dict["transitions"][a].items():

                prob = t_count/state_dict["count"]
                v_sbar = self.state_info[sbar_and_r[0]]["v"]
                addition = prob * (sbar_and_r[1] + self.gamma*v_sbar)

                action_returns[i] += addition
            
        greedy_choice = np.argmax(action_returns)
        greedy_probability = 1 / len([a for a in range(len(self.A_script)) if a == greedy_choice])

        # GENERALISE THIS
        if self.A_script[greedy_choice] == "JUMP":
            self.state_info[state]["pi"] = greedy_probability
        elif self.A_script[greedy_choice] == "FALL":
            self.state_info[state]["pi"] = 1-greedy_probability
        else:
            raise ValueError("wtf")


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


    def upload(self):
        
        with GraknClient(uri="localhost:48555") as client:
            with client.session(keyspace="clappy_bird") as session:

                for state, state_dict in self.state_info.items():
                    with session.transaction().write() as transaction:
                        state_insert_query = f"""
                            insert $s isa state, has state_string "{state}",
                            has pi {np.format_float_positional(state_dict['pi'])},
                            has v {np.format_float_positional(state_dict['v'])},
                            has total_count {state_dict['count']};
                        """
                        transaction.query(state_insert_query)
                        transaction.commit()
                
                for state, state_dict in self.state_info.items():

                    for action, transition_info in state_dict["transitions"].items():

                        for sbar_and_r, count in transition_info.items():

                            with session.transaction().write() as transaction:
                                transition_insert_query = f"""
                                    match
                                        $start_state isa state, has state_string "{state}";
                                        $end_state isa state, has state_string "{sbar_and_r[0]}";
                                    insert $new_state_transition (start_state: $start_state, end_state: $end_state) isa state_transition;
                                        $new_state_transition has reward {sbar_and_r[1]}, has action "{action}", has num_occurances {count};
                                """
                                transaction.query(transition_insert_query)
                                transaction.commit()                                