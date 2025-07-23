import requests
from lxml import etree
import json
import time
import pandas as pd

BASE_URL = 'https://src.sjtu.edu.cn'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Cookie': '改为自己的cookie'
}

def get_school_list(page_num):
    url = f'{BASE_URL}/rank/firm/0/?page={page_num}'
    resp = requests.get(url, headers=headers)
    tree = etree.HTML(resp.text)

    rows = tree.xpath('//tr[td[2]/a]')
    schools = []
    for row in rows:
        name = row.xpath('./td[2]/a/text()')[0].strip()
        href = row.xpath('./td[2]/a/@href')[0].strip()
        full_url = BASE_URL + href
        schools.append((name, full_url))
    return schools

def parse_school_detail(school_name, detail_url):
    resp = requests.get(detail_url, headers=headers)
    tree = etree.HTML(resp.text)

    json_text = tree.xpath('//script[@id="rose_pie_chart_data"]/text()')
    if not json_text:
        print(f"[跳过] {school_name} 没有漏洞数据")
        return []

    try:
        data = json.loads(json_text[0])
        return [{'学校名称': school_name, '漏洞类型': item['name'], '漏洞数量': item['value']} for item in data]
    except Exception as e:
        print(f"[错误] {school_name} JSON 解析失败：{e}")
        return []


all_data = []

#自行更改抓取的页面
for page in range(1, 3):
    print(f"\n正在抓取第 {page} 页学校数据...")
    school_list = get_school_list(page)
    for name, url in school_list:
        result = parse_school_detail(name, url)
        if result:
            all_data.extend(result)
        time.sleep(1)

# 保存为 Excel
df = pd.DataFrame(all_data)
df.to_excel('漏洞统计.xlsx', index=False)
print("\n 所有数据已保存到 漏洞统计.xlsx")
