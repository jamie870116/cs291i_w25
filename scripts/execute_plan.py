import os
from pathlib import Path
import subprocess
import argparse

def append_trans_ctr(allocated_plan):
    brk_ctr = 0
    code_segs = allocated_plan.split("\n\n")
    fn_calls = []
    for cd in code_segs:
        if "def" not in cd and "threading.Thread" not in cd and "join" not in cd and cd[-1] == ")":
            # fn_calls.append(cd)
            brk_ctr += 1
    print ("No Breaks: ", brk_ctr)
    return brk_ctr

# split the replan script into two parts
def split_script(text):
    segments = text.split("### Initialization End")
    result = []
    
    for segment in segments:
        if segment.strip():
            result.append(segment.strip())

    return result

def compile_aithor_exec_file(expt_name, replan=False):
    log_path = os.getcwd() + "/logs/" + expt_name
    
    executable_plan = ""
    
    # append the imports to the file
    import_file = Path(os.getcwd() + "/data/aithor_connect/imports_aux_fn.py").read_text()
    executable_plan += (import_file + "\n")
    # append the list of robots and floor plan number
    log_file = open(log_path + "/log.txt")
    log_data = log_file.readlines()
    # append the robot list
    executable_plan += (log_data[8] + "\n")
    # append the floor number
    flr_no = log_data[4][12:]
    gt = log_data[9]
    executable_plan += ("floor_no = " + flr_no + "\n\n")
    executable_plan += (gt)
    trans = log_data[10][8:]
    executable_plan += ("no_trans_gt = " + trans)
    max_trans = log_data[11][12:]
    executable_plan += ("max_trans = " + max_trans + "\n")
    
    if not replan:
        # append the ai thoe connector and helper fns
        connector_file = Path(os.getcwd() + "/data/aithor_connect/aithor_connect.py").read_text()
        executable_plan += (connector_file + "\n")
        
        # append the allocated plan
        allocated_plan = Path(log_path + "/code_plan.py").read_text()

        brks = append_trans_ctr(allocated_plan)
        executable_plan += (allocated_plan + "\n")
        executable_plan += ("no_trans = " + str(brks) + "\n")

        # append the task thread termination
        terminate_plan = Path(os.getcwd() + "/data/aithor_connect/end_thread.py").read_text()
        executable_plan += (terminate_plan + "\n")
    else:
        # append the ai thoe connector and helper fns
        connector_env_file = Path(os.getcwd() + "/data/aithor_connect/aithor_connect_replan_env.py").read_text()
        connector_util_file = Path(os.getcwd() + "/data/aithor_connect/aithor_connect_replan_util.py").read_text()
        executable_plan += (connector_env_file + "\n")
        
        # get the replan plan
        allocated_plan = Path(log_path + "/code_replan.py").read_text()
        segments = split_script(allocated_plan)
        brks = append_trans_ctr(segments[1])
        # append the initialization part
        executable_plan += (segments[0] + "\n")
        executable_plan += (connector_util_file + "\n")
        # append the replan part
        executable_plan += (segments[1] + "\n")
        executable_plan += ("no_trans = " + str(brks) + "\n")

        # append the task thread termination
        terminate_plan = Path(os.getcwd() + "/data/aithor_connect/end_thread.py").read_text()
        executable_plan += (terminate_plan + "\n")

        
    file_name= ''
    if replan:
        file_name = 're_executable_plan.py'
    else:
        file_name = 'executable_plan.py'
        
    with open(f"{log_path}/{file_name}", 'w') as d:
        d.write(executable_plan)
        
    return (f"{log_path}/{file_name}")

def execute_plan_main(args):
    expt_name = args["command"]
    print('Run ', expt_name)
    if args["replan"]:
        ai_exec_file = compile_aithor_exec_file(expt_name, args["replan"])
    else:
        ai_exec_file = compile_aithor_exec_file(expt_name, False)
    print('Finished')
    return ai_exec_file


# parser = argparse.ArgumentParser()
# parser.add_argument("--command", type=str, required=True)
# parser.add_argument("--replan", action="store_true")
# args = parser.parse_args()

# command
# replanwe