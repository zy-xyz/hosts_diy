import asyncio
import os
import re
from pathlib import Path

class HostsRule:
    def __init__(self, line):
        self.line = line

    def save(self, rules_folder):
        file_path = os.path.join(rules_folder, "host.txt")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{self.line}\n")

class DomainRule:
    def __init__(self, line):
        self.line = line

    def save(self, rules_folder):
        file_path = os.path.join(rules_folder, "domain.txt")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{self.line}\n")

class ModifyRule:
    def __init__(self, line):
        self.line = line

    def save(self, rules_folder):
        file_path = os.path.join(rules_folder, "modify.txt")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{self.line}\n")

class RegexRule:
    def __init__(self, line):
        self.line = line

    def save(self, rules_folder):
        file_path = os.path.join(rules_folder, "regex.txt")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{self.line}\n")

async def process_hosts(download_folder, rules_folder):
    tasks = []
    for file_path in Path(download_folder).glob("*"):
        if file_path.is_file():
            tasks.append(asyncio.create_task(process_file(file_path, rules_folder)))

    await asyncio.gather(*tasks)

async def process_file(file_path, rules_folder):
    print(f"Processing file: {file_path.name}")
    rules = []

    encodings = ["utf-8", "gbk", "latin-1"]
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                for line in f:
                    rule = parse_rule(line)
                    if rule:
                        rules.append(rule)
            break  # 如果成功读取,退出循环
        except UnicodeDecodeError:
            print(f"Error decoding file {file_path.name} with encoding {encoding}")
            continue

    rules_folder_path = Path(rules_folder)
    rules_folder_path.mkdir(exist_ok=True)
    for rule in rules:
        try:
            rule.save(str(rules_folder_path))
        except UnicodeEncodeError:
            print(f"Error encoding rule {rule} in {file_path.name}")

def parse_rule(line):
    line = line.strip()
    if line.startswith("!") or line.startswith("_"):
        return None

    # 处理以 "{" 开头的规则
    if line.startswith("{"):
        try:
            end_index = line.index("}")
            line = line[end_index+1:].strip()
        except ValueError:
            return None

    if line.startswith("||") or line.startswith("@@||") or line.startswith("|") or line.startswith("/") or line.startswith("*/") or line.startswith("@@/") or line.startswith("<") or line.startswith("*")or line.startswith(":"):
        if "$" in line or "#" in line:
            return ModifyRule(line)
        elif line.endswith("^") and "*" not in line:
            return DomainRule(line)
        else:
            return RegexRule(line)
    else:
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            ip, host = parts
            if is_valid_ip(ip):
                return HostsRule(line)
            elif "$" in line or "#" in line:  
                return ModifyRule(line)
               
            # elif is_valid_domain(host):
                # return DomainRule(line)
            else:
                return None
        elif len(parts) == 1:
            if "$" in line or "#" in line or "/" in line :
                return ModifyRule(line)
            elif is_valid_domain(line):
                return DomainRule(line)
            else:
                return None
        else:
            return None

def is_valid_ip(ip):
    try:
        # 检查 IPv4 地址
        parts = ip.split(".")
        if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            return True

        # 检查 IPv6 地址
        parts = ip.split(":")
        if 2 <= len(parts) <= 8:
            # 允许 IPv6 地址中出现 "::"
            if "::" in ip:
                double_colon_count = ip.count("::")
                if double_colon_count > 1:
                    return False
                parts = [part for part in ip.split(":") if part]
                if 2 <= len(parts) <= 8:
                    return all(len(part) <= 4 and all(c.isalnum() for c in part) for part in parts)
            else:
                return all(len(part) <= 4 and all(c.isalnum() for c in part) for part in parts)

        return False
    except ValueError:
        return False

def is_valid_domain(domain):
    parts = domain.split(".")
    for part in parts:
        if 2 <= len(part) <= 6 and part.isalpha():
            return True
    return False
        
async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_folder = os.path.join(script_dir, "downloaded_hosts")
    rules_folder = os.path.join(script_dir, "rules")

    await process_hosts(download_folder, rules_folder)

if __name__ == "__main__":
    asyncio.run(main())