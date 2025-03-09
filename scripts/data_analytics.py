import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
csv_filename = "/Users/xuanhezhou/291i/cs291i_w25/room_states.csv"
df = pd.read_csv(csv_filename)

# Convert numeric columns to float for accurate plotting
df["Success Rate (%)"] = df["Success Rate (%)"].astype(float)
df["Avg Time Per Task (s)"] = df["Avg Time Per Task (s)"].astype(float)

# Group data by Room
room_stats = df.groupby("Room").agg({
    "Success Rate (%)": "mean",
    "Avg Time Per Task (s)": "mean"
}).reset_index()

# Plot 1: Bar chart of success rates per room
plt.figure(figsize=(10, 5))
plt.bar(room_stats["Room"], room_stats["Success Rate (%)"], color="skyblue")
plt.xlabel("Rooms")
plt.ylabel("Success Rate (%)")
plt.title("Success Rate per Room")
plt.ylim(0, 100)  # Success rate is between 0-100%
plt.xticks(rotation=45)  # Rotate labels for readability
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("success_rate_per_room.png")  # Save as an image
plt.show()

# Plot 2: Line chart of average time per task per room
plt.figure(figsize=(10, 5))
plt.plot(room_stats["Room"], room_stats["Avg Time Per Task (s)"], marker="o", linestyle="-", color="red")
plt.xlabel("Rooms")
plt.ylabel("Avg Time Per Task (s)")
plt.title("Average Time Per Task per Room")
plt.xticks(rotation=45)
plt.grid(True, linestyle="--", alpha=0.7)
plt.savefig("avg_time_per_task.png")  # Save as an image
plt.show()
