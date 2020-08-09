import turtle
from random import randint
from time import sleep

#definitions
score = 0
highscore = 0

#scoreboard
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0,-260)
pen.write("Score: {}    High Score: {}".format(score, highscore), align = "center", font=("Comic Sans", 12,"bold"))


#Set up screen
wn = turtle.Screen()
wn.title("Clappy Bird by Puria Radmard")
wn.bgcolor("deep sky blue")
wn.setup(width=500, height=600)
wn.tracer(0)

#Bird
bird = turtle.Turtle()
bird.speed(0)
bird.shape("triangle")
bird.color("yellow")
bird.penup()
bird.goto(-100,0)
bird.direction="stop"

#intro screen
title = turtle.Turtle()
title.speed(0)
title.shape("square")
title.color("white")
title.penup()
title.hideturtle()
title.goto(0,260)
title.write("Clappy Bird", align = "center", font=("Comic Sans", 24,"bold"))

subtitle = turtle.Turtle()
subtitle.speed(0)
subtitle.shape("square")
subtitle.color("white")
subtitle.penup()
subtitle.hideturtle()
subtitle.goto(0,230)
subtitle.write("press space to start", align = "center", font=("Comic Sans", 16,"bold"))