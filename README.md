
# Enhancing Multi-Agent Robotic Systems with LLM-Driven Coordination
This repository is a course project for the course Win25 CS291I "Introduction to Robotics" at University of California, Santa Barbara.

## Setup
Create a conda environment (or virtualenv):
```
conda create -n smartllm python==3.9
```

Install dependencies:
```
pip install -r requirments.txt
```

## Creating LLM API Key

### For OpenAI
The code relies on OpenAI API. Create an API Key at https://platform.openai.com/.

Create a file named ```api_key.txt``` in the root folder of the project and paste your OpenAI Key in the file. 

<!-- ### for DeepSeek
The code relies on DeepSeek API. Create an API Key at https://deepseek.com/apikey.

Create a file named ```deepseek_api_key.txt``` in the root folder of the project and paste your DeepSeek Key in the file. 

### for Gemini
The code relies on Gemini API. Create an API Key at https://ai.google.dev/gemini-api/docs/quickstart.

Create a file named ```gemini_api_key.txt``` in the root folder of the project and paste your Gemini Key in the file. 

### for Llama
The code relies on Llama API. Create an API Key at https://llama.com/api.

Create a file named ```llama_api_key.txt``` in the root folder of the project and paste your Llama Key in the file.  -->







## Quick Start
Run the following command to run the code. This will generate the plan, execute the plan, and verify the plan. The generated files will be stored in the ```logs``` folder. 

```
python3 scripts/ai2thorCorr_main.py
```

## Running Script
### generate the plan
Run the following command to generate output execuate python scripts to perform the tasks in the given AI2Thor floor plans. 

Refer to https://ai2thor.allenai.org/demo for the layout of various AI2Thor floor plans.
```
python3 scripts/{run_llm.py} --floor-plan {floor_plan_no}
```
Note: Refer to the script for running it on different versions of GPT models and changing the test dataset. 

The above script should generate the executable code and store it in the ```logs``` folder.

### generate the executable code 
Run the following script to execute the above generated scripts and execute it in an AI2THOR environment. 

The script requires command which needs to be executed as parameter. ```command``` needs to be the folder name in the ```logs``` folder where the executable plans generated are stored. 
```
python3 scripts/execute_plan.py --command {command}
```

### run the executable code 
Find the corresponding executable code ```executable_plan.py``` in  ```\logs\*\```.

For example: 
```
python logs/_Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4_03-01-2025-13-56-32/executable_plan.py
```
Once you run the executable code, you suppose to get a ```environment_states.json``` file.

### replan

**TBD** Not yet implement. (replan using LLM and prev_stat of environment)

Generate an updated code in ```logs/{task}/code_replan.py```.

```
python scripts/replan.py --command {}
```

Run the following script to execute the above generated scripts and execute it in an AI2THOR environment. 

The script requires command which needs to be executed as parameter. ```command``` needs to be the folder name in the ```logs``` folder where the executable plans generated are stored. 
```
python3 scripts/execute_plan.py --command {command} --replan
```

Finally, rerun the executable code.
For example: 
```
python logs/_Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4_03-01-2025-13-56-32/executable_plan.py
```
<!-- ## Dataset
The repository contains numerous commands and robots with various skill sets to perform heterogenous robot tasks. 

Refer to ```data\final_test\``` and ```data\tests\``` for the various tasks, robots available for the tasks, and the final state of the environment after the task for evaluation. 

The file name corresponds to the AI2THOR floor plans where the task will be executed. 

Refer to ```resources\robots.py``` for the list of robots used in the final test and the skills possessed by each robot. 
 -->
