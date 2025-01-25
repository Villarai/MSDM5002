from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import csv
from datetime import datetime, timedelta

# 设置 ChromeDriver 路径
service = Service('C:/Users/user/Desktop/chromedriver-win32/chromedriver.exe')

# 设置 Chrome 无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 启用无头模式
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 启动浏览器
driver = webdriver.Chrome(service=service, options=chrome_options)

# # 启动浏览器
# driver = webdriver.Chrome(service=service)

# # 打开目标网页
# url = "https://www.hko.gov.hk/en/cis/dailyExtract.htm?y=2024&m=11"
# driver.get(url)

# 初始化日期范围
start_date = datetime(2004, 11, 1)
end_date = datetime(2024, 10, 31)
current_date = start_date

# 用于存储所有数据的列表
all_data = []

try:
    while current_date <= end_date:
        # 构建 URL
        url = f"https://www.hko.gov.hk/en/cis/dailyExtract.htm?y={current_date.year}&m={current_date.month}"
        driver.get(url)

        # 等待表格加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'dataTable'))  # 确保表格元素已加载
        )
        
        # 查找表格
        table = driver.find_element(By.ID, 'dataTable')  # 替换为实际表格 ID
        
        # 提取数据
        rows = table.find_elements(By.TAG_NAME, 'tr')
        # rows = rows[:-2]

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells:
                # 提取第一列（日期）并转换格式
                day = cells[0].text.strip()
                rainfall = cells[8].text.strip()
                if rainfall == "Trace":
                    rainfall = 0.02
                if day:  # 确保有数据
                    try:
                        # 尝试将日期转换为字符串
                        date_str = f"{current_date.year}-{current_date.month:02d}-{int(day):02d}"
                        all_data.append([date_str] + [cell.text.strip() for cell in cells[1:8]] + [rainfall])  # 添加前9列数据
                    except ValueError:
                        # 如果转换失败，跳过该行
                        continue
                    # 构建日期字符串
                    # date_str = f"{current_date.year}-{current_date.month:02d}-{int(day):02d}"

                    # all_data.append([date_str] + [cell.text.strip() for cell in cells[1:8]] + [rainfall])  # 添加前9列数据

        # 移动到下一个月
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)

    # 导出为 CSV 文件
    with open('weather.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)

    print("数据已成功导出为 weather.csv")
except Exception as e:
    print(f"发生错误: {e}")

finally:
    # 关闭浏览器
    driver.quit()