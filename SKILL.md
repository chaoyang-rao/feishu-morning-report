# 📱 飞书晨报技能 (feishu-morning-report)

## 功能说明

自动化的飞书晨报生成与发送技能，支持：
- 📰 从 RSS 源自动获取最新新闻（IT 之家、36 氪、雷峰网、钛媒体）
- 🌤️ 天气信息集成（wttr.in API）
- 🎨 本地配图轮播（5 张图片循环使用）
- ⏰ 定时任务支持（每天 09:00 自动执行）
- 📊 新闻去重 + 时效性检查（仅 24 小时内新闻）

## 开箱即用

### 1. 安装技能

```bash
# 克隆技能包到本地
git clone https://github.com/您的用户名/feishu-morning-report.git ~/.openclaw/skills/feishu-morning-report
```

### 2. 配置飞书应用

编辑 `生成晨报.py`，修改以下配置：

```python
FEISHU_APP_ID = "cli_xxx"           # 替换为您的飞书 App ID
FEISHU_APP_SECRET = "xxx"           # 替换为您的飞书 App Secret
TARGET_CHAT_ID = "oc_xxx"           # 替换为目标群聊 ID
```

### 3. 准备配图（可选）

在 `images/` 目录放置 5 张轮播配图：

```
images/
├── 晨报配图 -1.png
├── 晨报配图 -2.png
├── 晨报配图 -3.png
├── 晨报配图 -4.png
└── 晨报配图 -5.png
```

> 💡 如不配置配图，脚本将使用纯文本卡片发送

### 4. 设置定时任务

**OpenClaw Web 页面配置**：

- **执行时间**：每天 09:00
- **执行指令**：
```
请执行晨报生成任务：
1. 运行脚本：python3 /Users/Zhuanz1/.openclaw/workspace-assistant/scripts/生成晨报.py
2. 检查日志确认执行成功
```

## 核心配置

### 定时任务

| 配置项 | 值 |
|--------|-----|
| 执行时间 | 每天 09:00 |
| 执行方式 | AI 助手自动执行 |
| 脚本路径 | `/Users/Zhuanz1/.openclaw/workspace-assistant/scripts/生成晨报.py` |
| 日志路径 | `/Users/Zhuanz1/.openclaw/logs/晨报.log` |

### 发送目标

| 配置项 | 值 |
|--------|-----|
| 目标群 | 一人部门 |
| 群聊 ID | `oc_d9ff52a149e36edac69db6ad537d497a` |
| 消息类型 | 飞书交互式卡片（interactive） |

## 卡片格式

### 标准结构

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "template": "blue",
    "title": {"content": "📱 手机行业晨报 - MM 月 DD 日", "tag": "plain_text"}
  },
  "elements": [
    {
      "tag": "img",
      "img_key": "img_xxx",
      "alt": {"tag": "plain_text", "content": "手机行业晨报配图"}
    },
    {
      "tag": "div",
      "text": {
        "content": "**📅 YYYY 年 MM 月 DD 日 | 星期 X**\n🌤️ 天气：[天气信息]",
        "tag": "lark_md"
      }
    },
    {"tag": "hr"},
    {"tag": "div", "text": {"content": "**🔥 头条新闻**", "tag": "lark_md"}},
    // 10 条新闻，每条格式：
    {
      "tag": "div",
      "text": {
        "content": "**1. 新闻标题**\n\n新闻摘要...\n\n👉 [查看详情](URL)",
        "tag": "lark_md"
      }
    },
    {"tag": "hr"},
    // ... 重复 10 条新闻
    {
      "tag": "div",
      "text": {
        "content": "**💡 每日洞察**\n\n> \"手机行业每天都在变化，保持关注才能抓住机会\"",
        "tag": "lark_md"
      },
      "style": {"background_style": "grey"}
    },
    {
      "tag": "action",
      "actions": [{
        "tag": "button",
        "text": {"content": "✅ 已收到", "tag": "plain_text"},
        "type": "primary"
      }]
    }
  ]
}
```

## 内容规范

| 模块 | 数量 | 说明 |
|------|------|------|
| 日期天气 | 1 条 | 公历日期 + 星期 + 农历 + 天气 |
| 头条新闻 | 10 条 | RSS 源获取（优先 24 小时内），不足则展示全部 |
| 每日洞察 | 1 条 | 固定文案 + 今日思考（每天不同） |

## 新闻来源

### RSS 源（按优先级）

| 序号 | 来源 | 状态 |
|------|------|------|
| 1 | IT 之家 - 全部新闻 | ✅ 已验证 |
| 2 | 36 氪 | ✅ 已验证 |
| 3 | 雷峰网 | ✅ 已验证 |
| 4 | 钛媒体 | ✅ 已验证 |

### 关键词过滤

自动过滤与手机行业相关的新闻：
- 手机、智能、AI、科技、数码
- 华为、小米、OPPO、vivo、荣耀、苹果
- 发布、新品、大模型

## 配图配置

### 本地轮播模式（默认）

**配置目录**：`/Users/Zhuanz1/.openclaw/workspace-assistant/images/`

**配图列表**（5 张循环）：
```
晨报配图 -1.png  (约 500KB)
晨报配图 -2.png  (约 460KB)
晨报配图 -3.png  (约 600KB)
晨报配图 -4.png  (约 490KB)
晨报配图 -5.png  (约 410KB)
```

**轮换逻辑**：
- 每天自动切换到下一张
- 5 天一循环
- 状态记录在 `.配图状态.json`
- 图片不存在时自动跳过

**配图选择器**：`晨报配图选择器.py`

```python
# 5 张配图列表（按顺序循环）
IMAGES = [
    "晨报配图 -1.png",
    "晨报配图 -2.png",
    "晨报配图 -3.png",
    "晨报配图 -4.png",
    "晨报配图 -5.png",
]
```

### 上传图片到飞书

脚本自动将本地图片上传到飞书获取 `image_key`，用于卡片展示。

**上传函数**：`upload_image_to_feishu(image_path, token)`

**流程**：
1. 调用飞书 `/open-apis/im/v1/images` 接口
2. 获取 `image_key`
3. 在卡片中通过 `<img>` 元素展示

### 无配图模式

如不配置配图，脚本将发送纯文本卡片（无图片元素）。

## 处理规则

### 去重规则

- 基于标题标准化（小写 + 去空格）
- 基于 URL 去重
- 时效性检查（优先 24 小时内新闻）

### 故障处理

| 故障类型 | 处理方式 |
|---------|---------|
| 天气 API 失败 | 使用备用 API（Open-Meteo） |
| RSS 源失败 | 自动切换到下一个源 |
| 所有 RSS 失败 | 新闻数为 0，卡片仍发送 |
| 图片不存在 | 发送纯文本卡片 |
| 图片上传失败 | 发送纯文本卡片 |

## 文件结构

```
feishu-morning-report/
├── SKILL.md                    # 技能文档
├── 生成晨报.py                 # 主脚本
├── 晨报配图选择器.py           # 配图轮播逻辑
└── images/                     # 配图目录（可选）
    ├── 晨报配图 -1.png
    ├── 晨报配图 -2.png
    ├── 晨报配图 -3.png
    ├── 晨报配图 -4.png
    ├── 晨报配图 -5.png
    └── .配图状态.json          # 轮播状态记录
```

## 相关文件

| 文件 | 路径 |
|------|------|
| 主脚本 | `/Users/Zhuanz1/.openclaw/workspace-assistant/scripts/生成晨报.py` |
| 配图选择器 | `/Users/Zhuanz1/.openclaw/workspace-assistant/scripts/晨报配图选择器.py` |
| 日志 | `/Users/Zhuanz1/.openclaw/logs/晨报.log` |
| 错误日志 | `/Users/Zhuanz1/.openclaw/logs/晨报-error.log` |

## 检查清单

- [ ] 每天 09:00 后检查日志确认执行成功
- [ ] 每周一检查 RSS 源健康状态
- [ ] 每月检查定时任务状态
- [ ] 配图不足 5 张时及时补充

## 版本历史

- **v1.0** (2026-04-19) - 初始版本
  - 支持 RSS 新闻自动获取
  - 本地配图轮播（5 张循环）
  - 飞书交互式卡片发送
  - 定时任务集成
  - 删除 AI 生成图片功能（简化配置）

## GitHub 仓库

**仓库地址**：`https://github.com/您的用户名/feishu-morning-report`

**技能包地址**：`~/.openclaw/skills/feishu-morning-report/`

## 常见问题

### Q: 如何更换配图？
A: 替换 `images/` 目录下的 5 张 PNG 图片，保持文件名不变。

### Q: 如何修改发送时间？
A: 在 OpenClaw Web 页面的定时任务配置中修改执行时间。

### Q: 新闻不足 10 条怎么办？
A: 脚本会展示所有获取到的新闻，不强制凑满 10 条。

### Q: 如何查看执行日志？
A: 查看 `/Users/Zhuanz1/.openclaw/logs/晨报.log`
