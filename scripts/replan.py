import os
from pathlib import Path
import subprocess
import argparse
import json
from openai import OpenAI
import time
client = OpenAI(api_key=Path('api_key.txt').read_text())

def replan_code_file(expt_name, client=client, prev_error=None, prev_code_file=None):
    time_start = time.time()
    log_path = os.getcwd() + "/logs/" + expt_name

    log_file = open(log_path + "/log.txt")
    log_data = log_file.readlines()
    # get task
    task = log_data[0]

    # get the number of robots
    robot_no = log_data[8].count('name')
    # get floor number
    flr_no = int(log_data[4][12:])
    # based on loor-plan get scene
    scene = ''
    if flr_no < 30:
        scene = "kitchen"
    elif flr_no < 230:
        scene = "living room"
    elif flr_no < 330:
        scene = "bedroom"
    else:
        scene = "bathroom"

    # 读取 "code_plan.py" 的内容
    code_file_path = prev_code_file or f"{log_path}/code_plan.py"
    with open(code_file_path, "r", encoding="utf-8") as f:
        code_plan = f.read()

    # 读取 "environment_states.json" 的内容
    if not os.path.exists(f"{log_path}/environment_states.json"):
        environment_states = None
    else:
        with open(f"{log_path}/environment_states.json", "r", encoding="utf-8") as f:
            environment_states = json.load(f)

    # read input train prompts
    init_prompt_file = open(os.getcwd() + "/data/pythonic_plans/train_replan_initial.py", "r")
    init_prompt = init_prompt_file.read()
    init_prompt_file.close()

    # actions
    actions = ["GoToObject <robot><object>", "OpenObject <robot><object>", "CloseObject <robot><object>", 
                   "BreakObject <robot><object>", "SliceObject <robot><object>", "SwitchOn <robot><object>", 
                   "SwitchOff <robot><object>", "CleanObject <robot><object>", "PickupObject <robot><object>", 
                   "PutObject <robot><object><receptacleObject>", "DropHandObject <robot><object>", 
                   "ThrowObject <robot><object>", "PushObject <robot><object>", "PullObject <robot><object>"]
    actions = ', '.join(actions)

    # actions for initialization
    ai2thor_actions = [
        "PickupObject", 
        "DropHandObject", 
        "ThrowObject", 
        "PushObject", 
        "PullObject", 
        "OpenObject", 
        "CloseObject", 
        "ToggleObjectOn", 
        "ToggleObjectOff", 
        "PutObject", 
        "SliceObject", 
        "BreakObject", 
        "UseUpObject", 
        "EmptyLiquidFromObject"
    ]
    ai2thor_actions = ', '.join(ai2thor_actions)

    # 组合 prompt
    prompt = f"""
    You are an excellent task planner whose task is to help {robot_no} robots to complete the final task of "{task}" in {scene}. 
    In current stage, the robots in the environment had execute a existing plan. 
    However, it seems like the task is not yet completed. And your task is to based on previous plan and the information of last executed state to re-generated a new plan for the two robot agents to complete the final task.
    
    you will be given the following information:

    ```Original Code Plan``` which is a segment of python code file, this the section that how robot should take actions.
    And, you will also have following information which is the last executed state```Environment States```, this is a json file that contains the following :  ```agent_info``` which is the information of the robot agents, 
    ```object_info``` which is the objects list that are available in the environment, 
    ```reachable_positions``` which is the the position that an agent can reach within the environment, ```obj_changed``` which is the the object that ```agent[i]``` was interacting.

    And you will also have ```ai2thor_actions``` which is the list of actions that an agent can perform. These actions should be use in Code Plan.
    you will have the information of what task needs to be done, what objects are available in the scene (including the position of the objects)

    """

    prompt += f"""
    ## Original Code Plan:
    {code_plan}

    ## Environment States, this will only be provided if previous plan is executed but failed.
    {json.dumps(environment_states, indent=2)}

    ## ai2thor_actions for code plan
    {actions}

    ## ai2thor_actions for initialization which you should use it in the right syntax according to the ai2thor library.
    {ai2thor_actions}

    # Task
    Based on the above code plan and environment states, generate an improved and executable Python script. 
    
    You should reason over the information above, and generate an improved and executable Python script to complete the final task.
    Before generating a new plan, write the previous failure reason in comment.
    Your output should be two part of code, one is the initialization part, and another is code plan part. 
    For Initialization stage, which should be a segment of python code, starts with ### Initialization Start and ends with ### Initialization End, 
    this is the section of initialzation the environment, you need to use Teleport to setup agent's position.
    And redo the previously completed subtasks, such as pickup the specific object using objectID, or Turn on something using objectID. Make sure these are acted by the correct agent.
    These are the actions you can use for initialization, which are from ai2thor library: [PickupObject, PutObject, DropHandObject, ThrowObject, MoveHeldObjectAhead, MoveHeldObject, RotateHeldObject, DirectionalPush, PushObject, PullObject, PlaceObjectAtPoint ,OpenObject, CloseObject, BreakObject, CookObject, SliceObject, ToggleObjectOn, ToggleObjectOff, DirtyObject, CleanObject, FillObjectWithLiquid, EmptyLiquidFromObject, UseUpObject]
    
    ##Here is an example of Initialization:
    {init_prompt}

    The code plan part should be like the Original Code Plan. Refer to ai2thor_actions which is a list of actions that robot can perform. The code plan part do not need to redo the previously success subtask. The previously success subtask should be done in the Initialization stage. Be aware of that agent cannot put object if it is not picked up. Assign the correct agent to the action.
    In this part, you should use the correct syntax and method of actionfrom ai2thor library.
    Your output format should be like:
    ### Initialization Start
    code of initialization...
    ### Initialization End

    ### Code Plan Start
    code plan...
    ### Code Plan End

    Make sure the output file can successfully execute and stimulate the robot's actions and complete the final task. You should initialize the position of agents based on the ```env_state```.
    The code plan part no need to verify current state, just think of this is the next step from ```previous plan```.
    Make sure the type of the object is exist in ```object_info```. Sometimes the object name is not correct in Original Code Plan, which is one of the reason of failure.
    If the previous plan is not executed, you should not provide any initialization code, only code plan part.
    * NOTE: DO NOT OUTPUT ANYTHING EXTRA OTHER THAN WHAT HAS BEEN SPECIFIED
    NOTE: Do not output any other content. DO NOT use markdown format.
    Let's work this out in a step by step way to be sure we have the right answer.

    """
    if prev_error:
        prompt += f"""
        ## Previous Error:
        {prev_error}
        """

    # print('=======')
    # print(prompt)
    # print('=======')
    
    # 调用 OpenAI API (使用 gpt-4o-mini)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an expert robot task planner."},
                  {"role": "user", "content": prompt}],
        temperature=0.5
    )

    # 提取生成的代码
    generated_code = response.choices[0].message.content.strip()

    # 输出到 "code_replan.py"
    with open(f"{log_path}/code_replan.py", "w", encoding="utf-8") as f:
        f.write(generated_code)
    time_end = time.time()
    exe_time = time_end - time_start
    print(f"Time taken: {exe_time:.6f} seconds")
    return (f"{log_path}/code_replan.py")

def replan_main(args, prev_error, prev_code_file=None):
    time_start = time.time()
    client = OpenAI(api_key=Path('api_key.txt').read_text())
    expt_name = args["command"]
    ai_exec_file = replan_code_file(expt_name, client, prev_error, prev_code_file)
    time_end = time.time()
    exe_time = time_end - time_start
    print(f"Time taken: {exe_time:.6f} seconds")
    print('Finished')
    return ai_exec_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", type=str, required=True)
    args = parser.parse_args()

    expt_name = args.command
    # ai_exec_file = replan_main(args)
    replan_code_file(expt_name)


# parser = argparse.ArgumentParser()
# parser.add_argument("--command", type=str, required=True)
# args = parser.parse_args()

# expt_name = args.command
# ai_exec_file = replan_code_file(expt_name)
# print('Finished')
# subprocess.run(["python", ai_exec_file])