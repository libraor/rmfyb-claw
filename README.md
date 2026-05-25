# rmfyb-all

人民法院报（[www.rmfyb.com](https://www.rmfyb.com)）每日自动抓取与邮件分发工具。

## 功能

- 抓取当日人民法院报各版面的 PDF 文件
- 合并所有 PDF 为一个文件，按日期命名
- 压缩 PDF 体积以适配邮件附件大小限制
- 提取各版面文章标题及链接，生成邮件正文
- 通过 QQ 邮箱将合并后的 PDF 发送给订阅者

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

## 依赖

- `requests` — HTTP 请求
- `beautifulsoup4` — HTML 解析
- `PyPDF2` — PDF 合并
- `PyMuPDF` — PDF 压缩

## 配置

复制 `pw.example.py` 为 `pw.py`（已加入 `.gitignore`，不会上传），填写真实邮箱凭据：

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
├── pw.example.py     # 邮箱凭据示例（复制为 pw.py 后填写真实信息）
├── pw.py             # 邮箱凭据（需自行创建，已加入 .gitignore）
├── requirements.txt  # Python 依赖
├── downloaded_pdfs/  # 临时下载目录（发送后自动清空）
└── sent_pdfs/        # 已发送的 PDF 存档
```

## 执行流程

1. 清空临时下载目录
2. 抓取网站首页，找到所有 PDF 链接并下载
3. 合并所有 PDF 为 `YYYY-MM-DD_merged.pdf`
4. 压缩 PDF 体积（使用 PyMuPDF 渲染为 120 DPI 图片）
5. 遍历各版面提取文章标题和链接，生成邮件正文
6. 通过 QQ SMTP 发送带附件的邮件
7. 成功后将压缩 PDF 移至 `sent_pdfs/`，清空临时目录
