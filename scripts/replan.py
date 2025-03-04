import os
from pathlib import Path
import subprocess
import argparse
import json
from openai import OpenAI

client = OpenAI(api_key=Path('api_key.txt').read_text())
def replan_code_file(expt_name):
    log_path = os.getcwd() + "/logs/" + expt_name

    # 读取 "code_plan.py" 的内容
    with open(f"{log_path}/code_plan.py", "r", encoding="utf-8") as f:
        code_plan = f.read()

    # 读取 "environment_states.json" 的内容
    with open(f"{log_path}/environment_states.json", "r", encoding="utf-8") as f:
        environment_states = json.load(f)

    # 组合 prompt
    prompt = f"""
    # Code Plan
    {code_plan}

    # Environment States
    {json.dumps(environment_states, indent=2)}

    # Task
    Based on the above code plan and environment states, generate an improved and executable Python script. Do not output any other content. DO NOT use markdown format.
    """

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

    return (f"{log_path}/code_replan.py")



parser = argparse.ArgumentParser()
parser.add_argument("--command", type=str, required=True)
args = parser.parse_args()

expt_name = args.command
ai_exec_file = replan_code_file(expt_name)
print('Finished')
# subprocess.run(["python", ai_exec_file])