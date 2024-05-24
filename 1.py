import os
import requests
from urllib.parse import urlparse

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 指定 TXT 文件路径
txt_file = os.path.join(script_dir, "links.txt")

# 创建子文件夹
subfolder = os.path.join(script_dir, "downloaded_hosts")
if not os.path.exists(subfolder):
    os.makedirs(subfolder)

# 读取 TXT 文件中的链接和注释
links_and_comments = []
with open(txt_file, "r") as f:
    for line in f:
        line = line.strip()
        if line:
            # 分割链接和注释
            parts = line.split("#")
            link = parts[0].strip()
            comment = parts[1].strip() if len(parts) > 1 else ""
            links_and_comments.append((link, comment))

# 处理每个链接和注释
for link, comment in links_and_comments:
    try:
        # 下载远程 hosts 文件
        response = requests.get(link)
        response.raise_for_status()

        # 提取文件名和扩展名
        parsed_url = urlparse(link)
        filename = os.path.basename(parsed_url.path)
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".txt"  # 如果没有扩展名，默认使用 .txt
        if comment:
            filename = f"{comment}{ext}"
        else:
            filename = f"{name}{ext}"

        local_path = os.path.join(subfolder, filename)

        # 保存文件到本地
        with open(local_path, "wb") as f:
            f.write(response.content)

        print(f"Successfully downloaded {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {link}: {e}")