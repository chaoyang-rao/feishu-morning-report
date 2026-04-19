# 📱 飞书晨报技能 (feishu-morning-report)

## 功能说明

自动化的飞书晨报生成与发送技能，支持：
- 📰 从 RSS 源自动获取最新新闻（IT 之家、中关村在线等）
- 🌤️ 天气信息集成
- 🎨 飞书交互式卡片发送
- ⏰ 定时任务支持（每天 09:00 自动执行）

## 使用场景

当用户需要：
1. 每天定时发送行业晨报到飞书群
2. 自动收集并整理新闻资讯
3. 生成格式统一的飞书卡片消息

## 核心配置

### 定时任务

**执行时间**：每天 09:00

**执行方式**：AI 助手自动执行

**脚本路径**：`/Users/Zhuanz1/.openclaw/workspace-assistant/scripts/生成晨报.py`

### 发送目标

| 群名 | 群 ID |
|------|-------|
| 一人部门 | `oc_d9ff52a149e36edac69db6ad537d497a` |

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
| 头条新闻 | 10 条 | RSS 源获取（优先 24 小时内），不足则用备用新闻补充 |
| 每日洞察 | 1 条 | 固定文案 + 今日思考 |

## 新闻来源优先级

### RSS 源（按顺序）

1. IT 之家 - 全部新闻（主源）
2. IT 之家 - 手机数码
3. 中关村在线 - 手机频道
4. 太平洋电脑网 - 手机频道

### 备用新闻

当 RSS 源不足 10 条时，使用经典回顾新闻补充

## 处理规则

### 去重规则

- 基于标题标准化（小写 + 去空格）
- 基于 URL 去重
- 时效性检查（优先 24 小时内新闻）

### 故障处理

| 故障类型 | 处理方式 |
|---------|---------|
| 天气 API 失败 | 使用默认文案"多云，12-20°C" |
| RSS 源失败 | 自动切换到下一个源 |
| 所有 RSS 失败 | 使用 web_search 补充 + 备用新闻 |

## 相关文件

| 文件 | 路径 |
|------|------|
| 主脚本 | `/Users/Zhuanz1/.openclaw/workspace-assistant/scripts/生成晨报.py` |
| 日志 | `/Users/Zhuanz1/.openclaw/logs/晨报.log` |
| 错误日志 | `/Users/Zhuanz1/.openclaw/logs/晨报-error.log` |

## 检查清单

- [ ] 每天 09:00 后检查日志确认执行成功
- [ ] 每周一检查 RSS 源健康状态
- [ ] 每月检查定时任务状态

## 版本历史

- **v1.0** (2026-04-19) - 初始版本
  - 支持 RSS 新闻自动获取
  - 飞书交互式卡片发送
  - 定时任务集成

## GitHub 仓库

**仓库地址**：待配置

**技能包地址**：`~/.openclaw/skills/feishu-morning-report/`
