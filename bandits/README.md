# Fully configurable bandits from scratch

A playground for trying out parameters on a set of agents
Parameters can be set in X.yaml, and running:

```
python k_armed_bandits.py X.yaml
```

Will save the average score and percentage optimal plots over timesteps for each agent under `X.yaml.png`
Eah run in num_runs is unique, but identical for each of the agents, allowing for exact analysis of the parameters' effects.

Parameters are explained in `example_config.yaml`, and other examples can be found in this directory, along with their plots/