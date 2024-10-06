import pandas as pd

df = pd.DataFrame({
    'col1': [True, True, False, False],
    'col2': [True, False, True, False],
    'col3': [True, True, True, True]
})

df['col3'] = df.iloc[:, :-1].all(axis=1)

print(df.iloc[:, :-1])
