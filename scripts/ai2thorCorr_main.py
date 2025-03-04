from run_llm import run_llm_main
from execute_plan import execute_plan_main
from replan import replan_main
import subprocess
import openai
from pathlib import Path
import re

llm_args = {
    "openai_api_key_file": "api_key",
    "test_set": "tests",
    "floor_plan": 414,
    "prompt_decompse_set": "train_task_decompose",
    "llm_model": "gpt",
    "gpt_version": "gpt-4o-mini",
    "prompt_allocation_set": "train_task_allocation",
    "log_results": True
}

client = openai.OpenAI(api_key=Path('api_key.txt').read_text())  # New API format requires creating a client instance

def call_gpt_fix(error_message, file_path):
    print("Calling GPT-4o-mini to fix the syntax error...")
    
    with open(file_path, "r") as f:
        file_content = f.read()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use "gpt-4o" (not "gpt-4o-mini", as "mini" is not a valid model name)
        messages=[
            {"role": "system", "content": "You are an AI assistant robotic developer that fix syntax error by give people the entire code piece after fix without saying anything else"},
            {"role": "user", "content": f"Here is a Python script with a syntax error:\n\n{file_content}\n\nThe error message is: {error_message}\n\nPlease correct the syntax and provide the entire code piece that resolves the error, don't explain anything else, just give me the code."}
        ]
    )
    
    fixed_code = response.choices[0].message.content  # Extract the response
    
    return fixed_code


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

def main():
    exec_folders = run_llm_main(llm_args)

    if exec_folders and len(exec_folders) > 0:
        command_folder = exec_folders[0]

        execute_plan_args = {
            "command": command_folder,
            "replan": False
        }

        replan_args = {
            "command": command_folder
        }

        # Run functions synchronously
        execute_plan_main(execute_plan_args)  # Step 2
       
        executable_plan_path = f"./logs/{command_folder}/executable_plan.py"

        clean_python_code(executable_plan_path, executable_plan_path)
            

        try:

            # Run the executable_plan.py inside the command folder
            subprocess.run(["python", executable_plan_path], check=True)
            replan_main(replan_args, "")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {executable_plan_path}: {e}")
            syntax_error_suggestion = call_gpt_fix(str(e), executable_plan_path)
            replan_main(replan_args, syntax_error_suggestion)
            print("Retrying execution after fixing syntax errors...")

if __name__ == "__main__":
    main()
