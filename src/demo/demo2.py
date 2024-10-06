import pandas as pd

data = {'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'age': [25, 32, 18, 47],
        'gender': ['F', 'M', 'M', 'M'],
        'city': ['New York', 'Paris', 'London', 'Tokyo']}
df1 = pd.DataFrame(data)

df2 = df1

df2.iloc[0, 0] = 'Alice Smith'

print(df1)
print(df2)
