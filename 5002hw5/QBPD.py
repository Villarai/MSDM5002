import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
data = pd.read_csv('weather_with_warnings.csv')

# 将数据分为有高温天气警告和没有高温天气警告的两组
hot_warning = data[data['Very Hot Weather Warning'] == True]
no_hot_warning = data[data['Very Hot Weather Warning'] == False]

# 设置参数列表
parameters = [
    'Mean Pressure',
    'Absolute Daily Max Air Temp.',
    'Mean Air Temp.',
    'Absolute Daily Min Air Temp.',
    'Mean Dew Point',
    'Mean Relative Humidity',
    'Mean Amount of Cloud',
    'Total Rainfall'
]

# 创建2x4的子图
fig, axes = plt.subplots(2, 4, figsize=(15, 10))
axes = axes.flatten()  # 将2D数组展平，方便迭代

# 为每个参数绘制直方图
for i, param in enumerate(parameters):
    axes[i].hist(no_hot_warning[param], bins=20, alpha=0.5, label='No Hot Warning', color='red')
    axes[i].hist(hot_warning[param], bins=20, alpha=0.5, label='Hot Warning', color='blue')

    axes[i].set_title(param)
    axes[i].set_xlabel(param)
    axes[i].set_ylabel('Number of Days')
    axes[i].legend()

# 调整布局
plt.tight_layout()
plt.show()