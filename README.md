# 📤 Wireless Transfer

> Wireless file transfer tool for Windows · 方便从苹果手机传输文件到 Windows 电脑

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://github.com/brone2018/wireless-transfer)
[![Release](https://img.shields.io/badge/Release-v1.0.1-green.svg)](https://github.com/brone2018/wireless-transfer/releases/tag/v1.0.1)

Wireless Transfer 是一个轻量级的 Windows 桌面工具，通过本地 Wi-Fi 网络，让 iPhone（或其他智能手机）无需数据线、无需安装客户端，即可将照片、视频、文件无线传输到电脑。

扫描二维码即可在手机浏览器中打开上传页面，选择文件后一键上传到 PC 指定目录。

---

## 📑 目录

- [✨ 功能特性](#-功能特性)
- [🧩 技术栈](#-技术栈)
- [🏗 工作原理 / 架构](#-工作原理--架构)
- [📁 项目结构](#-项目结构)
- [⚙️ 环境要求](#️-环境要求)
- [🚀 快速开始](#-快速开始)
- [📖 使用说明](#-使用说明)
- [🔧 配置说明](#-配置说明)
- [🌐 API 接口文档](#-api-接口文档)
- [📦 打包说明（PyInstaller）](#-打包说明pyinstaller)
- [🔒 安全说明](#-安全说明)
- [❓ 常见问题](#-常见问题)
- [🤝 贡献](#-贡献)
- [📄 许可证](#-许可证)

---

## ✨ 功能特性

| 特性 | 说明 |
| --- | --- |
| 📶 纯局域网传输 | 不依赖外网云盘，文件全程不出本地 Wi-Fi，速度快、隐私安全 |
| 📱 扫码即用 | 手机扫描 PC 端二维码即可打开上传页，无需安装任何 App |
| 🖥️ 桌面 GUI | 基于 Tkinter 的原生窗口，显示二维码、访问地址、状态与保存路径 |
| 🔥 自动防火墙管理 | 程序启动自动放行端口，退出自动清理规则，无需手动配置 |
| 📂 自定义保存目录 | 可随时切换文件保存位置，默认 `~/PhoneUploads` |
| 📦 开箱即用 | 提供 `WirelessTransfer.exe`，免 Python 环境直接双击运行 |
| 🌍 移动端适配 | 上传页采用响应式 HTML，适配手机浏览器，支持多文件同时上传 |

---

## 🧩 技术栈

| 层级 | 技术 | 用途 |
| --- | --- | --- |
| Web 框架 | [FastAPI](https://fastapi.tiangolo.com/) | 提供 HTTP 上传服务与页面路由 |
| ASGI 服务器 | [Uvicorn](https://www.uvicorn.org/) | 运行 FastAPI 应用，监听端口 |
| GUI | [Tkinter](https://docs.python.org/3/library/tkinter.html) | 构建桌面窗口界面 |
| 二维码 | [qrcode](https://github.com/lincolnloop/python-qrcode) | 生成访问地址二维码 |
| 图像处理 | [Pillow (PIL)](https://python-pillow.org/) | 二维码图片缩放与 Tk 渲染 |
| 文件上传 | [python-multipart](https://andrew-d.github.io/python-multipart/) | FastAPI 解析 `multipart/form-data` |
| 打包 | [PyInstaller](https://pyinstaller.org/) | 将 Python 脚本打包为 Windows EXE |
| 系统 | Windows `netsh` | 自动管理防火墙入站规则 |

---

## 🏗 工作原理 / 架构

```
┌──────────────────────────────────────────────────────────────┐
│                        Windows PC                            │
│                                                              │
│   ┌──────────────────────┐        ┌────────────────────────┐ │
│   │  Tkinter GUI         │        │  FastAPI + Uvicorn     │ │
│   │  ───────────────     │        │  ────────────────────  │ │
│   │  · 显示二维码        │  启动  │  · GET  /  上传页面    │ │
│   │  · 显示访问地址      │ ─────▶ │  · POST /upload 接收   │ │
│   │  · 状态/保存路径     │        │  · 写入 save_folder    │ │
│   │  · 选择/打开文件夹  │        │  · 监听 0.0.0.0:8266   │ │
│   └──────────────────────┘        └───────────┬────────────┘ │
│              ▲                                ▲              │
│      自动添加/删除防火墙规则 (netsh)           │              │
└──────────────┼────────────────────────────────┼──────────────┘
               │ Wi-Fi 局域网                   │
               │                                │
        ┌──────┴───────┐               ┌────────┴─────────┐
        │   iPhone /   │   扫码打开    │  浏览器上传页面    │
        │  手机摄像头  │ ───────────▶ │  选文件 → 上传    │
        └──────────────┘               └───────────────────┘
```

**核心流程：**

1. **启动**：GUI 初始化后 300ms 调用 `start_service()`。
2. **放行端口**：`add_firewall()` 通过 `netsh advfirewall` 添加名为 `PhoneTransfer_Auto` 的入站规则，放行 TCP `8266`。
3. **获取本机 IP**：`get_ip()` 通过建立到 `8.8.8.8` 的 UDP socket 读取本机网卡 IP。
4. **生成二维码**：将 `http://{IP}:8266` 编码为二维码并渲染到窗口。
5. **启动服务**：在守护线程中运行 Uvicorn，监听 `0.0.0.0:8266`。
6. **手机扫码**：手机扫描二维码，浏览器打开上传页 `/`。
7. **上传文件**：在页面选择文件并提交，`POST /upload` 将文件保存到 `save_folder`。
8. **退出清理**：窗口关闭或进程退出时，`remove_firewall()` 删除防火墙规则（同时由 `atexit` 兜底）。

---

## 📁 项目结构

```
wireless-transfer/
├── Apple2PC.py          # 主程序源码（GUI + FastAPI 服务，单文件）
├── WirelessTransfer.exe # Windows 可执行文件（PyInstaller 打包产物）
├── icon.ico            # 应用图标
├── .gitignore          # Python 项目忽略规则
├── LICENSE             # MIT 许可证
└── README.md           # 项目说明文档
```

> 仓库采用单文件架构（`Apple2PC.py`），所有业务逻辑集中在该文件中，分为：配置、防火墙、IP 探测、目录选择、Web 页面、上传 API、服务启动、GUI 八个模块。

---

## ⚙️ 环境要求

- **操作系统**：Windows 7 / 10 / 11（依赖 `netsh` 防火墙命令与 `os.startfile`）
- **Python**：3.8 及以上（如需从源码运行 / 自行打包）
- **网络**：手机与电脑需连接**同一个 Wi-Fi** 网络
- **权限**：添加 / 删除防火墙规则需管理员权限，建议以管理员身份运行

### Python 依赖

```bash
pip install fastapi uvicorn qrcode Pillow python-multipart
```

> 打包 EXE 时还需：`pip install pyinstaller`

---

## 🚀 快速开始

### 方式一：直接使用 EXE（推荐普通用户）

1. 前往 [Releases](https://github.com/brone2018/wireless-transfer/releases/tag/v1.0.1) 下载 `WirelessTransfer.exe`。
2. **右键 → 以管理员身份运行**（便于自动配置防火墙）。
3. 窗口出现二维码与访问地址即表示服务已启动。

### 方式二：从源码运行（推荐开发者）

```bash
# 1. 克隆仓库
git clone https://github.com/brone2018/wireless-transfer.git
cd wireless-transfer

# 2. 安装依赖
pip install -r requirements.txt   # 如未提供，见上方依赖列表手动安装

# 3. 运行
python Apple2PC.py
```

---

## 📖 使用说明

1. **启动程序**：运行 `WirelessTransfer.exe` 或 `python Apple2PC.py`。
2. **确认状态**：窗口顶部显示 `🟢 Running`，下方显示访问地址（如 `http://192.168.1.10:8266`）。
3. **（可选）更改保存目录**：点击「📁 Select Folder」选择目标文件夹；点击「📂 Open Folder」可快速打开当前保存目录。
4. **手机扫码**：用 iPhone 相机或任意浏览器扫描窗口中的二维码。
5. **选择文件**：在打开的网页点击「1 - Choose Files」，选择相册或文件中的内容。
6. **上传**：点击「2 - Upload Files」，出现 ✅ Upload Successful! 即上传成功。
7. **查看文件**：在 PC 的保存目录中即可看到上传的文件。
8. **退出**：关闭窗口即可，程序会自动清理防火墙规则。

> ⚠️ 重要提示：手机与电脑必须处于**同一 Wi-Fi** 网络，否则无法访问。

---

## 🔧 配置说明

在 `Apple2PC.py` 顶部的 `CONFIG` 区可调整以下常量：

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `PORT` | `8266` | HTTP 服务监听端口 |
| `RULE_NAME` | `PhoneTransfer_Auto` | 防火墙规则名称（用于自动添加/删除） |
| `save_folder` | `~/PhoneUploads` | 文件保存目录，可在 GUI 中动态切换 |

修改端口后，请同步确认该端口未被占用，且防火墙规则会自动适配新端口。

---

## 🌐 API 接口文档

服务启动后，可在浏览器或使用 HTTP 工具直接调用以下接口。

### `GET /` — 上传页面

返回移动端友好的 HTML 上传页（含文件选择与提交表单）。

- **响应**：`text/html`（`HTMLResponse`）

### `POST /upload` — 文件上传

接收一个或多个文件，保存到 `save_folder`。

- **Content-Type**：`multipart/form-data`
- **表单字段**：`files`（可重复，多文件）
- **成功响应**：`200`，返回绿色提示页 `✅ Upload Successful!`
- **未选择文件**：返回黄色提示页 `⚠️ Please select files first`
- **失败响应**：返回红色提示页 `❌ Upload Failed`

**cURL 示例：**

```bash
curl -X POST http://<PC_IP>:8266/upload \
  -F "files=@/path/to/photo1.jpg" \
  -F "files=@/path/to/video2.mp4"
```

---

## 📦 打包说明（PyInstaller）

将 `Apple2PC.py` 打包为单文件 EXE：

```bash
pyinstaller --onefile --windowed --name WirelessTransfer \
  --icon icon.ico Apple2PC.py
```

**说明：**

- `--onefile`：生成单个 EXE，便于分发。
- `--windowed`：无控制台黑窗（GUI 程序）。
- 源码已包含 PyInstaller 兼容处理：
  ```python
  if getattr(sys, 'frozen', False):
      multiprocessing.freeze_support()
  if getattr(sys, 'frozen', False) and sys.stdout is None:
      sys.stdout = open(os.devnull, 'w')
      sys.stderr = open(os.devnull, 'w')
  ```
  上述逻辑确保冻结（frozen）环境下多进程正常启动，并屏蔽无 stdout 时的报错。

打包产物位于 `dist/WirelessTransfer.exe`。

---

## 🔒 安全说明

本项目面向**可信局域网**环境下的个人使用，使用时请注意：

- **监听地址**：服务绑定 `0.0.0.0`，同一局域网内的任何设备均可访问，请在可信网络中使用。
- **无身份认证**：上传接口未设置密码 / Token，建议仅在家庭或私有网络使用，避免在公共 Wi-Fi 下运行。
- **CORS 策略**：当前 `allow_origins=["*"]` 完全开放，便于浏览器跨域调用；如需收紧，可改为白名单。
- **防火墙规则**：运行期间临时放行 TCP `8266`，退出自动清理；如异常退出未清理，可手动删除名为 `PhoneTransfer_Auto` 的规则。
- **文件名安全建议**（可选优化方向）：当前 `os.path.join(save_folder, f.filename)` 直接使用客户端文件名，若作为公开服务部署，建议对文件名做 `os.path.basename` 处理或重命名，避免路径穿越风险。

---

## ❓ 常见问题

**Q1：手机扫码打不开页面？**
- 请确认手机与电脑在**同一 Wi-Fi**；某些公共/企业网络会隔离客户端互访，请改用家庭网络。
- 检查防火墙是否放行端口（以管理员身份运行程序以确保规则添加成功）。

**Q2：窗口显示 IP 为 `127.0.0.1`？**
- 表示未探测到可用网卡 IP（可能未联网或被拦截），请检查网络连接。程序通过连接 `8.8.8.8` 探测本机 IP，需保证至少有短暂的外网连通。

**Q3：上传失败提示 ❌？**
- 可能原因：保存目录无写权限、磁盘空间不足、文件名含非法字符。请尝试更换保存目录或检查权限。

**Q4：如何更换端口？**
- 修改 `Apple2PC.py` 中 `PORT` 常量后重新运行或重新打包；防火墙规则会自动适配。

**Q5：退出后防火墙规则未删除？**
- 若进程被强杀，`atexit` 可能无法执行。可手动执行：
  ```powershell
  netsh advfirewall firewall delete rule name="PhoneTransfer_Auto"
  ```

---

## 🤝 贡献

欢迎通过 Issue 或 Pull Request 反馈问题与改进建议。

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交修改：`git commit -m "Add some feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/brone2018">brone2018</a>
</p>
