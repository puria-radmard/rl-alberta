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


class Agent:

    def __init__(self, jump_speed, bird):

        self.jump_speed = jump_speed

        self.vertical_speed = 0
        self.bird = bird

        self.refresh_coords

    def refresh_coords(self):
        self.x = self.bird.xcor()
        self.y = self.bird.ycor()

    def goto(self, x, y):
        
        self.bird.goto(0,0)
        self.x = x
        self.y = y

    def sety(self, new_y):
        self.refresh_coords()

        self.bird.sety(
            new_y
        )
        self.y = new_y

    def setx(self, new_x):

        self.refresh_coords()

        self.bird.setx(
            new_x
        )
        self.x = new_x

    def jump(self):
        self.bird.direction = "up"
        self.vertical_speed = self.jump_speed

    def check_for_new_score(self, env, score):

        if len(env.tubes) < 3:
            for i in range(len(env.tubes)):
                if abs(env.tubes[i].x-self.x) < 6 and abs(env.tubes[i].y - self.y) < 78:
                    score += 1
  
        else:
            for i in range(-1, -4, -1):
                if abs(env.tubes[i].x-self.x) < 6 and abs(env.tubes[i].y - self.y) < 78:
                    score += 1

        return score


    def check_for_death(self, env):

        game_state = 1

        if len(env.tubes) < 3:
            for i in range(len(env.tubes)):
                if abs(env.tubes[i].x-self.x) < 6 and abs(env.tubes[i].y - self.y) > 78:
                    game_state = 0   
        else:
            for i in range(-1, -4, -1):
                if abs(env.tubes[i].x-self.x) < 6 and abs(env.tubes[i].y - self.y) > 78:
                    game_state = 0

        if self.y < -300 or self.y > 310:
            game_state = 0  

        return game_state

    def implement_gravity(self, env):
        self.vertical_speed += 0.05*env.g
        #y = self.bird.ycor()
        self.sety(
            self.y + self.vertical_speed
        )


class Tube:

    def __init__(self):

        tube = turtle.Turtle()
        tube.speed(0)
        tube.shape(tubeimg)
        tube.penup()
        tube.direction="stop" 
        tube.goto(270, randint(-200, 200))

        self.avi = tube

        self.x = self.avi.xcor()
        self.y = self.avi.ycor()

    def refresh_coords(self):
        self.x = self.avi.xcor()
        self.y = self.avi.ycor()

    def goto(self, x, y):
        
        self.avi.goto(x, y)
        self.x = x
        self.y = y

    def sety(self, new_y):

        self.refresh_coords()

        self.avi.sety(
            new_y
        )
        self.y = new_y

    def setx(self, new_x):

        self.refresh_coords()

        self.avi.setx(
            new_x
        )
        self.x = new_x