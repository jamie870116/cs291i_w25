import os
import json
import time
from fuzzywuzzy import fuzz, process
import argparse
def verify_plan(command_folder):
    time_start = time.time()
    # verify if the task is completed
    log_file = open(f"{command_folder}" + "/log.txt")
    log_data = log_file.readlines()
    task = log_data[0]
    # verify_gt = log_data[10]
    # print("verify_gt is:")
    # print(verify_gt)

    STATE_MAPPING = {
        "ON": ["isToggled"],
        "OFF": ["isToggled", False],
        "BROKEN": ["isBroken"],
        "FILLED": ["isFilledWithLiquid"],
        "OPEN": ["isOpen"],
        "CLOSED": ["isOpen", False],
        "PICKED_UP": ["isPickedUp"],
        "SLICED": ["isSliced"]
    }
    
    gt = log_data[9]
    print("gt is:")
    print(gt)
    if not os.path.exists(f"{command_folder}/environment_states.json"):
        # if the environment state file does not exist, meaning the task is not completed with unknown reason
        result = {
            'isComplete': False,
            'failure_reason': "Unknown",
            'completed_tasks': [],
            'remaining_tasks': ['"Nothing is completed"'],
            }
        return result
    else:
        with open(f"{command_folder}/environment_states.json", "r", encoding="utf-8") as f:
            environment_states = json.load(f)
    
    # print(environment_states["object_info"]["GarbageCan_d3abea71"])
    env_obj_info = environment_states["object_info"]
    env_objs = env_obj_info.keys()
    gt_json = json.loads(gt.split("=", 1)[1].strip().replace("'", '"'))
    response = {}
    for obj in gt_json:
        obj_name = obj["name"]
        state_desc = obj["state"]
        print("obj_name:" + obj_name + ", state_desc:" + state_desc)

        # Step 1: Find exact matches using prefix
        prefix_matches = [item for item in env_objs if item.startswith(obj_name.strip())]

        # Step 2: Use NLP fuzzy matching if no exact prefix matches found
        fuzzy_matches = process.extractBests(obj_name, env_objs, score_cutoff=80)

        # Combine both matching results
        all_matches = prefix_matches + [match[0] for match in fuzzy_matches if match[0] not in prefix_matches]
        print("Matched targets are: " + str(all_matches))
        # Step 3: Find corresponding state/contain property
        if obj['contains']:
            print(2)
            found_content = False
            for matched_target in all_matches:
                for gt_content in obj['contains']:
                    print("ground truth contents and env state contents:")
                    print(gt_content)
                    print(env_obj_info[matched_target]['contains'])
                    if env_obj_info[matched_target]['contains']:
                        matched_content = process.extractOne(gt_content, env_obj_info[matched_target]['contains'], score_cutoff=80)
                        if matched_content is not None:
                            print("Matched content:")
                            print(matched_content)
                            found_content = True
                            break
                if found_content:
                    break
            response[obj_name] = "success" if found_content else "failed"
        else:
            print(1)
            matched_property = None
            for key, properties in STATE_MAPPING.items():
                if process.extractOne(state_desc, [key], score_cutoff=80):  # Fuzzy match the state
                    matched_property = properties
                    break
            
            print("matched property is: " + str(matched_property))

            # Step 4: Validate the object state
            if matched_property:
                success_found = False
                for env_obj_match in all_matches:
                    env_state = env_obj_info[env_obj_match]
                    property_name = matched_property[0]
                    expected_value = matched_property[1] if len(matched_property) > 1 else True
                    print("expected and actual:")
                    print(expected_value)
                    print(env_state.get(property_name))
                    if env_state.get(property_name) == expected_value:
                        success_found = True
                        break
                response[obj_name] = "success" if success_found else "failed"
            
    
    complete = True
    for item in response.keys():
        if response[item] == 'failed':
            complete = False
    response["isComplete"] = complete
    time_end = time.time()
    exe_time = time_end - time_start
    print(f"Time taken: {exe_time:.6f} seconds")
    response['timeSpent'] = exe_time
    response = json.dumps(response, indent=4)
    response = json.loads(response)
    return response
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", type=str, required=True)
    args = parser.parse_args()

    expt_name = args.command
    response = verify_plan(expt_name)
    print(response)