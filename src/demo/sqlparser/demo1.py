import numpy as np

n = 3
m = 5

arrays = []

for i in range(n):
    arr = np.arange(i * m + 1, (i + 1) * m + 1)
    arrays.append(list(arr))
print(arrays)
result = np.vstack(arrays)

print(type(result))
