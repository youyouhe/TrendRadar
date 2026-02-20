# Windows 招标采集客户端 - 使用说明

## 概述

Windows 招标采集客户端允许您在 Windows 机器上采集招标信息，并自动推送到 Linux 服务器上的 TrendRadar 系统。

**架构：**
```
┌─────────────────────┐           ┌─────────────────────┐
│  Windows 客户端      │  推送     │  Linux 服务端        │
│  (采集器)           │ ========> │  (TrendRadar)       │
│                     │  HTTP     │                     │
│  - 采集招标信息      │           │  - 接收推送数据      │
│  - 定时运行         │           │  - 注入到HTML报告    │
│  - 本地备份         │           │  - 生成可视化报告    │
└─────────────────────┘           └─────────────────────┘
```

---

## 一、Linux 服务端配置

### 1.1 启动 TrendRadar API 服务

在 Linux 服务器上运行：

```bash
cd /path/to/TrendRadar

# 启动API服务（接收推送）
./start_api_server.sh
```

服务将监听在 `http://0.0.0.0:8080`，Windows客户端可通过IP地址访问。

### 1.2 验证服务状态

```bash
# 健康检查
curl http://localhost:8080/api/tenders/health

# 预期输出
{
  "status": "ok",
  "service": "tender_push_api",
  "timestamp": "2026-02-20T14:30:00.123456"
}
```

### 1.3 查看API文档

浏览器访问: `http://YOUR_SERVER_IP:8080/docs`

---

## 二、Windows 客户端配置

### 2.1 环境准备

#### 安装 Python

1. 下载 Python 3.8+ : https://www.python.org/downloads/
2. 安装时勾选 **"Add Python to PATH"**
3. 验证安装：
   ```cmd
   python --version
   ```

#### 复制项目文件到 Windows

将以下文件复制到 Windows 机器（如 `C:\TrendRadar\`）：

```
TrendRadar/
├── windows_tender_collector.py    # 采集客户端
├── start_windows_collector.bat    # 启动脚本
├── config/
│   ├── tender_sources.yaml        # 采集源配置
│   └── frequency_words.txt        # 关键词（可选）
├── trendradar/                    # 依赖模块
├── .env                           # 环境变量（DeepSeek API Key）
└── requirements.txt               # Python依赖
```

### 2.2 安装依赖

打开命令提示符（CMD）：

```cmd
cd C:\TrendRadar
pip install -r requirements.txt
```

### 2.3 配置环境变量

编辑 `.env` 文件，添加 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

获取API Key：https://platform.deepseek.com/

### 2.4 配置采集源

编辑 `config/tender_sources.yaml`，启用需要的省份：

```yaml
TENDER_SOURCES:
  - id: beijing
    name: 北京市政府采购网
    url: http://www.ccgp-beijing.gov.cn/
    enabled: true   # ← 设置为 true 启用

  - id: shanghai
    name: 上海市政府采购网
    url: http://www.ccgp-shanghai.gov.cn/
    enabled: true   # ← 启用多个省份

  # 更多省份...
```

### 2.5 配置服务端地址

编辑 `start_windows_collector.bat`，修改服务端地址：

```bat
REM 修改为您的Linux服务器IP
SET SERVER_URL=http://192.168.1.100:8080

REM 修改客户端标识（可选）
SET CLIENT_ID=office_pc
```

---

## 三、运行采集客户端

### 3.1 方式一：双击运行（推荐）

1. 双击 `start_windows_collector.bat`
2. 脚本会自动：
   - 检查Python和依赖
   - 连接服务端
   - 采集招标信息
   - 推送到服务端

### 3.2 方式二：命令行运行

```cmd
cd C:\TrendRadar

# 运行一次（测试用）
python windows_tender_collector.py --server http://192.168.1.100:8080

# 试运行（只采集不推送）
python windows_tender_collector.py --server http://192.168.1.100:8080 --dry-run

# 定时运行（每30分钟）
python windows_tender_collector.py --server http://192.168.1.100:8080 --schedule 30

# 指定客户端ID
python windows_tender_collector.py --server http://192.168.1.100:8080 --client-id my_pc
```

### 3.3 定时运行配置

在 `start_windows_collector.bat` 中设置定时：

```bat
REM 每30分钟运行一次
SET SCHEDULE=30
```

或使用 Windows 任务计划程序：

1. 打开 "任务计划程序"
2. 创建基本任务
3. 触发器：每天或每小时
4. 操作：启动程序
   - 程序：`C:\TrendRadar\start_windows_collector.bat`

---

## 四、验证和监控

### 4.1 查看采集日志

Windows客户端会输出详细日志：

```
========================================
Windows 招标采集客户端 - office_pc
服务端: http://192.168.1.100:8080
时间: 2026-02-20 14:30:00
========================================

✅ 服务端连接正常

🔍 开始采集...
   采集源: 2 个
   关键词: ['软件开发', '信息化', '智慧城市']
   每源数量: 10

[北京市政府采购网] 找到 5 个项目
[上海市政府采购网] 找到 3 个项目

📊 采集结果: 8 条

样本数据（前3条）:
1. [公开]某区信息化建设项目招标公告
   来源: 北京市政府采购网
   预算: 500万

📤 推送到服务端: http://192.168.1.100:8080/api/tenders/push
   数据量: 8 条

✅ 推送成功!
   服务端消息: 成功接收 8 条招标信息
   保存文件: output/tenders/tenders_office_pc_20260220_143000.json
   已触发HTML注入

========================================
✅ 任务完成
========================================
```

### 4.2 查看服务端数据

在 Linux 服务器上：

```bash
# 查看最新推送的数据
curl http://localhost:8080/api/tenders/latest

# 查看推送的JSON文件
ls -lt output/tenders/

# 查看HTML报告
cd output/html
python3 -m http.server 8000
# 浏览器访问: http://YOUR_SERVER_IP:8000/latest/current.html
```

### 4.3 失败处理

如果推送失败，客户端会自动保存本地备份：

```
Windows: C:\TrendRadar\output\tenders_backup\backup_office_pc_20260220_143000.json
```

稍后可手动上传或重新运行。

---

## 五、故障排除

### 5.1 无法连接到服务端

**问题**：`❌ 无法连接到服务端: http://192.168.1.100:8080`

**解决方案**：

1. 检查Linux服务器是否启动：
   ```bash
   curl http://localhost:8080/api/tenders/health
   ```

2. 检查防火墙是否开放8080端口：
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 8080

   # CentOS/RHEL
   sudo firewall-cmd --add-port=8080/tcp --permanent
   sudo firewall-cmd --reload
   ```

3. 检查网络连通性：
   ```cmd
   ping 192.168.1.100
   telnet 192.168.1.100 8080
   ```

### 5.2 采集失败

**问题**：`[北京市政府采购网] 搜索失败: ...`

**解决方案**：

1. 检查 DeepSeek API Key 是否正确（`.env` 文件）

2. 检查网络访问是否正常（代理、防火墙）

3. 启用详细日志：
   ```python
   # 在 windows_tender_collector.py 中添加
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### 5.3 详情页获取失败

**问题**：`ERR_CONNECTION_RESET` 或连接重置

**原因**：政府网站防爬虫限制

**解决方案**：

1. 系统已内置重试机制（自动重试2次）

2. 增加采集间隔：
   ```yaml
   # config/tender_sources.yaml
   TENDER_SETTINGS:
     REQUEST_INTERVAL: 5000  # 增加到5秒
   ```

3. 只采集列表数据（不获取详情）：
   修改 `trendradar/crawler/tender/__init__.py` 中的 `include_details` 参数

---

## 六、进阶配置

### 6.1 自定义关键词

编辑 `config/frequency_words.txt`：

```
[行业关键词]
软件开发
信息化建设
智慧城市
云计算
大数据
```

### 6.2 多客户端部署

如果有多台Windows机器，可以：

1. 分配不同的 `CLIENT_ID`：
   ```bat
   SET CLIENT_ID=office_pc_1
   SET CLIENT_ID=office_pc_2
   ```

2. 分配不同的省份：
   - PC1 采集: 北京、上海、天津
   - PC2 采集: 广东、深圳、浙江

3. 错开采集时间（避免同时推送）

### 6.3 数据去重

服务端会根据 URL 自动去重，同一条招标信息只保存一次。

### 6.4 数据备份

建议定期备份：

```bash
# Linux 服务端
tar -czf tenders_backup_$(date +%Y%m%d).tar.gz output/tenders/

# Windows 客户端
tar -czf tenders_backup_%date:~0,4%%date:~5,2%%date:~8,2%.tar.gz output\tenders_backup\
```

---

## 七、性能优化

### 7.1 采集速度

- 单个省份: ~2-5分钟（10条）
- 5个省份: ~10-20分钟
- DeepSeek API 成本: ~¥0.01-0.05 /次

### 7.2 推送性能

- 推送延迟: <1秒
- HTML注入: <2秒
- 无需等待，后台异步处理

### 7.3 资源占用

- 内存: ~200MB
- CPU: 采集时较高，空闲时很低
- 网络: ~10-50MB /次采集

---

## 八、联系和反馈

- 问题反馈：通过 GitHub Issues
- 功能建议：通过 Pull Request

---

## 九、完整示例

### 场景：办公室Windows电脑，每天采集3次

**步骤：**

1. **准备环境**（一次性）
   ```cmd
   cd C:\TrendRadar
   pip install -r requirements.txt
   ```

2. **配置 `.env`**
   ```env
   DEEPSEEK_API_KEY=sk-xxxxxx
   ```

3. **配置采集源** (`config/tender_sources.yaml`)
   ```yaml
   # 启用北京、上海、深圳
   ```

4. **配置 Windows 任务计划程序**
   - 任务名称: TrendRadar采集器
   - 触发器: 每天 9:00, 14:00, 18:00
   - 操作: 运行 `C:\TrendRadar\start_windows_collector.bat`
   - 设置: 允许手动触发

5. **首次测试**
   ```cmd
   cd C:\TrendRadar
   python windows_tender_collector.py --server http://192.168.1.100:8080 --dry-run
   ```

6. **正式运行**
   - 双击 `start_windows_collector.bat`
   - 或等待任务计划自动运行

7. **验证结果**
   - 浏览器访问: `http://192.168.1.100:8000/latest/current.html`
   - 查看"🏢 招标信息"区域

---

**完成！** 您的Windows采集器现已配置完毕，将自动采集并推送招标信息到TrendRadar系统。
