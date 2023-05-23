"""Script to plot sentence gradients
"""
import matplotlib.pyplot as plt
import json

################################################################################
sentence_gradients = "assets/20221207_223612_sentence_gradients.json"
################################################################################

# load ground truth gradients
with open(sentence_gradients, encoding="utf-8") as f:
  data = json.load(f)

max = 0

# plot all categories
for category, items in data["sentence_gradients"].items():
  for item in items:
    x = [a for a in range(len(item["sentence_gradients"]))]
    y = item["sentence_gradients"]
    plt.plot(x, y)
    if len(item["sentence_gradients"]) > max:
      max = len(item["sentence_gradients"])

x = [a for a in range(max)]
y = [0.02 for a in range(max)]
plt.plot(x, y, label="Gradient Limit")

plt.xlabel("Sentence #")
plt.ylabel("Gradient")

plt.legend()
plt.show()
