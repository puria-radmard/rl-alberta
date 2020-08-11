from avatars import *
from rl import Environment, Agent

env = Environment(tube_v=10, g=-50)

agent = Agent(jump_speed=30, jump_cost=20, stamina=0.75, avi=bird)

wn.listen()
wn.onkeypress(agent.jump, "space")

# Game loop including start screen and death
while True:

    # Set up game
    game_state = 1
    score = 0
    pen.clear()
    pen.write(
        "Score: {}    High Score: {}".format(score, highscore),
        align="center",
        font=("Comic Sans", 12, "bold"),
    )
    title.write("Clappy Bird", align="center", font=("Comic Sans", 24, "bold"))
    subtitle.write(
        "press space to start", align="center", font=("Comic Sans", 16, "bold")
    )

    # Start screen
    while True:
        wn.update()
        agent.goto(-0, 0)
        agent.energy = 100
        energy_pen.clear()
        state_pen.clear()
        if agent.avi.direction == "up":
            title.clear()
            subtitle.clear()
            break
        else:
            pass

    # Main game loop
    agent.t = 0
    prev_state = None
    while True:
        wn.update()

        # Standard loop actions
        agent.regain_energy()
        agent.implement_gravity(env)
        game_state = agent.check_for_death(env)
        score = agent.check_for_new_score(env, score)

        # Generate tube on RHS
        if agent.t % 25 == 0:
            env.generate_new_tube()

        # tubes cascade to LHS
        for i in range(len(env.tubes)):
            x = env.tubes[i].x
            env.tubes[i].setx(x - env.tube_v)

        if score > highscore:
            highscore = score

        # update score
        pen.clear()
        pen.write(
            f"Score: {score}    High Score: {highscore}",
            align="center",
            font=("Comic Sans", 12, "bold"),
        )

        sleep(0.05)
        agent.t += 1
        agent.time_since_jump += 1
        if game_state == 0:
            break
        else:
            pass

        for i, tube in enumerate(env.tubes):
            if tube.x < -300:
                del env.tubes[i]

        # Find current state
        state = agent.find_state(env)
        ### MAKE GRAPH ENTRY HERE
        prev_state = state

        state_pen.clear()
        state_string = ""
        for k, v in state.items():
            state_string += f"{k}: {v} \n"
        state_pen.write(state_string, align="left", font=("Comic Sans", 20, "bold"))

        if agent.energy > 80:
            energy_color = "green"
        elif agent.energy > 30:
            energy_color = "yellow"
        else:
            energy_color = "red"

        energy_pen.clear()
        energy_pen.color(energy_color)
        energy_pen.write(
            f"E: {int(agent.energy)}", align="left", font=("Comic Sans", 20, "bold")
        )

    # death
    for tube in env.tubes:
        tube.goto(-1000, -1000)
        del tube
    agent.avi.direction = "stop"

# finalise
wn.mainloop()
turtle.done()
