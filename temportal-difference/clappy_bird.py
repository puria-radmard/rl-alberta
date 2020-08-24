from graphics_util import *
from rl import Environment, Agent
from pprint import pprint
import pickle

env = Environment(
    tube_v=10, tube_gen_rate = 25, g=-50, death_reward=-8, score_reward=5, low_energy_reward=-0.01
)

agent = Agent(jump_speed=30, jump_cost=20, stamina=0.75, discount_rate=0.9, avi=bird)

wn.listen()
wn.onkeypress(agent.jump, "space")


num_eps = 0

# Game loop including start screen and death
while True:

    num_eps += 1

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

    while True:

        wn.update()

        env.move_tubes(agent)

        if agent.player_score > highscore:
            highscore = agent.player_score

        # Get s_t
        s_t = agent.find_state(env); agent.S.append(s_t)
        # Do a_t
        a_t = agent.apply_policy(s_t); agent.A.append(a_t)
        agent.time_since_jump += 1
        # Get r_t from s_t and a_t
        r_t = agent.check_rewards(env); agent.R.append(r_t)

        #sleep(0.05)
        agent.t += 1

        if env.game_state == 0:
            break
        
        # Removes need for an explicity start state
        try:
            agent.update_state_info(s_t, s_prev, a_t, r_t)
        except NameError:
            pass
        s_prev = s_t

        # Standard loop actions
        agent.regain_energy()
        agent.implement_gravity(env)

        update_pens(agent, s_t, state_pen, pen, energy_pen, agent.player_score)

    # death
    for tube in env.tubes:
        tube.goto(-1000, -1000)
        del tube
    agent.avi.direction = "stop"

    s_t = agent.death_state

    agent.update_state_info(s_t, s_prev, a_t, r_t)

    agent.post_process()    
    
    if num_eps % 500 == 0:
        # print(f"Uploading information after {num_eps} episodes...")
        # agent.upload()
        # print("Done")
        with open(f"state-{num_eps}.pkl", "wb") as jfile:
            pickle.dump(agent.state_info, jfile)

# finalise
wn.mainloop()
turtle.done()