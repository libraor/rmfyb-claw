# rmfyb-all

人民法院报（[rmfyb.chinacourt.org](https://rmfyb.chinacourt.org)）每日自动抓取与邮件分发工具。

## 功能

- 抓取当日人民法院报各版面的 PDF 文件
- 合并所有 PDF 为一个文件，按日期命名
- 提取各版面文章标题及链接，生成邮件正文
- 通过 QQ 邮箱将合并后的 PDF 发送给订阅者

## 快速开始

```bash
pip install requests beautifulsoup4 PyPDF2
python main.py
```

## 配置

在项目根目录创建 `pw.py`（已加入 `.gitignore`，不会上传）：

```python
def pw():
    my_sender = 'your-email@qq.com'
    my_pass = 'your-smtp-auth-code'
    my_user = ['recipient1@example.com', 'recipient2@example.com']
    return my_sender, my_pass, my_user
```

QQ 邮箱需开启 SMTP 服务并使用授权码作为密码。

## 目录结构

```
rmfyb-all/
├── main.py           # 主程序
├── mailbody.py       # 邮件正文生成（提取文章标题和链接）
├── pw.py             # 邮箱凭据（需自行创建）
├── downloaded_pdfs/  # 临时下载目录（发送后自动清空）
└── sent_pdfs/        # 已发送的 PDF 存档
```
