from graphics_util import *
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

        self.state = {
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

        # PROBABILITY OF JUMPING AT ANY POINT
        # As we only have two actions (jump or don't jump) - we only need one variable per state to make
        # pi(a|s) a distribtuion - it is a probability of jumping given the state
        self.state_pis = {}

        # These are the list of returns per state, which are found retroactively in post_process
        self.state_Gs = {}
        # These are the list of returns per state-action pair
        self.state_action_Gs = {}
        # These are the counts of times that state-action pairs lead to another state via a reward
        self.four_var_counts = {}

    def read_environment(self, env):
        reward = 0
        env.game_state, reward = self.check_for_death(env, reward)
        self.player_score, reward = self.check_for_new_score(
            env, self.player_score, reward
        )
        reward = self.check_for_low_energy(env, reward)
        return reward

    def apply_policy(self):

        state_string = "-".join(str(x) for x in self.state.values())
        pi = self.state_pis.get(state_string)

        # Quick fix? Not sure
        if pi == None:
            pi = 0.5
            self.state_pis["state_string"] = pi

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


    def post_process(self):

        state_strings = ["-".join(str(x) for x in s.values()) for s in self.S] # One extra one left over from death
        state_action_strings = ["-".join([state_strings[i], self.A[i]]) for i in range(len(self.S) - 1)]

        # Make this a solid attribute later
        # with GraknClient(uri="localhost:48555") as client:
        #     with client.session(keyspace="clappy_bird") as session:

        for asdf in ".":
        
                for j in range(len(self.S) - 1):

                    # First let's find the expected returns | S at each state passed in this round:

                    G = 0
                    future_states = state_strings[j:]
                    future_rewards = self.R[j:]
                    for i in range(len(future_rewards)):
                        G += future_rewards[i] * (self.gamma ** i)

                    try:
                        self.state_Gs[state_strings[j]].append(G)
                        self.state_action_Gs[state_action_strings[j]].append(G)
                    except KeyError:
                        self.state_Gs[state_strings[j]] = [G]
                        self.state_action_Gs[state_action_strings[j]] = [G]

                    # Then let's do the same for state-action pairs 

        self.S = []
        self.A = []
        self.R = []