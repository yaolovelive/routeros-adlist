#!/usr/bin/env python3
import sys
import os
import re
import urllib.request
import datetime

# 严格的域名合法性校验正则 (RFC 1035 / RFC 1123)
DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$"
)

# 危险字符黑名单（防止任何脚本注入、命令执行、配置破坏）
DANGEROUS_CHARS_RE = re.compile(r"[\r\n;\`\$\<\>\"\'\\\|\&\(\)\{\}\[\]\*\?\^\~\!\@\#\%\=\+\,\/\:\ ]")

# 重点核心保护列表（白名单）：防止误伤关键解析
CRITICAL_WHITELIST = {
    "localhost",
    "mikrotik.com",
    "upgrade.mikrotik.com",
    "cloud.mikrotik.com",
    "licensing.mikrotik.com",
    "github.com",
    "githubusercontent.com",
    "cloudflare.com",
    "apple.com",
    "google.com",
    "microsoft.com",
    "baidu.com",
    "qq.com",
    "alipay.com",
    "taobao.com",
    "jd.com",
    "bilibili.com"
}

SOURCES = [
    # Loyalsoldier clash reject rule payload (geosite:category-ads-all + reject)
    "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/reject-list.txt",
    # MetaCubeX category-ads-all
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ads-all.list"
]

def clean_domain(raw_line: str) -> str:
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return ""
    
    # 过滤 payload 格式如 - '+.example.com' 或 - 'example.com'
    if line.startswith("-"):
        line = line.lstrip("-").strip()
    line = line.strip("'\"")
    
    # 过滤 clash / v2ray 常见的通配前缀 +. 或 . 或 full: 或 domain:
    if line.startswith("+."):
        line = line[2:]
    elif line.startswith("."):
        line = line[1:]
    elif line.startswith("full:"):
        line = line[5:]
    elif line.startswith("domain:"):
        line = line[7:]
    
    line = line.strip().lower()
    return line

def is_valid_domain(domain: str) -> bool:
    if not domain or len(domain) > 253:
        return False
    if DANGEROUS_CHARS_RE.search(domain):
        return False
    if not DOMAIN_RE.match(domain):
        return False
    if domain in CRITICAL_WHITELIST:
        return False
    return True

def fetch_and_build():
    domains = set()
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RouterOS-Adlist-Generator/1.0)"}
    
    for url in SOURCES:
        print(f"Fetching {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                for line_bytes in resp:
                    raw_str = line_bytes.decode("utf-8", errors="ignore")
                    domain = clean_domain(raw_str)
                    if is_valid_domain(domain):
                        domains.add(domain)
        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            raise e

    sorted_domains = sorted(list(domains))
    print(f"Total valid unique domains: {len(sorted_domains)}")
    
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    header_text = (
        f"# Title: RouterOS Adlist (Clash geosite:category-ads-all)\n"
        f"# Last updated: {now_utc}\n"
        f"# Total rules: {len(sorted_domains)}\n"
        f"# Redirection: 127.0.0.1 (Loopback / Anti-Injection Sanitized)\n"
        f"#\n"
    )
    
    # 1. 生成标准的 hosts.txt 格式 (127.0.0.1 domain)
    # 适用于 RouterOS v7 的 /ip/dns/adlist
    with open("hosts.txt", "w", encoding="utf-8") as f:
        f.write(header_text)
        for d in sorted_domains:
            f.write(f"127.0.0.1 {d}\n")
            
    # 2. 生成纯域名列表 domains.txt
    with open("domains.txt", "w", encoding="utf-8") as f:
        f.write(f"# RouterOS Adlist Domains\n# Updated: {now_utc}\n# Total: {len(sorted_domains)}\n")
        for d in sorted_domains:
            f.write(f"{d}\n")

if __name__ == "__main__":
    fetch_and_build()
