import pandas as pd
import matplotlib.pyplot as plt

data1 = {
    'Category': ['A', 'B', 'C', 'D'],
    'Value1': [10, 20, 15, 30]
}

data2 = {
    'Category': ['A', 'B', 'C', 'D'],
    'Value2': [5, 12, 18, 25]
}

data3 = {
    'Category': ['A', 'B', 'C', 'D'],
    'Value3': [8, 10, 12, 15]
}

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)
df3 = pd.DataFrame(data3)

plt.style.use('ggplot')

fig, axs = plt.subplots(2, 3, figsize=(15, 10), sharey=True)


def plot_bar_chart(ax, df, title):
    ax.bar(df['Category'], df[df.columns[1]])
    ax.set_xlabel('Category')
    ax.set_ylabel('Value')
    ax.set_title(title)


plot_bar_chart(axs[0, 0], df1, 'DataFrame 1')
plot_bar_chart(axs[0, 1], df2, 'DataFrame 2')
plot_bar_chart(axs[0, 2], df3, 'DataFrame 3')

plt.tight_layout()
plt.show()
