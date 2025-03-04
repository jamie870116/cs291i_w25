# Below is an example of Initialization of the position of agent, and initialize the subtasks that were already completed.
### Initialization Start
# Set up initial environment state based on `env_state`
# Ensure robots are positioned correctly and set up necessary object states
# Teleport agents to their last known positions
c.step(dict(action="Teleport", position={"x": -1.0279, "y": 0.9028, "z": 0.3249}, agentId=0))
c.step(dict(action="Teleport", position={"x": -1.9983, "y": 0.9028, "z": 1.2995}, agentId=1))

# Ensure the faucet is turned on (Previously completed successfully)
c.step(dict(action="ToggleObjectOn", objectId="Faucet|-00.43|+00.00|+00.76", agentId=0, forceAction=True))

# Ensure the toilet paper is picked up (Previously completed successfully)
c.step(dict(action="PickupObject", objectId="ToiletPaper|-02.93|+01.20|+01.46", agentId=1, forceAction=True))

### Initialization Start