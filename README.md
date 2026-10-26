# RouterOS Adlist (Clash geosite:category-ads-all)

基于 Clash / MetaCubeX 及 Loyalsoldier 的 `geosite:category-ads-all` 与广告拦截规则，专门为 MikroTik RouterOS (v7+) 优化的 DNS Adlist 订阅源。

每日通过 GitHub Actions 自动更新，具备严格的安全注入清洗机制，将所有广告域名重定向至本机环回地址 `127.0.0.1`。

---

## 订阅地址 (Raw URL)

你可以直接在 RouterOS 中使用以下原始链接：

### 1. Hosts 格式（推荐，RouterOS v7 官方 Adlist 格式）
```text
https://raw.githubusercontent.com/yaolovelive/routeros-adlist/main/hosts.txt
```

### 2. 纯域名列表格式
```text
https://raw.githubusercontent.com/yaolovelive/routeros-adlist/main/domains.txt
```

---

## 安全清洗机制（Anti-Injection）

为了防止上游恶意投毒或意外的语法注入导致 RouterOS 异常，生成脚本执行了以下清洗过滤：

1. **IP 固定**：所有广告拦截 IP 统一且强制映射为本机回环 `127.0.0.1`，消除第三方中间人与外部探测风险。
2. **字符过滤**：剔除任何包含 Shell / ROS CLI 特殊字符（如 `;`、`$`、`` ` ``、`{}`、`[]`、`\`、`|`、`&` 等）的异常行。
3. **格式严格校验**：符合 RFC 1035 / RFC 1123 规范的标准 FQDN 域名格式。
4. **核心服务白名单保护**：内置 MikroTik 官方服务（`mikrotik.com`、`upgrade.mikrotik.com`、`cloud.mikrotik.com` 等）及主流互联网基础域名白名单，杜绝误拦截。

---

## RouterOS v7 配置方式

### 方式一：Winbox 图形界面配置
1. 打开 Winbox，进入 `IP` -> `DNS`。
2. 切换到 `Adlist` 标签页，点击 `+`。
3. 在 `Url` 处填入：
   ```text
   https://raw.githubusercontent.com/yaolovelive/routeros-adlist/main/hosts.txt
   ```
4. 点击 `OK`，RouterOS 会自动下载并在内存中构建哈希匹配表。

### 方式二：Terminal 命令行配置
```routeros
/ip dns adlist add url="https://raw.githubusercontent.com/yaolovelive/routeros-adlist/main/hosts.txt"
```

---

## 更新频率

- 每天 UTC 03:00（北京时间 11:00）自动抓取上游最新规则并构建。
