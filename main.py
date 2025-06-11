import os
import yaml
import requests
from urllib.parse import urlparse

# 输入输出文件路径
input_yaml = "config/bookmarks.googleicon.yaml"
output_yaml = "config/bookmarks.localicon.yaml"
icon_dir = "icons"

os.makedirs(icon_dir, exist_ok=True)


def get_icon_filename(icon_url):
    # 取域名.png
    u = urlparse(icon_url)
    # 支持 api.iowen.cn/favicon/xxx.png 及 google favicon
    domain = os.path.basename(u.path)
    return domain


def download_icon(icon_url, filename):
    try:
        resp = requests.get(icon_url, timeout=10)
        if resp.status_code == 200 and resp.content:
            with open(filename, "wb") as f:
                f.write(resp.content)
            return True
        return False
    except Exception as e:
        print(f"下载失败: {icon_url} -> {e}")
        return False


def process_item(item):
    if isinstance(item, list):
        return [process_item(i) for i in item]
    if isinstance(item, dict):
        new_dict = {}
        for k, v in item.items():
            if k == "icon" and v and v.endswith(".png"):
                icon_file = get_icon_filename(v)
                local_path = os.path.join(icon_dir, icon_file)
                # 下载
                if not os.path.exists(local_path):
                    print(f"正在下载: {v} -> {local_path}")
                    download_icon(v, local_path)
                new_dict[k] = f"/icons/{icon_file}"
            elif isinstance(v, (dict, list)):
                new_dict[k] = process_item(v)
            else:
                new_dict[k] = v
        return new_dict
    return item


with open(input_yaml, "r", encoding="utf-8") as f:
    data = list(yaml.safe_load_all(f))

fixed_data = [process_item(block) for block in data]

with open(output_yaml, "w", encoding="utf-8") as f:
    yaml.dump_all(fixed_data, f, allow_unicode=True, sort_keys=False)

print("全部完成！图标已下载到 icons 目录，新文件输出到:", output_yaml)
