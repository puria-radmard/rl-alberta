import turtle
from random import randint, random
from time import sleep

player_score = 0
highscore = 0

# scoreboard
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, -260)
pen.write(
    "Score: {}    High Score: {}".format(player_score, highscore),
    align="center",
    font=("Comic Sans", 12, "bold"),
)


# Set up screen
wn = turtle.Screen()
wn.title("Clappy Bird by Puria Radmard")
wn.bgcolor("deep sky blue")
wn.setup(width=500, height=600)
wn.tracer(0)

# Bird
bird = turtle.Turtle()
bird.speed(0)
bird.shape("triangle")
bird.color("yellow")
bird.penup()
bird.goto(-100, 0)
bird.direction = "stop"

# intro screen
title = turtle.Turtle()
title.speed(0)
title.shape("square")
title.color("white")
title.penup()
title.hideturtle()
title.goto(0, 260)
title.write("Clappy Bird", align="center", font=("Comic Sans", 24, "bold"))

subtitle = turtle.Turtle()
subtitle.speed(0)
subtitle.shape("square")
subtitle.color("white")
subtitle.penup()
subtitle.hideturtle()
subtitle.goto(0, 230)
subtitle.write("press space to start", align="center", font=("Comic Sans", 16, "bold"))


energy_pen = turtle.Turtle()
energy_pen.speed(0)
energy_pen.shape("square")
energy_pen.color("white")
energy_pen.penup()
energy_pen.hideturtle()
energy_pen.goto(0, 260)
# energy_pen.write(f"E: {int(agent.energy)}", align = "top left", font=("Comic Sans", 12,"bold"))


state_pen = turtle.Turtle()
state_pen.speed(0)
state_pen.shape("square")
state_pen.color("red")
state_pen.penup()
state_pen.hideturtle()
state_pen.goto(-100, -260)


def update_pens(agent, state_pen, pen, energy_pen, player_score):

    state_pen.clear()
    state_string = ""
    for k, v in agent.state.items():
        state_string += f"{k}: {v} \n"
    state_pen.write(state_string, align="left", font=("Comic Sans", 20, "bold"))

    if agent.energy > 80:
        energy_color = "green"
    elif agent.energy > 30:
        energy_color = "yellow"
    else:
        energy_color = "red"

    # update player_score
    pen.clear()
    pen.write(
        f"Score: {player_score}    High Score: {highscore}",
        align="center",
        font=("Comic Sans", 12, "bold"),
    )

    energy_pen.clear()
    energy_pen.color(energy_color)
    energy_pen.write(
        f"E: {int(agent.energy)}", align="left", font=("Comic Sans", 20, "bold")
    )


def init_pens(pen, title, subtitle, player_score, highscore):
    pen.clear()
    pen.write(
        "Score: {}    High Score: {}".format(player_score, highscore),
        align="center",
        font=("Comic Sans", 12, "bold"),
    )
    title.write("Clappy Bird", align="center", font=("Comic Sans", 24, "bold"))
    subtitle.write(
        "press space to start", align="center", font=("Comic Sans", 16, "bold")
    )


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
