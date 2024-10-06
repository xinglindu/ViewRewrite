import pandas as pd
import matplotlib.pyplot as plt

data1 = {
    'Category': ['A', 'B', 'C', 'D'],
    'Value1': [10, 20, 15, 30],
    'Value2': [5, 12, 18, 25]
}

data2 = {
    'Category': ['E', 'F', 'G', 'H'],
    'Value1': [18, 22, 27, 14],
    'Value2': [10, 8, 16, 21]
}

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

plt.style.use('ggplot')

fig, axs = plt.subplots(2, 1, figsize=(8, 10), sharex=True, sharey=True)


def plot_comparison_bar_chart(ax, df, title):
    x = range(len(df))

    width = 0.4
    ax.bar(x, df['Value1'], width=width, label='Value1')
    ax.bar([pos + width for pos in x], df['Value2'], width=width, label='Value2')

    ax.set_xticks([pos + width / 2 for pos in x])
    ax.set_xticklabels(df['Category'])

    ax.set_xlabel('Category')
    ax.set_ylabel('Value')
    ax.set_title(title)
    ax.legend()


plot_comparison_bar_chart(axs[0], df1, 'Comparison Bar Chart 1')

plot_comparison_bar_chart(axs[1], df2, 'Comparison Bar Chart 2')

plt.tight_layout()
plt.show()
