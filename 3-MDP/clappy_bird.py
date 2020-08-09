from avatars import *

from rl import Environment, Agent

env = Environment(
    tube_v = 10,
    g = -50
)

agent = Agent(
    jump_speed = 30,
    bird=bird
)

wn.listen()
wn.onkeypress(agent.jump, "space")

#Game loop including start screen and death
while True:
    
    #Set up game
    game_state = 1
    score = 0    
    pen.clear()
    pen.write("Score: {}    High Score: {}".format(score, highscore), align = "center", font=("Comic Sans", 12,"bold")) 
    title.write("Clappy Bird", align = "center", font=("Comic Sans", 24,"bold"))
    subtitle.write("press space to start", align = "center", font=("Comic Sans", 16,"bold"))
    
    #Start screen
    while True:
        wn.update()
        agent.goto(-3050,0)        
        if agent.bird.direction == "up":
            title.clear()
            subtitle.clear()
            break
        else:
            pass

    #Main game loop
    n = 0
    while True:
        wn.update()        
        
        # agent.

        #Implement gravity
        agent.implement_gravity(env)
        game_state = agent.check_for_death(env)
        score = agent.check_for_new_score(env, score)

        #Generate tube on RHS
        if n%25 == 0:
            env.generate_new_tube()

        #tubes cascade to LHS
        for i in range(len(env.tubes)):
            x = env.tubes[i].x
            env.tubes[i].setx(x - env.tube_v)

        if score > highscore:
            highscore = score

        #update score
        pen.clear()
        pen.write("Score: {}    High Score: {}".format(score, highscore), align = "center", font=("Comic Sans", 12,"bold"))
        sleep(0.05)
        n += 1
        if game_state == 0:
            break
        else:
            pass

        for i, tube in enumerate(env.tubes):
            if tube.x < -300:
                del env.tubes[i]
        
        print(len(env.tubes))

        agent.refresh_coords()
    
    #death    
    for tube in env.tubes:
        tube.goto(-1000,-1000)
        del tube
    bird.direction = "stop"       

#finalise  
wn.mainloop()
turtle.done()

if __name__ == "__main__":
    main()