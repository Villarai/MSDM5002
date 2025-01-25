import pandas as pd

# 读取CSV文件
weather_df = pd.read_csv('weather.csv', header=None)
hot_df = pd.read_csv('hot.csv', header=None)
cold_df = pd.read_csv('cold.csv', header=None)

# 重命名列
weather_df.columns = ['Date', 'Mean Pressure', 'Absolute Daily Max Air Temp.', 'Mean Air Temp.', 'Absolute Daily Min Air Temp.', 'Mean Dew Point', 'Mean Relative Humidity', 'Mean Amount of Cloud', 'Total Rainfall']
hot_df.columns = ['Hot_Start', 'Hot_End']
cold_df.columns = ['Cold_Start', 'Cold_End']

# 转换日期格式
weather_df['Date'] = pd.to_datetime(weather_df['Date'])
hot_df['Hot_Start'] = pd.to_datetime(hot_df['Hot_Start'])
hot_df['Hot_End'] = pd.to_datetime(hot_df['Hot_End'])
cold_df['Cold_Start'] = pd.to_datetime(cold_df['Cold_Start'])
cold_df['Cold_End'] = pd.to_datetime(cold_df['Cold_End'])

# 初始化新列
weather_df['Very Hot Weather Warning'] = False
weather_df['Cold Weather Warning'] = False

# 标记Very Hot Weather Warning
for _, row in hot_df.iterrows():
    mask = (weather_df['Date'] >= row['Hot_Start']) & (weather_df['Date'] <= row['Hot_End'])
    weather_df.loc[mask, 'Very Hot Weather Warning'] = True

# 标记Cold Weather Warning
for _, row in cold_df.iterrows():
    mask = (weather_df['Date'] >= row['Cold_Start']) & (weather_df['Date'] <= row['Cold_End'])
    weather_df.loc[mask, 'Cold Weather Warning'] = True

# 保存结果
weather_df.to_csv('weather_with_warnings.csv', index=False)