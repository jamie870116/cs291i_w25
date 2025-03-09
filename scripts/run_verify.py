import os
import csv
from verify import verify_plan

root_dir = "/Users/xuanhezhou/291i/cs291i_w25/final_exp"
files = os.listdir(root_dir)
response = {}

# Process directories only (skip .DS_Store and non-directory files)
for entry in files:
    full_path = os.path.join(root_dir, entry)
    if not os.path.isdir(full_path) or entry == ".DS_Store":
        continue  # Skip invalid files

    response[entry] = {}
    subdirs = [d for d in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, d))]

    for subdir in subdirs:
        plan_result = verify_plan(os.path.join(full_path, subdir))
        response[entry][subdir] = plan_result
        response[entry][subdir]['timeSpent'] = plan_result.get('timeSpent', 0)  # Store execution time


def extract_task_name(task_string):
    """ Extracts the correct task name from a complex task string. """
    task_name = "".join(char if char.isalpha() or char == "_" else " " for char in task_string).strip()
    if "_gpt" in task_name:
        task_name = task_name.split("_gpt")[0]
    return task_name


def calculate_success_rate(data):
    room_stats = {}
    total_tasks = 0
    total_successful_tasks = 0
    total_time_spent = 0
    total_time_successful = 0  # Total time spent on completed tasks

    task_summary = {}

    for room, tasks in data.items():
        if room == ".DS_Store" or not isinstance(tasks, dict):
            continue

        room_total_tasks = 0
        room_successful_tasks = 0
        room_time_spent = 0
        room_task_counts = {}
        room_task_successes = {}
        room_task_times = {}

        for task_name, task_details in tasks.items():
            if not isinstance(task_details, dict):
                continue

            is_complete = task_details.get("isComplete", False)
            time_spent = task_details.get("timeSpent", 0)
            task_key = extract_task_name(task_name)

            room_task_counts[task_key] = room_task_counts.get(task_key, 0) + 1
            room_task_times[task_key] = room_task_times.get(task_key, 0) + time_spent

            if is_complete:
                room_successful_tasks += 1
                room_task_successes[task_key] = room_task_successes.get(task_key, 0) + 1
                total_time_successful += time_spent  # Track time spent only on successful tasks

            room_time_spent += time_spent
            room_total_tasks += 1

            # Update overall task summary
            if task_key not in task_summary:
                task_summary[task_key] = {"total": 0, "completed": 0, "total_time": 0}

            task_summary[task_key]["total"] += 1
            task_summary[task_key]["total_time"] += time_spent

            if is_complete:
                task_summary[task_key]["completed"] += 1

        total_tasks += room_total_tasks
        total_successful_tasks += room_successful_tasks
        total_time_spent += room_time_spent

        room_stats[room] = {
            "success_rate": (room_successful_tasks / room_total_tasks) * 100 if room_total_tasks else 0,
            "total_tasks": room_total_tasks,
            "successful_tasks": room_successful_tasks,
            "total_time_spent": room_time_spent,
            "avg_time_per_task": (room_time_spent / room_total_tasks) if room_total_tasks else 0,
            "task_success_rates": {
                task: {
                    "completed": room_task_successes.get(task, 0),
                    "total": count,
                    "rate": (room_task_successes.get(task, 0) / count) * 100 if count else 0,
                    "total_time": room_task_times.get(task, 0),
                    "avg_time": (room_task_times.get(task, 0) / count) if count else 0
                }
                for task, count in room_task_counts.items()
            }
        }

    # Compute overall success rate and average task completion time
    total_success_rate = (total_successful_tasks / total_tasks) * 100 if total_tasks else 0
    avg_time_successful_tasks = (total_time_successful / total_successful_tasks) if total_successful_tasks else 0

    overall_stats = {
        "total_tasks": total_tasks,
        "total_successful_tasks": total_successful_tasks,
        "total_time_spent": total_time_spent,
        "total_success_rate": total_success_rate,
        "avg_time_successful_tasks": avg_time_successful_tasks,
        "task_summary": {
            task: {
                "completed": details["completed"],
                "total": details["total"],
                "rate": (details["completed"] / details["total"]) * 100 if details["total"] else 0,
                "total_time": details["total_time"],
                "avg_time": (details["total_time"] / details["total"]) if details["total"] else 0
            }
            for task, details in task_summary.items()
        }
    }

    return room_stats, overall_stats


# Compute success rates
room_success_rates, overall_stats = calculate_success_rate(response)

# Save results to CSV
csv_filename = "room_states.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)

    # Write CSV headers
    writer.writerow([
        "Room", "Success Rate (%)", "Total Tasks", "Successful Tasks",
        "Total Time Spent (s)", "Avg Time Per Task (s)",
        "Task Name", "Task Success Rate (%)", "Completed Tasks",
        "Total Attempts", "Task Total Time (s)", "Avg Task Time (s)"
    ])

    # Write room-level stats and task breakdowns
    for room, stats in room_success_rates.items():
        for task, details in stats["task_success_rates"].items():
            writer.writerow([
                room,
                f"{stats['success_rate']:.2f}",
                stats["total_tasks"],
                stats["successful_tasks"],
                f"{stats['total_time_spent']:.6f}",
                f"{stats['avg_time_per_task']:.6f}",
                task,
                f"{details['rate']:.2f}",
                details["completed"],
                details["total"],
                f"{details['total_time']:.6f}",
                f"{details['avg_time']:.6f}"
            ])

    # Write overall summary
    writer.writerow([])
    writer.writerow(["Overall Summary"])
    writer.writerow(["Total Success Rate (%)", "Total Tasks", "Successful Tasks",
                     "Total Time Spent (s)", "Avg Time Successful Tasks (s)"])
    writer.writerow([
        f"{overall_stats['total_success_rate']:.2f}",
        overall_stats["total_tasks"],
        overall_stats["total_successful_tasks"],
        f"{overall_stats['total_time_spent']:.6f}",
        f"{overall_stats['avg_time_successful_tasks']:.6f}"
    ])

    # Write task summary
    writer.writerow([])
    writer.writerow(["Task Summary"])
    writer.writerow(["Task Name", "Task Success Rate (%)", "Completed Tasks",
                     "Total Attempts", "Task Total Time (s)", "Avg Task Time (s)"])
    for task, details in overall_stats["task_summary"].items():
        writer.writerow([
            task,
            f"{details['rate']:.2f}",
            details["completed"],
            details["total"],
            f"{details['total_time']:.6f}",
            f"{details['avg_time']:.6f}"
        ])

print(f"CSV file '{csv_filename}' has been generated successfully!")
