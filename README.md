# 煜辰的 Markdown 笔记（Windows 桌面版）

一个 Windows 桌面端 Markdown 笔记应用：左侧笔记列表 + 右侧「编辑 / 实时预览」双栏，支持 Markdown / PDF / Word 互导，数据完全存放在本地。

- 窗口标题与副标题：`煜辰的 Markdown 笔记` / `煜辰的 Markdown`
- 界面标识：`MARKDOWN`
- 应用图标：`app_icon.ico`（紫色背景 + 白色 M 字）

## 技术方案

完全使用原生 **PySide6（Qt Widgets）** 实现，**不依赖任何浏览器内核**（不用 Electron / WebView / pywebview），因此没有黑框、没有闪退、启动即出窗口。

| 用途 | 方案 |
|---|---|
| 界面 | PySide6 原生控件 + Qt 样式表（QSS） |
| Markdown 渲染 | Python `markdown` 库 |
| 导出 | MD（原生）、PDF（reportlab）、Word（python-docx） |
| 导入 | Markdown（原生读取 `*.md` `*.markdown`）、PDF（pdfminer.six）、Word（python-docx 转 Markdown），支持多选批量导入 |
| 数据存储 | 本地 JSON：`notes_data/notes.json` |
| 启动器 | `pythonw.exe`（无控制台窗口） |

## 功能

- 左侧笔记列表，显示 **标题 / 大小 / 更新时间**
- 点击笔记切换，右侧实时编辑与预览
- 顶部搜索框按标题过滤
- 顶部工具栏：导入（Markdown / PDF / Word，支持多选）、导出 MD / PDF / Word、删除当前笔记
- 新建笔记（紫色按钮），删除有确认弹窗
- 底部状态栏：行列号、字数、保存状态
- 自动保存到本地 JSON

## 环境要求

- Windows 10 / 11
- Python 3.10+（开发环境为 3.13）

## 安装

在本项目根目录执行：

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> 虚拟环境**必须**建在项目根目录且命名为 `.venv`，因为 `run_desktop.cmd` 和 `make_lnk.py` 固定引用 `.venv\Scripts\pythonw.exe`。

## 运行

方式一，双击项目根目录的 `run_desktop.cmd`；

方式二，命令行直接启动（无控制台窗口）：

```cmd
.venv\Scripts\pythonw.exe main.pyw
```

需要在控制台看报错信息时，改用 `python.exe`：

```cmd
.venv\Scripts\python.exe main.pyw
```

## 创建桌面快捷方式

```cmd
.venv\Scripts\python.exe make_lnk.py
```

会在桌面生成 `煜辰的 Markdown 笔记.lnk`（带紫色 M 图标），双击只出现一个应用窗口，无黑框。

该脚本用原生 COM（`IShellLinkW` + `IPersistFile`）实现，不依赖 `WScript.Shell` / `pywin32`，并且以 Unicode 存储路径，能正确处理中文目录名。

### 手动创建快捷方式

如果不想用脚本，可在桌面新建快捷方式，按下表填写（把 `<项目目录>` 换成你的实际路径）：

| 字段 | 值 |
|---|---|
| 目标 | `"<项目目录>\.venv\Scripts\pythonw.exe" "<项目目录>\main.pyw"` |
| 起始位置 | `<项目目录>` |
| 图标 | `<项目目录>\app_icon.ico` |

## 项目结构

```
md-notes-desktop/
├── main.pyw            # 应用本体（PySide6 全部逻辑）
├── app_icon.ico        # 应用图标（紫色背景 + 白色 M 字，含 16~256px 多尺寸）
├── icon_source.png     # 图标源文件
├── make_icon.py        # 从 icon_source.png 生成/刷新 app_icon.ico
├── make_lnk.py         # 生成桌面 .lnk 快捷方式
├── run_desktop.cmd     # 一键启动脚本
├── requirements.txt    # 依赖清单
├── LICENSE             # MIT
└── notes_data/         # 笔记数据（本机运行后生成，已被 .gitignore 排除）
```

## 数据与备份

笔记全部保存在本机 `notes_data/notes.json`，**不上传任何服务器**。

- 备份：直接复制 `notes_data/` 整个目录
- 清空：删除 `notes_data/notes.json` 即可（应用会重新创建空数据）
- 该目录已被 `.gitignore` 排除，不会被提交到仓库

## 故障排查

- **双击没反应 / 一闪而过**：查看项目根目录的 `crash.log`，或用 `.venv\Scripts\python.exe main.pyw` 在控制台运行看报错。
- **提示缺少依赖**：
  ```cmd
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  ```
- **快捷方式启动失败**：确认虚拟环境就在项目根目录且名为 `.venv`，然后重新运行 `make_lnk.py`。
- **笔记丢失**：数据在 `notes_data/notes.json`，从备份恢复该文件即可。

## 许可证

[MIT](LICENSE) © 2026 yuchenzang
