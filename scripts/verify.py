import json

tests = {
    "floor_plan": 414,
    "task": "Turn on Sink faucet and put toilet paper in the trash", 
    "ground_truth": [{"name": "Faucet", "contains": [], "state": "ON"},{"name": "GarbageCan", "contains": ["ToiletPaper"], "state": "None"}]
}


with open('./data/samples/sample_environment_states.json', 'r') as f:
    env_states = json.load(f)

object_info = env_states["object_info"]

ground_truth = tests["ground_truth"]
res = []
failed = []
for gt in ground_truth:
    obj_name = gt["name"]
    obj_contains = gt["contains"]
    obj_state = gt["state"]
    
    if obj_contains:
        for obj in object_info:
            if obj_name in object_info[obj]["objectType"]:
                print(obj)
                print(object_info[obj]["contains"])
                for c in obj_contains:
                    for obj_in in object_info[obj]["contains"]:
                        if c in obj_in:
                            res.append(f"{obj_name} contains {c}") 

        if not res:
            failed.append(f"{obj_name} does not contain {c}")

    if obj_state:
           if obj_state == 'ON':
               for obj in object_info:
                   if obj_name in object_info[obj]["objectType"]:
                       if object_info[obj]["isToggled"]:
                           res.append(f"{obj_name} is ON")
                       




# def verify_plan(plan_path, floor_no):
#     with open(plan_path, 'r') as f:
#         plan = json.load(f)
#     return plan