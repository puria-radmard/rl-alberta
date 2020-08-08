import turtle
from random import randint
from time import sleep

#Set up screen
wn = turtle.Screen()
wn.title("Clappy Bird by Puria Radmard")
wn.bgcolor("deep sky blue")
wn.setup(width=600, height=600)
wn.tracer(0)

#definitions
score = 0
highscore = 0
tubeimg = "tubes.gif"
wn.addshape(tubeimg)
tubes = []
g = -50
v = 0

#Bird
bird = turtle.Turtle()
bird.speed(0)
bird.shape("triangle")
bird.color("yellow")
bird.penup()
bird.goto(-100,0)
bird.direction="stop"

#scoreboard
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0,-260)
pen.write("Score: {}    High Score: {}".format(score, highscore), align = "center", font=("Comic Sans", 24,"bold"))

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

#define jumps
def jump():
    bird.direction = "up"
    global v
    v = 30         
wn.listen()
wn.onkeypress(jump, "space")

#Game loop including start screen and death
while True:
    
    #Set up game
    game_state = 1
    tubes = []
    score = 0    
    pen.clear()
    pen.write("Score: {}    High Score: {}".format(score, highscore), align = "center", font=("Comic Sans", 24,"bold")) 
    title.write("Clappy Bird", align = "center", font=("Comic Sans", 24,"bold"))
    subtitle.write("press space to start", align = "center", font=("Comic Sans", 16,"bold"))
    
    #Start screen
    while True:
        wn.update()
        bird.goto(-100,0)        
        if bird.direction == "up":
            title.clear()
            subtitle.clear()
            break
        else:
            pass
    
    #Main game loop
    n = 0
    while True:
        wn.update()        
        
        #Implement gravity
        v += 0.05*g
        y = bird.ycor()
        bird.sety(y + v)
        
        #Generate tube on RHS
        if n%30 == 0:
            tube = turtle.Turtle()
            tube.speed(0)
            tube.shape(tubeimg)
            tube.penup()
            tube.direction="stop" 
            tube.goto(310, randint(-200, 200))
            tubes.append(tube)
        
        #tubes cascade to LHS
        for i in range(len(tubes)-1):
            x = tubes[i].xcor()
            tubes[i].setx(x - 10)
        
        #set collisions and scoring
        if len(tubes) < 3:
            for i in range(len(tubes) - 1):
                if abs(tubes[i].xcor()-bird.xcor()) < 6 and abs(tubes[i].ycor() - bird.ycor()) < 78:
                    score += 1
                elif abs(tubes[i].xcor()-bird.xcor()) < 6 and abs(tubes[i].ycor() - bird.ycor()) > 78:
                    game_state = 0            
        else:
            for i in range(-1, -4, -1):
                if abs(tubes[i].xcor()-bird.xcor()) < 6 and abs(tubes[i].ycor() - bird.ycor()) < 78:
                    score += 1
                elif abs(tubes[i].xcor()-bird.xcor()) < 6 and abs(tubes[i].ycor() - bird.ycor()) > 78:
                    game_state = 0   
        if bird.ycor() < -300:
            game_state = 0   
        if score > highscore:
            highscore = score
        
        #update score
        pen.clear()
        pen.write("Score: {}    High Score: {}".format(score, highscore), align = "center", font=("Comic Sans", 24,"bold"))
        sleep(0.05)
        n += 1
        if game_state == 0:
            break
        else:
            pass
    
    #death    
    for tube in tubes:
        tube.goto(1000,1000)
    bird.direction = "stop"       

#finalise  
wn.mainloop()
turtle.done()