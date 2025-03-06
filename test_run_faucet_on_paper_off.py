
----Test set tasks----
['Turn on Sink faucet and put toilet paper in the trash']
Total: 1 tasks

Generating Decompsed Plans...
Generating Allocation Solution...
Generating Allocated Code...
Storing generated plans...
start storing Turn on Sink faucet and put toilet paper in the trash
Turn on Sink faucet and put toilet paper in the trash Plan Stored at "./logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14"
==========
Running experiment 1: Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14
Run  Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14
No Breaks:  1
Finished
Going to  Sink|-02.72|+00.86|+02.23 {'x': -2.648437023162842, 'y': 0.9443130493164062, 'z': 2.2319998741149902}
Going to  ToiletPaper|-02.93|+01.20|+01.46 {'x': -2.927177667617798, 'y': 1.2567285299301147, 'z': 1.4589654207229614}
Reached:  ToiletPaper
PIcking:  ToiletPaper
Picking Up  ToiletPaper|-02.93|+01.20|+01.46 {'x': -2.927177667617798, 'y': 1.2567285299301147, 'z': 1.4589654207229614}
Going to  GarbageCan|-00.40|-00.03|+00.24 {'x': -0.4102923274040222, 'y': 0.29078996181488037, 'z': 0.24096132814884186}
Reached:  GarbageCan
Reached:  Sink
Switching On:  Faucet
Going to  Faucet|-02.93|+00.98|+02.23 {'x': -2.93, 'y': 0.98, 'z': 2.23}
Reached:  Faucet|-02.93|+00.98|+02.23
[{'name': 'Faucet', 'contains': [], 'state': 'ON'}, {'name': 'GarbageCan ', 'contains': ['ToiletPaper'], 'state': 'None'}]
1 1 1
SR:0, TC:0, GCR:0.5, Exec:1.0, RU:1
Execute success.
Attempt 1 of 2: Verify if the task was successful?
Verification result: Task failed. Reason:  The sink faucet is toggled on, but the toilet paper has not been placed in the trash.
==start to replan==
=======
=======
Finished
Run  Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14
No Breaks:  1
Finished
Going to  GarbageCan|-00.40|-00.03|+00.24 {'x': -0.4102923274040222, 'y': 0.29078996181488037, 'z': 0.24096132814884186}
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/Users/xuanhezhou/opt/anaconda3/envs/smartllm/lib/python3.9/threading.py", line 950, in _bootstrap_inner
    self.run()
  File "/Users/xuanhezhou/opt/anaconda3/envs/smartllm/lib/python3.9/threading.py", line 888, in run
    self._target(*self._args, **self._kwargs)
  File "/Users/xuanhezhou/291i/cs291i_w25/logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14/re_executable_plan.py", line 587, in put_toilet_paper_in_trash
    GoToObject(robot, 'GarbageCan')
  File "/Users/xuanhezhou/291i/cs291i_w25/logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14/re_executable_plan.py", line 305, in GoToObject
    robot_name = robot['name']
TypeError: string indices must be integers
Traceback (most recent call last):
  File "/Users/xuanhezhou/291i/cs291i_w25/logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14/re_executable_plan.py", line 614, in <module>
    exec = float(success_exec) / float(total_exec)
ZeroDivisionError: float division by zero
Error in replan: Command '['python', '/Users/xuanhezhou/291i/cs291i_w25/logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14/re_executable_plan.py']' returned non-zero exit status 1.
Attempt 2 of 2: Verify if the task was successful?
Verification result: Task failed. Reason:  The task requires turning on the sink faucet and putting toilet paper in the trash. The sink faucet is toggled on, but the toilet paper has not been put in the trash since the trash still contains toilet paper.
==start to replan==
=======
=======
Finished
Run  Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14
No Breaks:  1
Finished
Going to  GarbageCan|-00.40|-00.03|+00.24 {'x': -0.4102923274040222, 'y': 0.29078996181488037, 'z': 0.24096132814884186}
Exception in thread Thread-2:
Traceback (most recent call last):
  File "/Users/xuanhezhou/opt/anaconda3/envs/smartllm/lib/python3.9/threading.py", line 950, in _bootstrap_inner
    self.run()
  File "/Users/xuanhezhou/opt/anaconda3/envs/smartllm/lib/python3.9/threading.py", line 888, in run
    self._target(*self._args, **self._kwargs)
  File "/Users/xuanhezhou/291i/cs291i_w25/logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14/re_executable_plan.py", line 587, in put_toilet_paper_in_trash
    GoToObject(robot, 'GarbageCan')
  File "/Users/xuanhezhou/291i/cs291i_w25/logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14/re_executable_plan.py", line 305, in GoToObject
    robot_name = robot['name']
TypeError: string indices must be integers
Traceback (most recent call last):
  File "/Users/xuanhezhou/291i/cs291i_w25/logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14/re_executable_plan.py", line 614, in <module>
    exec = float(success_exec) / float(total_exec)
ZeroDivisionError: float division by zero
Error in replan: Command '['python', '/Users/xuanhezhou/291i/cs291i_w25/logs/Turn_on_Sink_faucet_and_put_toilet_paper_in_the_trash_plans_gpt_gpt-4o-mini_03-06-2025-00-14-14/re_executable_plan.py']' returned non-zero exit status 1.
replan for max_attempt 2 times. Failed.