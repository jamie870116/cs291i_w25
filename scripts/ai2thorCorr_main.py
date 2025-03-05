from run_llm import run_llm_main
from execute_plan import execute_plan_main
from replan import replan_main
import subprocess
import openai
from pathlib import Path
import re
import os
import json
api_key_filename = "api_key"

llm_args = {
    "openai_api_key_file": api_key_filename,
    "test_set": "tests",
    "floor_plan": 414,
    "prompt_decompse_set": "train_task_decompose",
    "llm_model": "gpt",
    "gpt_version": "gpt-4o-mini",
    "prompt_allocation_set": "train_task_allocation",
    "log_results": True
}

client = openai.OpenAI(api_key=Path('api_key.txt').read_text())

def call_gpt_fix(error_message, file_path):
    print("Calling GPT-4o-mini to fix the syntax error...")
    
    with open(file_path, "r") as f:
        file_content = f.read()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant robotic developer that fix syntax error by give people the entire code piece after fix without saying anything else"},
            {"role": "user", "content": f"Here is a Python script with a syntax error:\n\n{file_content}\n\nThe error message is: {error_message}\n\nPlease correct the syntax and provide the entire code piece that resolves the error, don't explain anything else, just give me the code."}
        ]
    )
    
    fixed_code = response.choices[0].message.content  # Extract the response
    with open(f"{file_path[:-3]}_fixed.py", "w", encoding='utf-8') as f:
        f.write(fixed_code)
    
    return f'{file_path[:-3]}_fixed.py'


def clean_python_code(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove markdown Python code block markers (```python and ```)
    content = re.sub(r'```(?:python)?\n|\n```', '', content)

    # Remove standalone occurrences of 'python' (case insensitive)
    content = re.sub(r'\bpython\b', '', content, flags=re.IGNORECASE)

    # Replace all occurrences of: exec = float(success_exec) / float(total_exec)
    # With: exec = 0 if total_exec == 0 else float(success_exec) / float(total_exec)
    content = re.sub(
        r'(\bexec\s*=\s*)float\(\s*success_exec\s*\)\s*/\s*float\(\s*total_exec\s*\)',
        r'\1 0 if total_exec == 0 else float(success_exec) / float(total_exec)',
        content
    )

    # Replace all occurrences of robot['name'] with robot
    content = re.sub(r"robot\['name'\]", "robot", content)

    # Write cleaned Python code to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def verify_plan(command_folder):
    # verify if the task is completed
    log_file = open(f"./logs/{command_folder}" + "/log.txt")
    log_data = log_file.readlines()
    task = log_data[0]
    ground_truth = log_data[9]

    
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

        ### ground truth
        {ground_truth}

        ### environment state
        {environment_states}
        
        You should reason over the above information,
        and tell me if the task is complete or not, if not, tell me what is completed and what was not. 
        You should not depend purely on the '''ground truth''' to decide if the task is complete or not, 
        because the gound truth only show the type of objects, it didnot specify the object id, meaning not specific object need to be activated.
        There might be multiple same type of objects in the environment, be tolerant.

        your output should be in the following format in dictionary:
        ## Output Format
        {{
        'isComplete': bool,
        'failure_reason': str of reason why the task is failed,
        'completed_tasks': ['list of completed item', empty list if none],
        'remaining_tasks': ['list of completed item', empty list if none],
        }}
        * Note: only return the json, don't say anything else.
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
    return response


def main():
    '''
    work flow:
    1. generate plan (run_llm_main)。
    2. attemp to execute the plan:
        run execute_plan_main(), clean up
        run generated executable_plan.py; if there is a syntax error, call call_gpt_fix to fix it.
    3. run verify_plan to check if the task is completed:
        if success, end.
        if failed, based on failure_reason to run replan_main
    4. execute the replaned plan:
        run execute_plan_main(replan=True)
    5. run verify_plan again to check if the task is completed:
    '''
    # step 1.
    exec_folders = run_llm_main(llm_args)

    if exec_folders and len(exec_folders) > 0:
        for i in range(len(exec_folders)):
            print("="*10)
            print(f"Running experiment {i+1}: {exec_folders[i]}")
            command_folder = exec_folders[i]

            execute_plan_args = {
                "command": command_folder,
                "replan": False
            }

            replan_args = {
                "command": command_folder,
                "replan": True
            }
            # step 2.
            # Run functions synchronously
            exe_path = execute_plan_main(execute_plan_args)  
        
            executable_plan_path = f"./logs/{command_folder}/executable_plan.py"

            clean_python_code(executable_plan_path, executable_plan_path)
                
            # step3. check if there is a syntax error
            try:
                # Run the executable_plan.py inside the command folder
                subprocess.run(["python", executable_plan_path], check=True)
                print("No syntax error")
                # replan_main(replan_args, "")
                break
            except subprocess.CalledProcessError as e:
                attempt += 1
                error_message = e.stderr if e.stderr else str(e)
                if "SyntaxError" in error_message:
                    print(f"Error executing {executable_plan_path}: {e}")
                    fixed_file_path = call_gpt_fix(str(e), executable_plan_path)
                    clean_python_code(fixed_file_path, executable_plan_path)
                    print("Retrying execution after fixing syntax errors...")
                else:
                    print(f"Non-syntax error encountered in {executable_plan_path}: {e}")
                        

            # step 4.verify whether the task is completed
            verify_result = verify_plan(command_folder)
            if verify_result["isComplete"]:
                print("Task completed successfully")
            else:
                if verify_result['failure_reason'] == "Unknown":
                    print("Task failed")
                    break
                else:
                    # replan based on the failure reason, and execute the plan again from previous step
                    try:
                        replan_path = replan_main(replan_args, verify_result)
                        exe_path = execute_plan_main(replan_args)
                        subprocess.run(["python", exe_path], check=True)
                        # step 5. verify the task again
                        verify_result = verify_plan(command_folder)
                        if verify_result["isComplete"]:
                            print("Task completed successfully")
                        else:
                            print("Task failed")
                        
                    except Exception as e:
                        print(f"Error in replan: {e}")
            # print(response)
    else:
        print("No plan generated")
            
if __name__ == "__main__":
    main()
    
    # error_message = """
    # SyntaxError: invalid syntax
    # Error executing ./logs/Place_the_Bar_of_soap_in_the_sink_first_and_then_place_dishsponge_in_the_sink_plans_gpt_gpt-4o-mini_03-04-2025-17-23-51/executable_plan.py: 
    # Command '['python', './logs/Place_the_Bar_of_soap_in_the_sink_first_and_then_place_dishsponge_in_the_sink_plans_gpt_gpt-4o-mini_03-04-2025-17-23-51/executable_plan.py']' returned non-zero exit status 1.
    # """
    # command_folder = "Place_the_Bar_of_soap_in_the_sink_first_and_then_place_dishsponge_in_the_sink_plans_gpt_gpt-4o-mini_03-04-2025-17-23-51"
    # command_folder = "_Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4_03-03-2025-16-49-11"

    # response = {'isComplete': False, 'completed_tasks': [], 'remaining_tasks': ['Turn on Sink faucet', 'Put toilet paper in the trash']}
    # print(response)
    # is_complete = response["isComplete"]
    # completed_tasks = response["completed_tasks"]
    # remaining_tasks = response["remaining_tasks"]
    # print(is_complete)
    # print(completed_tasks)
    # print(remaining_tasks)

    