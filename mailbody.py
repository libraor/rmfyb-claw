import requests
from bs4 import BeautifulSoup


def get_article_links(url): # 获取每个子版面页面的文章标题和链接
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
    # 查找所有的<li>标签（该标签中有文章标题及链接）
        lis = soup.find_all('li')
        # 遍历所有的<li>标签，并打印其文本内容（即文章标题及链接）
        for li in lis:
            # .get_text(strip=True) 方法用于获取标签的文本内容，并去除多余的空白符
            text = li.get_text(strip=True)
            if text:  # 只打印有内容的<li>标签（即文章标题）
                print(text)
            if 'data-src' in li.attrs:  # 检查是否存在属性'data-src'（即文章链接）
                print(url + li.attrs['data-src']) # 输出完整的文章链接'''
    else:
        print(f"请求失败，状态码：{response.status_code}")

def get_layout_links(url):
    # 发送HTTP GET请求以获取网页内容
    response = requests.get(url)
    # 确保请求成功
    if response.status_code == 200:
        html_content = response.text  # 获取网页的HTML内容
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')
        # print(soup) # 打印解析后的HTML内容
        # 查找所有的<div class = directory_item>标签（该标签中有版面标题及链接）
        divs = soup.find_all('div', class_='directory_item')
        for div in divs:
            # .get_text(strip=True) 方法用于获取标签的文本内容，并去除多余的空白符
            text = div.get_text(strip=True)
            if text:  # 只打印有内容的<div>标签（即版面标题）
                print(text)
            if 'href' in div.a.attrs:  # 检查是否存在属性'href'（即版面链接）
                #print(url + div.a.attrs['href']) # 输出完整的版面链接'''
                url2 = url + div.a.attrs['href']
                get_article_links(url2)# 调用函数get_article_links()获取每个子版面页面的文章标题和链接
    else:
        print(f"请求失败，状态码：{response.status_code}")


# 目标网页URL
url = 'https://rmfyb.chinacourt.org'
get_layout_links(url)




