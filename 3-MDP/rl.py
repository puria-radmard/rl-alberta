from avatars import *

tubeimg = "tubes.gif"
wn.addshape(tubeimg)


class Environment:
    def __init__(self, tube_v, g):

        self.tube_v = tube_v
        self.g = g

        self.tubes = []

    def generate_new_tube(self):

        new_tube = Tube()
        self.tubes.append(new_tube)


class TurtleController:
    def __init__(self,):

        pass

    def refresh_coords(self):
        self.x = self.avi.xcor()
        self.y = self.avi.ycor()

    def goto(self, x, y):

        self.avi.goto(x, y)
        self.x = x
        self.y = y

    def sety(self, new_y):

        self.refresh_coords()

        self.avi.sety(new_y)
        self.y = new_y

    def setx(self, new_x):

        self.refresh_coords()

        self.avi.setx(new_x)
        self.x = new_x


class Agent(TurtleController):
    def __init__(self, jump_speed, jump_cost, stamina, avi):

        self.jump_speed = jump_speed
        self.jump_cost = jump_cost
        self.stamina = stamina

        self.energy = 100
        self.t = 0
        self.time_since_jump = 0

        self.vertical_speed = 0
        self.avi = avi

        self.refresh_coords()

    def jump(self):
        if self.energy >= self.jump_cost:
            self.avi.direction = "up"
            self.vertical_speed = self.jump_speed
            self.energy -= self.jump_cost
            self.time_since_jump = 0

    def regain_energy(self):
        if self.energy < 100:
            self.energy += self.stamina

    def check_for_new_score(self, env, score):

        if len(env.tubes) < 3:
            for i in range(len(env.tubes)):
                if (
                    abs(env.tubes[i].x - self.x) < 6
                    and abs(env.tubes[i].y - self.y) < 78
                ):
                    score += 1

        else:
            for i in range(-1, -4, -1):
                if (
                    abs(env.tubes[i].x - self.x) < 6
                    and abs(env.tubes[i].y - self.y) < 78
                ):
                    score += 1

        return score

    def check_for_death(self, env):

        game_state = 1

        if len(env.tubes) < 3:
            for i in range(len(env.tubes)):
                if (
                    abs(env.tubes[i].x - self.x) < 10
                    and abs(env.tubes[i].y - self.y) > 78
                ):
                    game_state = 0
        else:
            for i in range(-1, -4, -1):
                if (
                    abs(env.tubes[i].x - self.x) < 10
                    and abs(env.tubes[i].y - self.y) > 78
                ):
                    game_state = 0

        if self.y < -300 or self.y > 310:
            game_state = 0

        return game_state

    def implement_gravity(self, env):
        self.vertical_speed += 0.05 * env.g
        self.sety(self.y + self.vertical_speed)

    def find_state(self, env):

        state_dict = {}

        # side-of-gap
        tube_coords = sorted([(t.x, t.y) for t in env.tubes], key = lambda x: abs(x[0]))
        try:
            closest_tubes = sorted([tube_coords[0], tube_coords[1]], key=lambda x: x[0])
            proportion_of_way = closest_tubes[0][0] / (closest_tubes[0][0] - closest_tubes[1][0])
            state_dict["side-of-gap"] = "LEFT" if proportion_of_way < 0.5 else "RIGHT"
        except IndexError:
            state_dict["side-of-gap"] = "LEFT"

        try:
            tube_height = closest_tubes[1][1]
            if tube_height - self.y > 78:
                state_dict["relative-height"] = "LOW"
            elif 0 < tube_height - self.y <= 78:
                state_dict["relative-height"] = "MIDLOW"
            elif 0 > tube_height - self.y >= -78:
                state_dict["relative-height"] = "MIDHIGH"
            else:
                state_dict["relative-height"] = "HIGH"

        except NameError:
            # BAD - make this a single tube search instead
            state_dict["relative-height"] = "MIDHIGH"

        if self.energy > 100 - 1.5*self.jump_cost:
            state_dict["energy-level"] = "HIGH"
        elif self.energy > 1.5*self.jump_cost:
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
