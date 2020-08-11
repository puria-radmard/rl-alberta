from graphics_util import *
from rl import Environment, Agent

env = Environment(
    tube_v=10, g=-50, death_reward=-10, score_reward=2, low_energy_reward=-0.1
)

agent = Agent(jump_speed=30, jump_cost=20, stamina=0.75, discount_rate=0.9, avi=bird)

wn.listen()
wn.onkeypress(agent.jump, "space")

# Game loop including start screen and death
while True:

    # Set up game
    env.game_state = 1
    agent.player_score = 0
    init_pens(pen, title, subtitle, agent.player_score, highscore)

    # Start screen
    while True:
        wn.update()
        agent.goto(-0, 0)
        agent.energy = 100
        energy_pen.clear()
        state_pen.clear()
        agent.jump()
        if agent.avi.direction == "up":
            title.clear()
            subtitle.clear()
            break
        else:
            pass

    # Main game loop
    agent.t = 0
    agent.prev_state = agent.state

    while True:
        wn.update()

        env.move_tubes(agent)

        if agent.player_score > highscore:
            highscore = agent.player_score

        sleep(0.05)
        agent.t += 1
        agent.time_since_jump += 1
        if env.game_state == 0:
            break
        else:
            pass

        # Get s_t
        agent.state = agent.find_state(env)

        # Do r_t
        a_t = agent.apply_policy()

        # Get r_t from s_t and a_t
        r_t = agent.read_environment(env)

        # Memory build up for this episode
        # A[t] made at/after S[t], giving R[t]
        agent.S.append(agent.state.copy())
        agent.A.append(a_t)
        agent.R.append(r_t)

        print(agent.S[-1], agent.A[-1], agent.R[-1])

        agent.prev_state = agent.state

        # Standard loop actions
        agent.regain_energy()
        agent.implement_gravity(env)

        update_pens(agent, state_pen, pen, energy_pen, agent.player_score)

    # death
    for tube in env.tubes:
        tube.goto(-1000, -1000)
        del tube
    agent.avi.direction = "stop"
    agent.state = agent.death_state
    agent.S.append(agent.state.copy())

    # Apply expected returns and Bellman's
    agent.post_process()


# finalise
wn.mainloop()
turtle.done()
