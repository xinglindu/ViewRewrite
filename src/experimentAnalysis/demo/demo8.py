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

data3 = {
    'Category': ['I', 'J', 'K', 'L'],
    'Value1': [12, 15, 20, 8],
    'Value2': [6, 11, 16, 9]
}

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)
df3 = pd.DataFrame(data3)

plt.style.use('ggplot')

fig, axs = plt.subplots(2, 2, figsize=(10, 6), sharex=False, sharey=False)


def plot_comparison_bar_chart(ax, df, title):
    x = range(len(df))

    width = 0.4
    ax.bar(x, df['Value1'], width=width, label='Value1')
    ax.bar([pos + width for pos in x], df['Value2'], width=width, label='Value2')

    ax.set_xticks([pos + width / 2 for pos in x])
    ax.set_xticklabels(df['Category'])
    ax.tick_params(axis='x', rotation=0)  # Rotate x-axis labels

    ax.set_xlabel('Category')
    ax.set_ylabel('Value')
    ax.set_title(title)
    ax.legend()


plot_comparison_bar_chart(axs[0, 0], df1, 'Comparison Bar Chart 1')

plot_comparison_bar_chart(axs[0, 1], df2, 'Comparison Bar Chart 2')

plot_comparison_bar_chart(axs[1, 0], df3, 'Comparison Bar Chart 3')

plt.subplots_adjust(wspace=0.3, hspace=0.5)

plt.tight_layout()
plt.show()