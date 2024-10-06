import matplotlib.pyplot as plt
import numpy as np

data1 = np.array([5, 15, 10, 8, 12])
data2 = np.array([10, 8, 6, 4, 2])
data3 = np.array([3, 6, 9, 12, 15])

fig, axs = plt.subplots(3, 1, figsize=(8, 12), sharex=False)

x1 = np.arange(len(data1))
axs[0].bar(x1, data1, color='blue')
axs[0].set_ylabel('Data 1')
axs[0].set_title('Bar Chart 1')

x2 = np.arange(len(data2))
axs[1].bar(x2, data2, color='green')
axs[1].set_ylabel('Data 2')
axs[1].set_title('Bar Chart 2')

x3 = np.arange(len(data3))
axs[2].bar(x3, data3, color='red')
axs[2].set_ylabel('Data 3')
axs[2].set_title('Bar Chart 3')

plt.suptitle('Multiple Bar Charts', fontsize=16)
plt.xticks(np.arange(len(data1)), ['A', 'B', 'C', 'D', 'E'])

plt.tight_layout()

plt.show()
