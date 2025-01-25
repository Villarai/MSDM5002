import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
data = pd.read_csv('weather_with_warnings.csv')

# 将数据分为有高温天气警告和没有高温天气警告的两组
cold_warning = data[data['Cold Weather Warning'] == True]
no_cold_warning = data[data['Cold Weather Warning'] == False]

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
    axes[i].hist(no_cold_warning[param], bins=20, alpha=0.5, label='No Cold Warning', color='red')
    axes[i].hist(cold_warning[param], bins=20, alpha=0.5, label='Cold Warning', color='blue')

    axes[i].set_title(param)
    axes[i].set_xlabel(param)
    axes[i].set_ylabel('Number of Days')
    axes[i].legend()

# 调整布局
plt.tight_layout()
plt.show()