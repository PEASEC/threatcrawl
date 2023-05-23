statistics = {
    "behaviors_ttps": {
        "lowest": 42,
        "highest": 810,
        "average": 270.4,
        "median": 247
    },
    "broad_information": {
        "lowest": 26,
        "highest": 381,
        "average": 137.625,
        "median": 129.5
    },
    "malware_used": {
        "lowest": 29,
        "highest": 1245,
        "average": 246.02777777777777,
        "median": 127.0
    },
    "not_relevant": {
        "lowest": 4,
        "highest": 621,
        "average": 62.27358490566038,
        "median": 44.0
    },
    "vulnerabilities_targeted": {
        "lowest": 30,
        "highest": 701,
        "average": 193.02631578947367,
        "median": 141.5
    }
}

import matplotlib.pyplot as plt
import json

################################################################################
sentence_statistics_file = "assets/20221204_234639_sentence_statistics.json"
################################################################################

with open(sentence_statistics_file, encoding="utf-8") as f:
  data = json.load(f)

stats = data["statistics"]

x = [1, 2, 3, 4, 5]

x_values = []
y_min = []
y_max = []
y = []
averages = []
mediums = []

for cat, item in stats.items():
  x_values.append(cat)
  y_min.append(item["average"] - item["lowest"])
  y_max.append(item["highest"] - item["average"])
  y.append(item["average"])
  averages.append(item["average"])
  mediums.append(item["median"])

plt.errorbar(x, y, yerr=[y_min, y_max], fmt="o", capsize=10, markersize=0)
plt.plot(x, averages, "go", label="average")
plt.plot(x, mediums, "yo", label="medium")
plt.ylabel("Sentences #")

plt.xticks(ticks=x, labels=x_values)
plt.legend()
plt.show()