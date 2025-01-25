from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

# 设置 ChromeDriver 路径
service = Service('C:/Users/user/Desktop/chromedriver-win32/chromedriver.exe')

# 启动浏览器
driver = webdriver.Chrome(service=service)

try:
    # 打开目标网页
    url = "https://www.hko.gov.hk/en/wxinfo/climat/warndb/warndb12.shtml"
    driver.get(url)

    # 等待页面加载
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'startdate'))  # 修改为正确的ID
    )

    # 输入年份和月份
    start_date_input = driver.find_element(By.ID, 'startdate')
    end_date_input = driver.find_element(By.ID, 'enddate')

    # 清除输入框中的内容
    start_date_input.clear()
    end_date_input.clear()

    # 设置要查询的起始和结束时间
    start_date = "200411"  # 修改为所需的开始日期
    end_date = "202411"    # 修改为所需的结束日期

    start_date_input.send_keys(start_date)
    end_date_input.send_keys(end_date)

    # 提交查询
    submit_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Submit Query']"))
    )
    submit_button.click()

    # 等待表格加载
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'result'))  # 确保表格元素已加载
    )

    # 查找表格
    table = driver.find_element(By.ID, 'result')

    # 提取数据
    rows = table.find_elements(By.TAG_NAME, 'tr')

    # 用于存储所有数据的列表
    all_data = []

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            # 提取时间和日期，去掉第五列
            time_str = cells[0].text.strip()  # HH MM
            date_str = cells[1].text.strip()  # DD/MON/YYYY
            time_strEnd = cells[2].text.strip()  # HH MM
            date_strEnd = cells[3].text.strip()  # DD/MON/YYYY


            # 转换为 'yyyy-mm-dd hh:mm:ss' 格式
            day, month, year = date_str.split('/')
            dayEnd, monthEnd, yearEnd = date_strEnd.split('/')
            month_num = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }[month]
            month_numEnd = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }[monthEnd]

            hour, minute = time_str.split(':')
            hourEnd, minuteEnd = time_strEnd.split(':')
            datetime_str = f"{year}-{month_num}-{day} {hour}:{minute}:00"
            datetime_strEnd = f"{yearEnd}-{month_numEnd}-{dayEnd} {hourEnd}:{minuteEnd}:00"
            all_data.append([datetime_str] + [datetime_strEnd])

    # 导出为 CSV 文件
    with open('cold.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)

    print("数据已成功导出为 cold.csv")

except Exception as e:
    print(f"发生错误: {e}")
    print(driver.page_source)  # 打印当前页面的HTML内容以调试

finally:
    # 关闭浏览器
    driver.quit()