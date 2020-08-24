from graphics_util import *
import numpy as np
# from grakn.client import GraknClient

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
    def __init__(self, tube_v, tube_gen_rate, g, death_reward, score_reward, low_energy_reward):

        self.tube_v = tube_v
        self.g = g

        self.death_reward = death_reward
        self.score_reward = score_reward
        self.low_energy_reward = low_energy_reward
        self.tube_gen_rate = tube_gen_rate

        self.tube_gap = tube_gen_rate * tube_v

        self.game_state = 1

        self.tubes = []

    def generate_new_tube(self):

        new_tube = Tube()
        self.tubes.append(new_tube)

    def move_tubes(self, agent):
        # Generate tube on RHS
        if agent.t % self.tube_gen_rate == 0:
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
        self.epsilon = 0.2

        self.A_script = ["JUMP", "FALL"]
        self.pi_init = [0.05, 0.95]

        self.state_info = {
            "DEATH-DEATH-DEATH-DEATH-0": {
                "pi": {a: 1/len(self.A_script) for a in self.A_script},
                "v": 0,
                "count": 0,
                "transitions": {}
            },
            "START-START-START-START-0": {
                # Policy (probabiliity of jumping) at that state
                "pi": {a: 1/len(self.A_script) for a in self.A_script},
                "q" : {a: 0 for a in self.A_script},
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
            "pi": {a: 1/len(self.A_script) for a in self.A_script},
            # Value estimate
            "v": 123,
            # Action value estimate
            "q": {
                "JUMP": 94,
                "FALL": 95
            },
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
                "pi": {self.A_script[i]: self.pi_init[i] for i in range(len(self.A_script))},
                # Action value estimate
                "q" : {a: 0 for a in self.A_script},
                # State value estimate
                "v": 0,
                # Number of times state has been accessed - same as one before
                "count": 0,
                # Counts of transitions - allows live probability movement
                "transitions": {a: {} for a in self.A_script}
            }
            self.state_info[state_string] = state_info
        pi = state_info["pi"]

        # GENERALISE THIS
        if random() < pi["JUMP"]:
            self.jump()
            return "JUMP"
        return "FALL"


    def find_state(self, env):

        state_dict = {}

        tube_coords = sorted([(t.x, t.y) for t in env.tubes], key=lambda x: abs(x[0]))
        try:
            closest_tubes = sorted([tube_coords[0], tube_coords[1]], key=lambda x: x[0])
            proportion_of_way = closest_tubes[0][0] / (
                closest_tubes[0][0] - closest_tubes[1][0]
            )
            prop = round(proportion_of_way, 3)
        except IndexError:
            closest_tubes = [None, tube_coords[0]]
            proportion_of_way = (env.tube_gap - closest_tubes[1][0]) / env.tube_gap
            prop = round(proportion_of_way, 3)
        if prop < 0:
            state_dict["prop"] = 0
        elif prop > 1:
            state_dict["prop"] = 1
        else:
            state_dict["prop"] = prop

        state_dict["vel"] = self.vertical_speed
        state_dict["height"] = self.y
        state_dict["rel-height"] = closest_tubes[1][1] - self.y
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
        Unused
        Change bootstrapped v(s) as per update to Bellman's equation:
        v(s) <-- Sum_a[pi(a|s)*SUM_sbar,r*p[(sbar,r|s,a)*(r+gamma*v(sbar))]]
        """

        new_v_s = 0
        state_dict = self.state_info[state]

        old_vs = state_dict["v"]

        # fall cases:
        for a in self.A_script:

            action_count = sum(list(state_dict["transitions"][a].values()))

            for sbar_and_r, t_count in state_dict["transitions"][a].items():

                prob = t_count/action_count
                v_sbar = self.state_info[sbar_and_r[0]]["v"]
                addition = state_dict["pi"][a] * prob * (sbar_and_r[1] + self.gamma*v_sbar)
                new_v_s += addition        

        self.state_info[state]["v"] = new_v_s

    def monte_carlo_q_update(self):
        for t in list(range(len(self.A)))[::-1]:
            try:
                latest_episode_Gs = [self.R[t] + latest_episode_Gs[0] * self.gamma] + latest_episode_Gs
            except NameError:
                latest_episode_Gs = [self.R[-1]]
        
        for j, s in enumerate(self.S):
            a = self.A[j]
            state_string = "-".join(str(x) for x in s.values())
            action_count = max([sum(self.state_info[state_string]["transitions"][a].values()), 1])

            current_q = self.state_info[state_string]["q"][a]
            new_G = latest_episode_Gs[j]
            self.state_info[state_string]["q"][a] = current_q + (1/action_count)*(new_G - current_q)

        self.S = []
        self.A = []
        self.R = []


    def q_greedify_policy(self, state):

        state_dict = self.state_info[state]

        action_returns = [0 for a in self.A_script]

        if False:
            # Greedify based on bootstrapped s/a combinations
            for i, a in enumerate(self.A_script):
                action_count = sum(list(state_dict["transitions"][a].values()))
                for sbar_and_r, t_count in state_dict["transitions"][a].items():
                    prob = t_count/action_count
                    v_sbar = self.state_info[sbar_and_r[0]]["v"]
                    addition = prob * (sbar_and_r[1] + self.gamma*v_sbar)
                    action_returns[i] += addition

        # Greedify based on Monte Carlo action values - by itself this would be enough with exploring starts
        for i, a in enumerate(self.A_script):
            action_returns[i] = state_dict["q"][a]

        # TODO: make greedy choices split probability?
            
        greedy_choice = np.argmax(action_returns)
        greedy_probability = 1 - self.epsilon + (self.epsilon/len(self.A_script))
        exploratorive_probability = self.epsilon / len(self.A_script)

        for i, a in enumerate(self.A_script):
            if i == greedy_choice:
                self.state_info[state]["pi"][a] = greedy_probability
            else:
                self.state_info[state]["pi"][a] = exploratorive_probability
        
        try:
            assert sum(self.state_info[state]["pi"].values()) == 1
        except:
            import pdb; pdb.set_trace()

    def post_process(self):

        self.monte_carlo_q_update()

        non_death_states = [state for state in self.state_info.keys() if "DEATH" not in state]
        for state in non_death_states:
            self.q_greedify_policy(state)


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