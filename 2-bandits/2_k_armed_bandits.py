from blocks import *
import default_args
import yaml
import sys
from tqdm import tqdm

def parameter_array(param_name, param, type_, len_):
    if isinstance(param, type_):
        param = [param for e in range(len_)]
    elif isinstance(param, list):
        assert len(param) == len_
    else:
        raise TypeError(
            f"{param_name} must be floats or list of floats (of size num_agents)"
        )
    return param


def general_run(
    epses,
    num_agents,
    num_steps,
    k,
    q_var,
    q_mean,
    alphas,
    step_methods,
    variation_step,
    Q0s,
    reward_uncertainty,
    cs,
):

    epses = parameter_array("epses", epses, float, num_agents)
    alphas = parameter_array("alphas", alphas, float, num_agents)
    step_methods = parameter_array("step_methods", step_methods, str, num_agents)
    Q0s = parameter_array("Q0s", Q0s, float, num_agents)
    cs = parameter_array("cs", cs, float, num_agents)

    group_of_agents = GroupOfAgents(
        k=k,
        epses=epses,
        step_methods=step_methods,
        q_var=q_var,
        q_mean=q_mean,
        alphas=alphas,
        Q0s=Q0s,
        variation_step=variation_step,
        reward_uncertainty=reward_uncertainty,
        cs=cs,
    )

    graphs = [
        {"t": [], "average_score": [], "optimal_choice_prop": []}
        for j in range(num_agents)
    ]

    for step in range(num_steps):
        latest_stats = group_of_agents.forward_run()

        # Slows it down, but sanity check that rewards are always the same for each bandit
        agents = group_of_agents.agents
        bandit_rewards = [
            [b.latest_reward for b in list(a.bandits.keys())] for a in agents
        ]
        assert bandit_rewards.count(bandit_rewards[0]) == len(bandit_rewards)

        for i, graph in enumerate(graphs):
            for k in graph:
                graph[k].append(latest_stats[i][k])

    return graphs


def averaged_runs(
    num_runs,
    **kwargs
):
    graphs = []
    for run in tqdm(range(num_runs)):
        graphs.append(general_run(**kwargs))
    num_variations = [len(g) for g in graphs]
    assert num_variations.count(num_variations[0]) == len(num_variations)

    example_dict = graphs[0][0].copy()
    avg_dict_list = [{k: None for k in example_dict.keys()} for j in range(num_variations[0])]

    for i, avg_dict in enumerate(avg_dict_list):
        for k in avg_dict.keys():
            avg_dict[k] = np.average([run_graph[i][k] for run_graph in graphs], axis = 0)
    
            # import pdb; pdb.set_trace()
    
    return avg_dict_list



if __name__ == "__main__":

    args = default_args.args.copy()

    with open("config.yaml", "r") as f:
        yaml_args = yaml.load(f.read())

    args.update(yaml_args)

    graphs = averaged_runs(**args)

    f = plt.figure(figsize=(20, 8))
    average_score_plot = f.add_subplot(121)
    optimal_choice_prop_plot = f.add_subplot(122)

    average_score_plot.set_ylim(0, 2.0)
    optimal_choice_prop_plot.set_ylim(0, 100)

    # Removing first step from plots
    for j, graph in enumerate(graphs):
        average_score_plot.plot(
            graph["t"][1:], graph["average_score"][1:], label=str(args["epses"][j])
        )

    for j, graph in enumerate(graphs):
        pcs = [g * 100 for g in graph["optimal_choice_prop"][1:]]
        optimal_choice_prop_plot.plot(graph["t"][1:], pcs, label=str(args["epses"][j]))

    plt.legend()

    plt.savefig(sys.argv[1])