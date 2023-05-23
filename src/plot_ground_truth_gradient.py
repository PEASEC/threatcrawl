"""Script to plot ground truth gradients
"""
import matplotlib.pyplot as plt
import json

################################################################################
ground_truth_gradients_file = "assets/20221207_223612_ground_truth_gradients.json"
################################################################################

# load ground truth gradients
with open(ground_truth_gradients_file, encoding="utf-8") as f:
  data = json.load(f)

# plot all categories
for category, datapoints in data["ground_truth_gradients"].items():
  x = [a for a in range(len(datapoints))]
  y = datapoints
  plt.plot(x, y, label=category)

plt.xlabel("Document #")
plt.ylabel("Gradient")
#plt.title("Ground Truth Gradients")
plt.legend()
plt.show()