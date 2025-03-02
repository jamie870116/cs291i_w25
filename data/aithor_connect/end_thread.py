
for i in range(25):
    action_queue.append({'action':'Done'})
    action_queue.append({'action':'Done'})
    action_queue.append({'action':'Done'})
    time.sleep(0.1)

task_over = True
time.sleep(5)


exec = float(success_exec) / float(total_exec)

print (ground_truth)
objs = list([obj for obj in c.last_event.metadata["objects"]])

gcr_tasks = 0.0
gcr_complete = 0.0
for obj_gt in ground_truth:
    obj_name = obj_gt['name']
    state = obj_gt['state']
    contains = obj_gt['contains']
    gcr_tasks += 1
    for obj in objs:
        # if obj_name in obj["name"]:
        #     print (obj)
        if state == 'SLICED':
            if obj_name in obj["name"] and obj["isSliced"]:
                gcr_complete += 1 
                
        if state == 'OFF':
            if obj_name in obj["name"] and not obj["isToggled"]:
                gcr_complete += 1 
        
        if state == 'ON':
            if obj_name in obj["name"] and obj["isToggled"]:
                gcr_complete += 1 
        
        if state == 'HOT':
            # print (obj)
            if obj_name in obj["name"] and obj["temperature"] == 'Hot':
                gcr_complete += 1 
                
        if state == 'COOKED':
            if obj_name in obj["name"] and obj["isCooked"]:
                gcr_complete += 1 
                
        if state == 'OPENED':
            if obj_name in obj["name"] and obj["isOpen"]:
                gcr_complete += 1 
                
        if state == 'CLOSED':
            if obj_name in obj["name"] and not obj["isOpen"]:
                gcr_complete += 1 
                
        if state == 'PICKED':
            if obj_name in obj["name"] and obj["isPickedUp"]:
                gcr_complete += 1 
        
        if len(contains) != 0 and obj_name in obj["name"]:
            print (contains, obj_name, obj["name"])   
            for rec in contains:
                if obj['receptacleObjectIds'] is not None:
                    for r in obj['receptacleObjectIds']:
                        print (rec, r)
                        if rec in r:
                            print (rec, r)
                            gcr_complete += 1 
                    
            
             
sr = 0
tc = 0
if gcr_tasks == 0:
    gcr = 1
else:
    gcr = gcr_complete / gcr_tasks

if gcr == 1.0:
    tc = 1 
    
max_trans += 1
no_trans_gt += 1
print (no_trans_gt, max_trans, no_trans)
if max_trans == no_trans_gt and no_trans_gt == no_trans:
    ru = 1
elif max_trans == no_trans_gt:
    ru = 0
else:
    ru =  (max_trans - no_trans) / (max_trans - no_trans_gt)

if tc == 1 and ru == 1:
    sr = 1

print (f"SR:{sr}, TC:{tc}, GCR:{gcr}, Exec:{exec}, RU:{ru}")



generate_video()

def save_environment_states_to_file(object_info, agent_info, reachable_p, obj_changed=None):
    data = {
        "object_info": object_info,
        "agent_info": agent_info,
        "reachable_positions": reachable_p,
        "obj_changed": obj_changed,
    }
    cur_path = os.path.dirname(__file__) + "/"
    with open(os.path.join(cur_path, 'environment_states.json'), 'w') as f:
        json.dump(data, f, indent=4)


event = c.last_event
object_info = {}
multi_agent_info = {}
i = 0

def closest_agent_to_object(agents, object):
    """
    find the closest agent

    :param agents: a dict of agents info, contain position (x, y, z)
    :param object: a certain object info, contain position (x, y, z)
    :return: closest agent index
    """
    object_position = object['position']
    closest_index = None
    closest_distance = float('inf')

    for index, agent_pos in enumerate(agents):
        # agent_pos = agent['position']
        distance = math.sqrt(
            (agent_pos['x'] - object_position['x']) ** 2 +
            (agent_pos['y'] - object_position['y']) ** 2 +
            (agent_pos['z'] - object_position['z']) ** 2
        )
        if distance < closest_distance:
            closest_distance = distance
            closest_index = index

    return closest_index

agent_pos = []
for e in multi_agent_event.events:
    multi_agent_info['agent_'+ str(i)] = e.metadata['agent']
    agent_pos.append(e.metadata['agent']['position'])
    i += 1
obj_changed = [[] for _ in range(no_robot)]
for obj in event.metadata['objects']:
    cur_obj = {
                    "objectId": obj["objectId"],
                    "objectType": obj["objectType"],
                    "position": obj["position"],
                    "isPickedUp": obj.get("isPickedUp", False),
                    "isOpen": obj.get("isOpen", False),
                    "isSliced": obj.get("isSliced", False),
                    "isToggled": obj.get("isToggled", False),
                    "isBroken": obj.get("isBroken", False),
                    "isFilledWithLiquid": obj.get("isFilledWithLiquid", False),
                    "mass": obj.get("mass", 0.0),
                    "center": obj.get("axisAlignedBoundingBox", {}).get("center", None),
                    "state": obj.get("state", "None")
                }
    object_info[obj['name']] = cur_obj
    if obj['isPickedUp']:
        closest_agent_idx = closest_agent_to_object(agent_pos, cur_obj)
        obj_changed[closest_agent_idx].append(cur_obj)


reachable_p_ = c.step(action="GetReachablePositions").metadata["actionReturn"]
reachable_p = [(p["x"], p["y"], p["z"]) for p in reachable_p_]
c.stop()
save_environment_states_to_file(object_info, multi_agent_info, reachable_p, obj_changed)


