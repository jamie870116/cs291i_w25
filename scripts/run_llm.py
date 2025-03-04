import copy
import glob
import json
import os
import argparse
from pathlib import Path
from datetime import datetime
import random
import subprocess

from openai import OpenAI

client = OpenAI(api_key=Path('api_key.txt').read_text())
import ai2thor.controller

from google import genai
from google.genai import types

# genai.configure(api_key=Path('gemini_api_key.txt').read_text())
gemini_client = genai.Client(api_key=Path('gemini_api_key.txt').read_text())

import sys
sys.path.append(".")

import resources.actions as actions
import resources.robots as robots

def LM(prompt, llm_model, llm_version, max_tokens=128, temperature=0, stop=None, logprobs=1, frequency_penalty=0):
    if llm_model == "gpt":

        if "gpt" not in llm_model:
            response = client.completions.create(model=llm_version, 
                                                prompt=prompt, 
                                                max_tokens=max_tokens, 
                                                temperature=temperature, 
                                                stop=stop, 
                                                logprobs=logprobs, 
                                                frequency_penalty = frequency_penalty)

            return response, response.choices[0].text.strip()

        else:
            response = client.chat.completions.create(model=llm_version, 
                                                messages=prompt, 
                                                max_tokens=max_tokens, 
                                                temperature=temperature, 
                                                frequency_penalty = frequency_penalty)

            return response, response.choices[0].message.content.strip()
    elif llm_model == "gemini":
        response = gemini_client.models.generate_content(
            model=llm_version,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
            ))
        if '```python' in response.text.strip():
            content = response.text.strip().split('```python')[1].split('```')[0]
            return response, content.strip()
        return response, response.text.strip()

def decompose_task(test_tasks, prompt, llm_model, llama_version):
    decomposed_plan = []
    for task in test_tasks:
        curr_prompt =  f"{prompt}\n\n# Task Description: {task}"
        if llm_model == "gpt":
            if "gpt" not in llama_version:
                # older gpt versions
                _, text = LM(curr_prompt, llm_model, llama_version, max_tokens=1000, stop=["def"], frequency_penalty=0.15)
            else:            
                messages = [{"role": "user", "content": curr_prompt}]
                _, text = LM(messages, llm_model, llama_version, max_tokens=1300, frequency_penalty=0.0)
        elif llm_model == "gemini":
            _, text = LM(curr_prompt, llm_model,args.gemini_model, max_tokens=1000, stop=["def"], frequency_penalty=0.15)
        decomposed_plan.append(text)
    return decomposed_plan

def allocate_robots(decomposed_plan, prompt, available_robots, objects_ai, llm_model, llama_version):
    allocated_plan = []
    for i, plan in enumerate(decomposed_plan):
        no_robot  = len(available_robots[i])
        curr_prompt = prompt + plan
        curr_prompt += f"\n# TASK ALLOCATION"
        curr_prompt += f"\n# Scenario: There are {no_robot} robots available, The task should be performed using the minimum number of robots necessary. Robots should be assigned to subtasks that match its skills and mass capacity. Using your reasoning come up with a solution to satisfy all contraints."
        curr_prompt += f"\n\nrobots = {available_robots[i]}"
        curr_prompt += f"\n{objects_ai}"
        curr_prompt += f"\n\n# IMPORTANT: The AI should ensure that the robots assigned to the tasks have all the necessary skills to perform the tasks. IMPORTANT: Determine whether the subtasks must be performed sequentially or in parallel, or a combination of both and allocate robots based on availablitiy. "
        curr_prompt += f"\n# SOLUTION  \n"
        if llm_model == "gpt":
            if "gpt" not in llama_version:
                # older versions of GPT
                _, text = LM(curr_prompt, llm_model, llama_version, max_tokens=1000, stop=["def"], frequency_penalty=0.65)

            elif "gpt-3.5" in llama_version:
                # gpt 3.5 and its variants
                messages = [{"role": "user", "content": curr_prompt}]
                _, text = LM(messages, llm_model, llama_version, max_tokens=1500, frequency_penalty=0.35)

            else:          
                # gpt 4.0
                messages = [{"role": "system", "content": "You are a Robot Task Allocation Expert. Determine whether the subtasks must be performed sequentially or in parallel, or a combination of both based on your reasoning. In the case of Task Allocation based on Robot Skills alone - First check if robot teams are required. Then Ensure that robot skills or robot team skills match the required skills for the subtask when allocating. Make sure that condition is met. In the case of Task Allocation based on Mass alone - First check if robot teams are required. Then Ensure that robot mass capacity or robot team combined mass capacity is greater than or equal to the mass for the object when allocating. Make sure that condition is met. In both the Task Task Allocation based on Mass alone and Task Allocation based on Skill alone, if there are multiple options for allocation, pick the best available option by reasoning to the best of your ability."},{"role": "system", "content": "You are a Robot Task Allocation Expert"},{"role": "user", "content": curr_prompt}]
                _, text = LM(messages,llm_model, llama_version, max_tokens=400, frequency_penalty=0.69)
        elif llm_model == "gemini":
            messages = "You are a Robot Task Allocation Expert. Determine whether the subtasks must be performed sequentially or in parallel, or a combination of both based on your reasoning. In the case of Task Allocation based on Robot Skills alone - First check if robot teams are required. Then Ensure that robot skills or robot team skills match the required skills for the subtask when allocating. Make sure that condition is met. In the case of Task Allocation based on Mass alone - First check if robot teams are required. Then Ensure that robot mass capacity or robot team combined mass capacity is greater than or equal to the mass for the object when allocating. Make sure that condition is met. In both the Task Task Allocation based on Mass alone and Task Allocation based on Skill alone, if there are multiple options for allocation, pick the best available option by reasoning to the best of your ability." + curr_prompt
            _, text = LM(messages, llm_model, llama_version, max_tokens=1000, stop=["def"], frequency_penalty=0.15)

        allocated_plan.append(text)
    return allocated_plan

def generate_code(decomposed_plan, allocated_plan, prompt, available_robots, llm_model, llama_version):
    code_plan = []
    prompt_file2 = os.getcwd() + "/data/pythonic_plans/train_final_exe_plan.py"
    final_exe_plan_file = open(prompt_file2, "r")
    final_exe_plan = final_exe_plan_file.read()
    final_exe_plan_file.close()

    if llm_model == "gemini":
        prompt += final_exe_plan

    for i, (plan, solution) in enumerate(zip(decomposed_plan,allocated_plan)):
        curr_prompt = prompt + plan
        curr_prompt += f"\n# TASK ALLOCATION"
        curr_prompt += f"\n\nrobots = {available_robots[i]}"
        curr_prompt += solution
        curr_prompt += f"\n# CODE Solution  \n"
        if llm_model == "gpt":
            if "gpt" not in llama_version:
                # older versions of GPT
                _, text = LM(curr_prompt, llm_model, llama_version, max_tokens=1000, stop=["def"], frequency_penalty=0.30)
            else:            
                # using variants of gpt 4 or 3.5
                messages = [{"role": "system", "content": "You are a Robot Task Allocation Expert"},{"role": "user", "content": curr_prompt}]
                _, text = LM(messages, llm_model, llama_version, max_tokens=1400, frequency_penalty=0.4)
        elif llm_model == "gemini":
            
            _, text = LM(final_exe_plan+curr_prompt, llm_model, llama_version, max_tokens=1000, stop=["def"], frequency_penalty=0.15)

        code_plan.append(text)
    return code_plan

def set_api_key(openai_api_key):
    client.api_key = Path(openai_api_key + '.txt').read_text()

# Function returns object list with name and properties.
def convert_to_dict_objprop(objs, obj_mass):
    objs_dict = []
    for i, obj in enumerate(objs):
        obj_dict = {'name': obj , 'mass' : obj_mass[i]}
        # obj_dict = {'name': obj , 'mass' : 1.0}
        objs_dict.append(obj_dict)
    return objs_dict

def get_ai2_thor_objects(floor_plan_id):
    # connector to ai2thor to get object list
    controller = ai2thor.controller.Controller(scene="FloorPlan"+str(floor_plan_id))
    obj = list([obj["objectType"] for obj in controller.last_event.metadata["objects"]])
    obj_mass = list([obj["mass"] for obj in controller.last_event.metadata["objects"]])
    controller.stop()
    obj = convert_to_dict_objprop(obj, obj_mass)
    return obj

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--floor-plan", type=int, required=True)
    parser.add_argument("--openai-api-key-file", type=str, default="api_key")
    parser.add_argument("--gemini-api-key-file", type=str, default="gemini_api_key")

    parser.add_argument("--llm-model", type=str, default="gpt", 
                        choices=['gpt', 'gemini'])
    parser.add_argument("--gemini-model", type=str, default="gemini-2.0-flash", 
                        choices=['gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-2.0-flash-lite-preview-02-05'])
    parser.add_argument("--gpt-version", type=str, default="gpt-4", 
                        choices=['gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo-16k'])

    parser.add_argument("--prompt-decompse-set", type=str, default="train_task_decompose", 
                        choices=['train_task_decompose'])

    parser.add_argument("--prompt-allocation-set", type=str, default="train_task_allocation", 
                        choices=['train_task_allocation'])

    parser.add_argument("--test-set", type=str, default="tests", 
                        choices=['final_test', 'tests'])

    parser.add_argument("--log-results", type=bool, default=True)

    return parser.parse_args()


def run_llm_main(args):
    
    set_api_key(args["openai_api_key_file"])

    if not os.path.isdir(f"./logs/"):
        os.makedirs(f"./logs/")

    # read the tasks        
    test_tasks = []
    robots_test_tasks = []  
    gt_test_tasks = []    
    trans_cnt_tasks = []
    max_trans_cnt_tasks = []  
    with open (f"./data/{args["test_set"]}/FloorPlan{args["floor_plan"]}.json", "r") as f:
        for line in f.readlines():
            # print(line)
            test_tasks.append(list(json.loads(line).values())[0])
            robots_test_tasks.append(list(json.loads(line).values())[1])
            gt_test_tasks.append(list(json.loads(line).values())[2])
            trans_cnt_tasks.append(list(json.loads(line).values())[3])
            max_trans_cnt_tasks.append(list(json.loads(line).values())[4])

    print(f"\n----Test set tasks----\n{test_tasks}\nTotal: {len(test_tasks)} tasks\n")
    # prepare list of robots for the tasks
    available_robots = []
    for robots_list in robots_test_tasks:
        task_robots = []
        for i, r_id in enumerate(robots_list):
            rob = robots.robots [r_id-1]
            # rename the robot
            rob['name'] = 'robot' + str(i+1)
            task_robots.append(rob)
        available_robots.append(task_robots)


    ######## Train Task Decomposition ########

    # prepare train decompostion demonstration for ai2thor samples
    prompt = f"from skills import " + actions.ai2thor_actions
    prompt += f"\nimport time"
    prompt += f"\nimport threading"
    objects_ai = f"\n\nobjects = {get_ai2_thor_objects(args["floor_plan"])}"
    prompt += objects_ai

    # read input train prompts
    decompose_prompt_file = open(os.getcwd() + "/data/pythonic_plans/" + args["prompt_decompse_set"] + ".py", "r")
    decompose_prompt = decompose_prompt_file.read()
    decompose_prompt_file.close()

    prompt += "\n\n" + decompose_prompt

    print ("Generating Decompsed Plans...")

    if args["llm_model"] == "gpt":
        decomposed_plan = decompose_task(test_tasks, prompt, args["llm_model"], args["gpt_version"])
    elif args["llm_model"] == "gemini":
        decomposed_plan = decompose_task(test_tasks, prompt, args["llm_model"], args["gemini_model"])

    # print('decomposed_plan  ', decomposed_plan[:100])
    print ("Generating Allocation Solution...")

    ######## Train Task Allocation - SOLUTION ########
    prompt = f"from skills import " + actions.ai2thor_actions
    prompt += f"\nimport time"
    prompt += f"\nimport threading"

    prompt_file = os.getcwd() + "/data/pythonic_plans/" + args["prompt_allocation_set"] + "_solution.py"
    allocated_prompt_file = open(prompt_file, "r")
    allocated_prompt = allocated_prompt_file.read()
    allocated_prompt_file.close()

    prompt += "\n\n" + allocated_prompt + "\n\n"
    if args["llm_model"] == "gpt":
        allocated_plan = allocate_robots(decomposed_plan, prompt, available_robots, objects_ai, args["llm_model"], args["gpt_version"])
    elif args["llm_model"] == "gemini":
        allocated_plan = allocate_robots(decomposed_plan, prompt, available_robots, objects_ai, args["llm_model"], args["gemini_model"])

    print ("Generating Allocated Code...")

    ######## Train Task Allocation - CODE Solution ########

    prompt = f"from skills import " + actions.ai2thor_actions
    prompt += f"\nimport time"
    prompt += f"\nimport threading"
    prompt += objects_ai

    prompt_file1 = os.getcwd() + "/data/pythonic_plans/" + args["prompt_allocation_set"] + "_code.py"
    code_prompt_file = open(prompt_file1, "r")
    code_prompt = code_prompt_file.read()
    code_prompt_file.close()

    prompt += "\n\n" + code_prompt + "\n\n"
    if args["llm_model"] == "gpt": 
        code_plan = generate_code(decomposed_plan, allocated_plan, prompt, available_robots, args["llm_model"], args["gpt_version"])
    elif args["llm_model"] == "gemini":
        code_plan = generate_code(decomposed_plan, allocated_plan, prompt, available_robots, args["llm_model"], args["gemini_model"])


    print("Storing generated plans...")
    # save generated plan
    exec_folders = []
    if args["log_results"]:
        line = {}
        now = datetime.now() # current date and time
        date_time = now.strftime("%m-%d-%Y-%H-%M-%S")

        for idx, task in enumerate(test_tasks):
            task_name = "{fxn}".format(fxn = '_'.join(task.split(' ')))
            task_name = task_name.replace('\n','')
            folder_name = f"{task_name}_plans_{args["llm_model"]}_{args["gpt_version"]}_{date_time}"
            exec_folders.append(folder_name)

            os.mkdir("./logs/"+folder_name)
            print(f'start storing {task}')
            with open(f"./logs/{folder_name}/log.txt", 'w') as f:
                f.write(task)
                f.write(f"\n\nGPT Version: {args["gpt_version"]}")
                f.write(f"\n\nFloor Plan: {args["floor_plan"]}")
                f.write(f"\n{objects_ai}")
                f.write(f"\nrobots = {available_robots[idx]}")
                f.write(f"\nground_truth = {gt_test_tasks[idx]}")
                f.write(f"\ntrans = {trans_cnt_tasks[idx]}")
                f.write(f"\nmax_trans = {max_trans_cnt_tasks[idx]}")

            with open(f"./logs/{folder_name}/decomposed_plan.py", 'w') as d:
                d.write(decomposed_plan[idx])

            with open(f"./logs/{folder_name}/allocated_plan.py", 'w') as a:
                a.write(allocated_plan[idx])

            with open(f"./logs/{folder_name}/code_plan.py", 'w') as x:
                x.write(code_plan[idx])

            print(f'{task} Plan Stored at "./logs/{folder_name}"')
    return exec_folders

if __name__ == "__main__":
    
    # Get arguments
    args = get_args()

    set_api_key(args.openai_api_key_file)

    if not os.path.isdir(f"./logs/"):
        os.makedirs(f"./logs/")

    # read the tasks        
    test_tasks = []
    robots_test_tasks = []  
    gt_test_tasks = []    
    trans_cnt_tasks = []
    max_trans_cnt_tasks = []  
    with open (f"./data/{args.test_set}/FloorPlan{args.floor_plan}.json", "r") as f:
        for line in f.readlines():
            # print(line)
            test_tasks.append(list(json.loads(line).values())[0])
            robots_test_tasks.append(list(json.loads(line).values())[1])
            gt_test_tasks.append(list(json.loads(line).values())[2])
            trans_cnt_tasks.append(list(json.loads(line).values())[3])
            max_trans_cnt_tasks.append(list(json.loads(line).values())[4])

    print(f"\n----Test set tasks----\n{test_tasks}\nTotal: {len(test_tasks)} tasks\n")
    # prepare list of robots for the tasks
    available_robots = []
    for robots_list in robots_test_tasks:
        task_robots = []
        for i, r_id in enumerate(robots_list):
            rob = robots.robots [r_id-1]
            # rename the robot
            rob['name'] = 'robot' + str(i+1)
            task_robots.append(rob)
        available_robots.append(task_robots)


    ######## Train Task Decomposition ########

    # prepare train decompostion demonstration for ai2thor samples
    prompt = f"from skills import " + actions.ai2thor_actions
    prompt += f"\nimport time"
    prompt += f"\nimport threading"
    objects_ai = f"\n\nobjects = {get_ai2_thor_objects(args.floor_plan)}"
    prompt += objects_ai

    # read input train prompts
    decompose_prompt_file = open(os.getcwd() + "/data/pythonic_plans/" + args.prompt_decompse_set + ".py", "r")
    decompose_prompt = decompose_prompt_file.read()
    decompose_prompt_file.close()

    prompt += "\n\n" + decompose_prompt

    print ("Generating Decompsed Plans...")

    if args.llm_model == "gpt":
        decomposed_plan = decompose_task(test_tasks, prompt, args.llm_model, args.gpt_version)
    elif args.llm_model == "gemini":
        decomposed_plan = decompose_task(test_tasks, prompt, args.llm_model, args.gemini_model)

    # print('decomposed_plan  ', decomposed_plan[:100])
    print ("Generating Allocation Solution...")

    ######## Train Task Allocation - SOLUTION ########
    prompt = f"from skills import " + actions.ai2thor_actions
    prompt += f"\nimport time"
    prompt += f"\nimport threading"

    prompt_file = os.getcwd() + "/data/pythonic_plans/" + args.prompt_allocation_set + "_solution.py"
    allocated_prompt_file = open(prompt_file, "r")
    allocated_prompt = allocated_prompt_file.read()
    allocated_prompt_file.close()

    prompt += "\n\n" + allocated_prompt + "\n\n"
    if args.llm_model == "gpt":
        allocated_plan = allocate_robots(decomposed_plan, prompt, available_robots, objects_ai, args.llm_model, args.gpt_version)
    elif args.llm_model == "gemini":
        allocated_plan = allocate_robots(decomposed_plan, prompt, available_robots, objects_ai, args.llm_model, args.gemini_model)

    print ("Generating Allocated Code...")

    ######## Train Task Allocation - CODE Solution ########

    prompt = f"from skills import " + actions.ai2thor_actions
    prompt += f"\nimport time"
    prompt += f"\nimport threading"
    prompt += objects_ai

    prompt_file1 = os.getcwd() + "/data/pythonic_plans/" + args.prompt_allocation_set + "_code.py"
    code_prompt_file = open(prompt_file1, "r")
    code_prompt = code_prompt_file.read()
    code_prompt_file.close()

    prompt += "\n\n" + code_prompt + "\n\n"
    if args.llm_model == "gpt": 
        code_plan = generate_code(decomposed_plan, allocated_plan, prompt, available_robots, args.llm_model, args.gpt_version)
    elif args.llm_model == "gemini":
        code_plan = generate_code(decomposed_plan, allocated_plan, prompt, available_robots, args.llm_model, args.gemini_model)


    print("Storing generated plans...")
    # save generated plan
    exec_folders = []
    if args.log_results:
        line = {}
        now = datetime.now() # current date and time
        date_time = now.strftime("%m-%d-%Y-%H-%M-%S")

        for idx, task in enumerate(test_tasks):
            task_name = "{fxn}".format(fxn = '_'.join(task.split(' ')))
            task_name = task_name.replace('\n','')
            folder_name = f"{task_name}_plans_{args.llm_model}_{args.gpt_version}_{date_time}"
            exec_folders.append(folder_name)

            os.mkdir("./logs/"+folder_name)
            print(f'start storing {task}')
            with open(f"./logs/{folder_name}/log.txt", 'w') as f:
                f.write(task)
                f.write(f"\n\nGPT Version: {args.gpt_version}")
                f.write(f"\n\nFloor Plan: {args.floor_plan}")
                f.write(f"\n{objects_ai}")
                f.write(f"\nrobots = {available_robots[idx]}")
                f.write(f"\nground_truth = {gt_test_tasks[idx]}")
                f.write(f"\ntrans = {trans_cnt_tasks[idx]}")
                f.write(f"\nmax_trans = {max_trans_cnt_tasks[idx]}")

            with open(f"./logs/{folder_name}/decomposed_plan.py", 'w') as d:
                d.write(decomposed_plan[idx])

            with open(f"./logs/{folder_name}/allocated_plan.py", 'w') as a:
                a.write(allocated_plan[idx])

            with open(f"./logs/{folder_name}/code_plan.py", 'w') as x:
                x.write(code_plan[idx])

            print(f'{task} Plan Stored at "./logs/{folder_name}"')