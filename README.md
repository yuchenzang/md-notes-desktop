# 煜辰的 Markdown 笔记（Windows 桌面版）

一个 Windows 桌面端 Markdown 笔记应用。

- 左侧标题：`MARKDOWN`
- 副标题：`煜辰的 Markdown`
- 应用图标：`app_icon.ico`（紫色背景 + 白色 M 字）

## 技术方案

完全使用原生 PySide6（Qt Widgets）实现，不依赖任何浏览器内核，无黑框、无闪退。

- 界面：PySide6 原生控件 + Qt 样式表
- Markdown 渲染：Python `markdown` 库
- 导出：MD（原生）、PDF（reportlab）、Word（python-docx）
- 导入：Markdown（原生读取 *.md *.markdown）、PDF（pdfminer.six）、Word（python-docx 转 Markdown），支持多选批量导入
- 数据存储：`notes_data/notes.json`
- 图标：`app_icon.ico`（紫色背景 + 白色 M 字，含多尺寸 16~256px）
- 启动器：`pythonw.exe`（无控制台窗口）

## 功能

- 左侧笔记列表，显示**标题 / 大小 / 更新时间**
- 点击笔记切换，实时编辑与预览
- 顶部搜索框按标题过滤
- 顶部工具栏：导入 Markdown / PDF / Word（支持多选）、导出 MD / PDF / Word、删除当前笔记
- 新建笔记（紫色按钮置顶/置底），删除确认弹窗
- 底部状态栏：行列号、字数、保存状态
- 自动保存到本地 JSON

## 运行方式

### 1. 直接运行

```cmd
.venv\Scripts\pythonw.exe main.pyw
```

或双击项目根目录下的 `run_desktop.cmd`。

### 2. 创建 / 刷新桌面快捷方式

```cmd
.venv\Scripts\python.exe make_lnk.py
```

> 会在桌面生成 `煜辰的 Markdown 笔记.lnk`（带紫色 M 图标），双击只出现一个应用窗口，无黑框。

### 3. 手动创建快捷方式

位置填：
```
"D:\Q-Blot\Users\yaokemei001\热点靶点发现与文献检索\md-notes-desktop\.venv\Scripts\pythonw.exe" "main.pyw"
```

## 项目结构

```
md-notes-desktop/
├── main.pyw            # 应用本体
├── app_icon.ico        # 应用图标（用户提供：紫色背景 + 白色 M 字）
├── icon_source.png     # 图标源文件
├── make_icon.py        # 从 icon_source.png 生成/刷新 app_icon.ico
├── run_desktop.cmd     # 启动脚本
├── make_lnk.py         # 生成桌面 .lnk
├── notes_data/         # 笔记数据
└── (src/ dist/ 等为早期 React 方案残留，可忽略或删除)
```

## 故障排查

- **双击没反应 / 一闪而过**：查看项目根目录 `crash.log`，或用控制台运行看报错：
  ```cmd
  .venv\Scripts\python.exe main.pyw
  ```
- **依赖缺失**：
  ```cmd
  .venv\Scripts\python.exe -m pip install PySide6 markdown reportlab python-docx pdfminer.six
  ```
- **笔记丢失**：数据在 `notes_data/notes.json`，备份或删除该文件即可。
