import requests  
from bs4 import BeautifulSoup  
from urllib.parse import urljoin
import os
import PyPDF2
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import shutil
from pw import pw #pw.py是邮箱账号密码，不上传到github

# 获取每个子版面页面的文章标题和链接
def get_article_links(url):
    articles = []
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        lis = soup.find_all('li')
        for li in lis:
            text = li.get_text(strip=True)
            if text and 'data-src' in li.attrs:
                articles.append(f"{text}\n{urljoin(url, li.attrs['data-src'])}\n")
    else:
        print(f"请求失败，状态码：{response.status_code}")
    return articles

# 获取每个版面页面的标题和链接
def get_layout_links(url):
    articles = []
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        divs = soup.find_all('div', class_='directory_item')
        for div in divs:
            if 'href' in div.a.attrs:
                url2 = urljoin(url, div.a.attrs['href'])
                section_articles = get_article_links(url2)
                if section_articles:
                    articles.extend(section_articles)
    else:
        print(f"请求失败，状态码：{response.status_code}")
    return '\n'.join(articles)

# 下载PDF文件的函数  
def download_pdf(url, filename):
    """下载PDF文件到指定文件名"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        else:
            raise Exception(f"Failed to download PDF from {url}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error downloading {url}: {e}")  

def merge_pdfs(paths, output):# 合并PDF文件到指定路径
    pdf_writer = PyPDF2.PdfWriter()

    for path in sorted(paths):  # 按文件名排序
        pdf_reader = PyPDF2.PdfReader(path)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    with open(output, 'wb') as out:
        pdf_writer.write(out)


def rename(download_folder): # 合并PDF文件并重命名为当前日期
    # 获取下载文件夹中所有的PDF文件
    pdf_files = [os.path.join(download_folder, f) for f in os.listdir(download_folder) if f.lower().endswith(('.pdf', '.pdf_'))]

    # 获取当前日期并格式化
    current_date = datetime.now().strftime('%Y-%m-%d')
    output_filename = f"{current_date}_merged.pdf"

    # 合并PDF文件
    merge_pdfs(pdf_files, os.path.join(download_folder, output_filename))

    print(f"合并完成，文件已保存为：{os.path.join(download_folder, output_filename)}")

def send_email_with_attachment(sender, password, recipient, subject, body, file_path):
    try:
        # 创建一个带附件的 email 消息实例
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain'))

        # 添加附件
        with open(file_path, "rb") as attachment_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment_file).read())
            encoders.encode_base64(part)
            attachment_filename = os.path.basename(file_path)
            part.add_header('Content-Disposition', f"attachment; filename= {attachment_filename}")
        msg.attach(part)

        # 发送邮件
        server = smtplib.SMTP_SSL('smtp.qq.com')  
        server.login(sender, password)  
        text = msg.as_string()
        server.sendmail(sender, recipient.split(','), text)
        server.quit()
        print(f"Succeed to send email")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")

def move_file_to_sent_folder(sent_folder, file_path):
    """将文件移动到已发送文件夹"""
    sent_file_path = os.path.join(sent_folder, os.path.basename(file_path))
    shutil.move(file_path, sent_file_path)
    print(f"文件已移动到已发送文件夹: {sent_file_path}")

def clean_download_folder(download_folder):
    """清空下载文件夹"""
    for filename in os.listdir(download_folder):
        file_path = os.path.join(download_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"删除文件时出错: {e}")
    print(f"下载文件夹 {download_folder} 已清空")

# 拆分原有的 move_file_and_clean_folder 函数
def handle_email_and_folders(sender, password, recipient, subject, body, file_path, sent_folder, download_folder):
    if send_email_with_attachment(sender, password, recipient, subject, body, file_path):
        move_file_to_sent_folder(sent_folder, file_path)
        clean_download_folder(download_folder)
    else:
        print("邮件发送失败")


'''
主程序开始
'''

# 需抓取的网页URL  
url = 'https://rmfyb.chinacourt.org'  
  
# 存放下载PDF的文件夹  
download_folder = 'downloaded_pdfs'  
if not os.path.exists(download_folder):  
    os.makedirs(download_folder)  

# 存放已发送PDF的文件夹
sent_folder = 'sent_pdfs'  
if not os.path.exists(sent_folder):  
    os.makedirs(sent_folder)  

# 发送HTTP GET请求  
response = requests.get(url)  
  
# 使用BeautifulSoup解析HTML内容  
soup = BeautifulSoup(response.text, 'html.parser')  
  
# 查找所有PDF链接
pdf_links = [a['href'] for a in soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))]  
  
# 遍历PDF链接并下载
for link in pdf_links:
    # 构建完整的PDF URL
    full_link = urljoin(url, link)  # 使用urljoin确保URL拼接正确
  
    # 生成本地文件名
    filename = os.path.join(download_folder, os.path.basename(full_link))
  
    # 下载PDF文件
    try:
        download_pdf(full_link, filename)
    except requests.exceptions.RequestException as e:  # 处理网络请求异常
        print(f"Error downloading {full_link}: {e}")

# 合并PDF文件并重命名为当前日期
rename(download_folder)

# 生成邮件正文内容
body = get_layout_links(url)

# 发送邮件参数
sender, password, recipient = pw()  # 传入发件邮箱、密码、收件邮箱
recipient = ','.join(recipient)  # 将收件人列表转换为逗号分隔的字符串
subject = f"{datetime.now().strftime('%Y-%m-%d')}人民法院报"
file_path = os.path.join(download_folder, f"{datetime.now().strftime('%Y-%m-%d')}_merged.pdf")


# 发送并移动文件
handle_email_and_folders(sender, password, recipient, subject, body, file_path, sent_folder, download_folder)
del sender, password, recipient #删除敏感信息

#下一步计划
# 1.生成当日人民法院报各版面的文章标题，并附上链接，与邮件一起发送(完成)
# 2.增加版面信息
