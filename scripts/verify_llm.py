import os
from pathlib import Path
import subprocess
import argparse
import json
from openai import OpenAI
import time
client = OpenAI(api_key=Path('api_key.txt').read_text())

def verify_plan(command_folder):
    time_start = time.time()
    # verify if the task is completed
    log_file = open(f"./logs/{command_folder}" + "/log.txt")
    log_data = log_file.readlines()
    task = log_data[0]
    # verify_gt = log_data[10]
    # print("verify_gt is:")
    # print(verify_gt)
    
    gt = log_data[9]
    print("gt is:")
    print(gt)
    if not os.path.exists(f"./logs/{command_folder}/environment_states.json"):
        # if the environment state file does not exist, meaning the task is not completed with unknown reason
        result = {
            'isComplete': False,
            'failure_reason': "Unknown",
            'completed_tasks': [],
            'remaining_tasks': ['"Nothing is completed"'],
            }
        return result
    else:
        with open(f"./logs/{command_folder}/environment_states.json", "r", encoding="utf-8") as f:
            environment_states = json.load(f)
    
    # print(environment_states["object_info"]["GarbageCan_d3abea71"])
    


    prompt = f"""
        you are a task planning expert. Your task is to verify if the task is completed or not. You will be given '''task''' which is the final goal, '''environment state''' which is the current state of environment, and '''ground truth''' which is the ground truth you should check in environment.
    
        object information in '''environment state''' includes the object information:
        {{"objectId": unique id of the object,
        "objectType": object type, can have multiple same type of objects in the environment,
        "position": position of the object,
        "isPickedUp": bool, true if the object is picked up,
        "isOpen": bool, true if the object is open,
        "isSliced": bool, true if the object is sliced,
        "isToggled": bool, true if the object is toggled,
        "isBroken": bool, true if the object is broken,
        "isFilledWithLiquid": bool, true if the object is filled with liquid,
        "contains": list of object ids of the objects contained in the object,
        "center": center of the object,
        "size": size of the object,
        }}

        ## Input
        ###task:
        {task}

        ### ground truth: this is a list of items you need to check in the environment, do not check other items if not specified in the ground truth.
        {gt}

        ### environment state
        {environment_states}
        
        You should reason over the above information,
        and tell me if the task is complete or not, if not, tell me what is completed and what was not. 
        

        ### Task Completion Evaluation Criteria:
        you are given the '''ground truth''' and '''environment state'''. If the 'state' of each object in '''ground truth''' is the following:
        - contains: check If the 'state' of an object in ground truth is "contains", check if any object of the specified type exists within the 'contains' field of the environment object. Partial matches are acceptable.

        * Note: gound truth only show the type of objects, while environment state using object id. This meaning not specific object need to be activated.
        There might be multiple same type of objects in the environment, be tolerant. If at least one object of the same type satisfy the ground truth condition, then the subtask is completed.
        Noticed that '''ground truth''' and '''environment state''' might have different naming. For example, state of object in ground truth is Toggled, means that the isToggled field of the object in environment state is true.
        Please be tolerent and some of Criteria is given to you in above.
        If you are not sure whether object A contains object B, first check the contains list. If absent, verify if B's position is inside A’s bounding box (size + position tolerance).


        your output should be in the following format in dictionary:
        ## Output Format
        {{
        "isComplete": bool,
        "failure_reason": str of reason why the task is failed,
        "according": str of reason why you determine the task is completed or not,
        "completed_tasks": ['list of completed item', empty list if none],
        "remaining_tasks": ['list of completed item', empty list if none],
        }}
        * Note: only return the JSON schema format, don't say anything else. Do not use markdown format.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": "You are a great robotic developer. You need to verify whether the task is completed or not."},
            {"role": "user", "content": prompt}
        ]
    )
    
    response = response.choices[0].message.content
    response = json.loads(response)
    time_end = time.time()
    exe_time = time_end - time_start
    print(f"Time taken: {exe_time:.6f} seconds")
    print(response)
    return response
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", type=str, required=True)
    args = parser.parse_args()

    expt_name = args.command
    verify_plan(expt_name)