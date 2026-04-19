#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 手机行业晨报自动生成脚本（实时数据版）
🦞 OpenClaw 小助理
⏰ 每天 9:00 自动运行
✨ 优化：使用真实 API 获取新闻、天气、金价
✨ 新增：多 RSS 源、去重逻辑、时效性检查、RSS 健康检查
"""

import requests
import json
import base64
import sys
from datetime import datetime, timedelta
import os
import lunardate
import feedparser
from urllib.parse import urlparse

# 导入配图选择器（循环使用本地图片）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 晨报配图选择器 import get_today_image

# 配置
OUTPUT_DIR = "/Users/Zhuanz1/.openclaw/workspace-assistant"
IMAGE_OUTPUT_DIR = "/Users/Zhuanz1/.openclaw/workspace-assistant/images"
FEISHU_APP_ID = "cli_a93ff1dd98f89cb5"  # OpenClaw brother 机器人
FEISHU_APP_SECRET = "y3iR386JiUJNXDPe2ax7DdWTGoczvndq"
TARGET_CHAT_ID = "oc_d9ff52a149e36edac69db6ad537d497a"  # 一人部门



# RSS 源配置（已验证可用源）
RSS_SOURCES = [
    {
        "name": "IT 之家 - 全部新闻",
        "url": "https://www.ithome.com/rss/",
        "keywords": ["手机", "智能", "ai", "科技", "数码", "发布", "新品", "华为", "小米", "OPPO", "vivo", "荣耀", "苹果"],
        "healthy": True  # ✅ 已验证可用 (HTTP 200)
    },
    {
        "name": "36 氪",
        "url": "https://36kr.com/feed",
        "keywords": ["手机", "智能", "科技", "华为", "小米", "OPPO", "vivo", "荣耀", "苹果", "发布", "新品"],
        "healthy": True  # ✅ 已验证可用 (HTTP 200, 141KB)
    },
    {
        "name": "雷峰网",
        "url": "https://www.leiphone.com/feed",
        "keywords": ["手机", "智能", "AI", "科技", "华为", "小米", "OPPO", "vivo", "荣耀", "苹果", "发布", "新品", "大模型"],
        "healthy": True  # ✅ 已验证可用 (HTTP 200, RSS/XML)
    },
    {
        "name": "钛媒体",
        "url": "https://www.tmtpost.com/feed",
        "keywords": ["手机", "智能", "科技", "华为", "小米", "OPPO", "vivo", "荣耀", "苹果", "发布", "数码"],
        "healthy": True  # ✅ 已验证可用 (HTTP 200, XML)
    },
    # 以下 RSS 源已失效或需要验证
    # {"name": "cnBeta", "url": "https://www.cnbeta.com.tw/backend.php", "keywords": [...]},  # ❌ 302 跳转
    # {"name": "少数派", "url": "https://sspai.com/feed", "keywords": [...]},  # ❌ 405
    # {"name": "果壳", "url": "https://www.guokr.com/feed/", "keywords": [...]},  # ❌ 302 跳转
    # {"name": "虎嗅", "url": "https://www.huxiu.com/rss/0/1.xml", "keywords": [...]},  # ❌ 404
    # {"name": "21 世纪经济报道", "url": "https://www.21jingji.com/rss/tech.xml", "keywords": [...]},  # ❌ 404
]

# 备用新闻已移除 - 新闻数不足时有多少展示多少


def get_feishu_token():
    """获取飞书 API Token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
    return resp.json().get("tenant_access_token")


def check_rss_health(rss_url, timeout=5):
    """检查 RSS 源是否可用"""
    try:
        resp = requests.get(rss_url, timeout=timeout)
        if resp.status_code == 200 and len(resp.content) > 100:
            return True, f"✅ 可用 ({len(resp.content)} bytes)"
        else:
            return False, f"❌ 状态码：{resp.status_code}"
    except Exception as e:
        return False, f"❌ 错误：{str(e)}"


def rss_health_check():
    """在脚本开头检查所有 RSS 源的健康状态"""
    print("\n🔍 RSS 源健康检查...")
    healthy_sources = []
    
    # 初始化时效性检查计数器
    is_within_24_hours.debug_count = 0
    
    for source in RSS_SOURCES:
        is_healthy, status = check_rss_health(source["url"])
        source["healthy"] = is_healthy
        source["status"] = status
        print(f"  {source['name']}: {status}")
        if is_healthy:
            healthy_sources.append(source)
    
    if not healthy_sources:
        print("⚠️ 所有 RSS 源都不可用，将使用 web_search 作为补充")
    else:
        print(f"✅ {len(healthy_sources)}/{len(RSS_SOURCES)} 个 RSS 源可用\n")
    
    return healthy_sources


def is_within_24_hours(entry, strict=True):
    """
    检查新闻是否在 24 小时内发布
    strict=True: 严格模式，没有时间信息则拒绝
    strict=False: 宽松模式，没有时间信息则接受
    """
    try:
        # 尝试解析发布时间
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            pub_time = datetime(*published[:6])
            time_diff = datetime.now() - pub_time
            hours_diff = time_diff.total_seconds() / 3600
            
            # 输出调试信息（仅第一条）
            if hasattr(is_within_24_hours, 'debug_count') and is_within_24_hours.debug_count < 3:
                print(f"  ⏰ 时效性检查：{hours_diff:.1f}小时前 {'✅' if hours_diff < 24 else '❌'}")
                is_within_24_hours.debug_count += 1
            
            return hours_diff < 24  # 严格 24 小时限制
        
        # 没有时间信息时，根据 strict 参数决定
        if strict:
            return False  # 严格模式：拒绝
        else:
            return True   # 宽松模式：接受
    except Exception as e:
        # 解析失败时拒绝
        return False


def normalize_title(title):
    """标准化标题用于去重比较"""
    if not title:
        return ""
    # 移除多余空格、转小写
    return " ".join(title.lower().split())


def search_news(max_results=10):
    """
    使用 RSS 源获取最新手机行业新闻
    时效性要求：不得超过 24 小时
    新闻数不足时有多少展示多少（不使用备用新闻）
    """
    news_items = []
    seen_titles = set()  # 用于去重的标题集合
    seen_urls = set()    # 用于去重的 URL 集合
    
    # 使用 RSS 源获取新闻
    print(f"🔍 使用 RSS 源获取最新手机新闻...")
    for source in RSS_SOURCES:
        if not source.get("healthy", True):
            continue
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries:
                if len(news_items) >= max_results:
                    break
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", "")[:200] if entry.get("summary") else ""
                
                # 时效性检查（严格 24 小时内）
                if not is_within_24_hours(entry):
                    continue
                
                # 去重检查
                normalized_title = normalize_title(title)
                if normalized_title in seen_titles or link in seen_urls:
                    continue
                
                # 关键词过滤
                if any(keyword in normalized_title for keyword in source["keywords"]):
                    seen_titles.add(normalized_title)
                    seen_urls.add(link)
                    news_items.append({
                        "title": title,
                        "url": link,
                        "content": summary,
                        "source": source["name"],
                        "is_backup": False
                    })
        except Exception as e:
            print(f"  ⚠️ RSS 源失败 {source['name']}: {e}")
    
    # 新闻数不足时有多少展示多少（不使用备用新闻）
    print(f"✅ 共获取 {len(news_items)} 条新闻（不足 10 条则展示全部）")
    return news_items[:max_results]


def get_weather_backup(city="Dongguan"):
    """备用天气 API（Open-Meteo）"""
    # 东莞坐标：23.02, 113.75
    city_coords = {
        "Dongguan": (23.02, 113.75),
        "Shenzhen": (22.54, 114.06),
        "Guangzhou": (23.13, 113.26),
        "Shanghai": (31.23, 121.47),
        "Beijing": (39.90, 116.40)
    }
    lat, lon = city_coords.get(city, (23.02, 113.75))
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FShanghai"
        headers = {"User-Agent": "OpenClaw-Morning-Report/1.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        temp = current.get("temperature_2m", 20)
        humidity = current.get("relative_humidity_2m", 60)
        weather_code = current.get("weather_code", 2)
        temp_max = daily.get("temperature_2m_max", [25])[0]
        temp_min = daily.get("temperature_2m_min", [15])[0]
        
        weather_codes = {
            0: "晴", 1: "晴间多云", 2: "多云", 3: "阴",
            45: "雾", 48: "雾凇", 51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
            61: "小雨", 63: "中雨", 65: "大雨", 71: "小雪", 73: "中雪", 75: "大雪",
            80: "阵雨", 81: "中阵雨", 82: "大阵雨", 95: "雷雨"
        }
        weather_text = weather_codes.get(weather_code, "多云")
        
        return f"{weather_text}，{temp_min}-{temp_max}°C，当前{temp}°C，湿度{humidity}%"
    except Exception as e:
        print(f"⚠️ 备用天气 API 也失败：{e}")
        return "多云，15-25°C"


def get_weather(city="Dongguan"):
    """使用 wttr.in API 获取真实天气（无需 API key，支持城市名）"""
    # 使用 wttr.in API，支持城市名（使用英文名称）
    # 常见城市英文名：Dongguan, Shenzhen, Guangzhou, Shanghai, Beijing
    city_encoded = city.replace(" ", "+")
    url = f"https://wttr.in/{city_encoded}?format=j1"
    
    try:
        # 增加重试机制和 User-Agent（wttr.in 要求）
        headers = {"User-Agent": "OpenClaw-Morning-Report/1.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")
        
        # 检查响应内容是否为有效 JSON
        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            raise Exception(f"JSON 解析失败：{e}")
        
        # 天气代码转中文
        weather_codes = {
            0: "晴", 1: "晴间多云", 2: "多云", 3: "阴",
            45: "雾", 48: "雾凇", 51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
            61: "小雨", 63: "中雨", 65: "大雨", 71: "小雪", 73: "中雪", 75: "大雪",
            80: "阵雨", 81: "中阵雨", 82: "大阵雨", 95: "雷雨"
        }
        
        current = data.get("current_condition", [{}])[0]
        weather = data.get("weather", [{}])[0]
        
        # 验证数据完整性
        if not current or not weather:
            raise Exception("天气数据不完整")
        
        temp = int(current.get("temp_C", 0))
        feels_like = int(current.get("FeelsLikeC", 0))
        temp_max = int(weather.get("maxtempC", temp))
        temp_min = int(weather.get("mintempC", temp))
        weather_code = int(current.get("weatherCode", 0))
        weather_text = weather_codes.get(weather_code, "多云")
        humidity = current.get("humidity", "?")
        
        return f"{weather_text}，{temp_min}-{temp_max}°C，当前{temp}°C（体感{feels_like}°C），湿度{humidity}%"
    except Exception as e:
        print(f"⚠️ 天气获取失败：{e}")
        # 使用 Open-Meteo 作为备用方案
        return get_weather_backup(city)


def get_gold_info():
    """黄金价格信息（已移除）"""
    return []


def get_lunar_date(date_obj):
    """获取农历日期"""
    try:
        lunar = lunardate.LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
        return f"农历{lunar.year}年{lunar.month}月{lunar.day}"
    except:
        # 备用：简单计算
        return "农历二月十七"


def generate_morning_image(news_items, date_str):
    """
    使用阿里云通义万相生成晨报配图
    返回图片本地路径
    """
    # 确保输出目录存在
    os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
    
    # 生成提示词（基于头条新闻）
    if news_items:
        if isinstance(news_items[0], dict):
            top_news = news_items[0]['title'][:50]
        else:
            top_news = str(news_items[0])[:50]
        prompt = f"科技新闻晨报配图，手机行业，{top_news}，现代科技风格，蓝色调，简洁专业，高质量，8K"
    else:
        prompt = "科技新闻晨报配图，手机行业，现代科技风格，蓝色调，简洁专业，高质量，8K"
    
    # 文件名
    today = datetime.now().strftime("%Y%m%d")
    image_path = os.path.join(IMAGE_OUTPUT_DIR, f"晨报配图-{today}.png")
    
    # 检查是否已有今日图片
    if os.path.exists(image_path):
        print(f"♻️ 使用已有图片：{image_path}")
        return image_path
    
    # 检查是否有最近的图片可复用
    import glob
    existing_images = glob.glob(os.path.join(IMAGE_OUTPUT_DIR, "晨报配图 -*.png"))
    if existing_images:
        existing_images.sort(reverse=True)
        print(f"♻️ API 不可用，复用最近的图片：{existing_images[0]}")
        # 复制为今日图片
        import shutil
        shutil.copy2(existing_images[0], image_path)
        return image_path
    
    # 调用阿里云 API 生成图片
    try:
        headers = {
            "Authorization": f"Bearer {ALIYUN_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "wanx-v1",
            "input": {"prompt": prompt},
            "parameters": {
                "style": "<photographic>",
                "size": "1024*512",
                "n": 1
            }
        }
        
        resp = requests.post(ALIYUN_IMAGE_URL, headers=headers, json=payload, timeout=30)
        result = resp.json()
        
        # 解析结果
        if "output" in result and "results" in result["output"]:
            image_url = result["output"]["results"][0]["url"]
            
            # 下载图片
            img_resp = requests.get(image_url, timeout=10)
            with open(image_path, 'wb') as f:
                f.write(img_resp.content)
            
            print(f"🖼️ 图片已生成：{image_path}")
            return image_path
        else:
            print(f"⚠️ 图片生成失败：{result}")
            return None
            
    except Exception as e:
        print(f"⚠️ 图片生成异常：{e}")
        return None


def upload_image_to_feishu(image_path, token):
    """
    上传图片到飞书获取 image_key
    用于飞书卡片消息
    """
    try:
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        headers = {
            "Authorization": f"Bearer {token}"
            # Content-Type 由 requests 自动设置为 multipart/form-data
        }
        
        with open(image_path, 'rb') as f:
            files = {"image": (os.path.basename(image_path), f)}
            data = {"image_type": "message"}
            
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=10)
            result = resp.json()
            
            if result.get("code") == 0 or result.get("Success"):
                image_key = result.get("data", {}).get("image_key") or result.get("image_key")
                print(f"✅ 图片已上传飞书：{image_key}")
                return image_key
            else:
                print(f"⚠️ 图片上传失败：{result}")
                return None
    except Exception as e:
        print(f"⚠️ 图片上传异常：{e}")
        return None


def generate_morning_report():
    """生成晨报（使用实时数据）"""
    today = datetime.now()
    date_str = today.strftime("%Y年%m月%d日")
    weekday = today.strftime("%A")
    
    # RSS 源健康检查
    healthy_sources = rss_health_check()
    
    # 获取真实天气
    weather = get_weather()
    print(f"🌤️ 天气：{weather}")
    
    # 获取真实新闻（自动去重、时效性检查）
    print("🔍 搜索实时新闻...")
    news_items = search_news(max_results=10)
    
    # 统计新闻数量
    print(f"📰 共获取 {len(news_items)} 条新闻（全部为 24 小时内实时新闻）")
    
    # 获取农历
    try:
        lunar = lunardate.LunarDate.fromSolarDate(today.year, today.month, today.day)
        lunar_str = f"农历{lunar.year}年{lunar.month}月{lunar.day}"
    except:
        lunar_str = "农历二月十七"
    
    # 生成晨报内容
    content = "# 📱 手机行业晨报\n\n"
    content += f"> 📅 日期：{date_str} {weekday}\n"
    content += f"> 🌙 {lunar_str}\n"
    content += f"> 🌤️ 天气：{weather}\n"
    content += f"> 🦞 生成：OpenClaw 小助理（实时数据）\n\n"
    content += "---\n\n"
    content += "## 🔥 头条新闻\n\n"
    
    for i, news in enumerate(news_items[:10], 1):
        content += f"### {i}. {news['title']}\n\n"
        content += f"**来源**: [点击查看]({news['url']})\n\n"
        content += f"**摘要**: {news['content']}...\n\n"
        content += "---\n\n"
    
    # 每日洞察内容库（随机选择，保持新颖）
    insights = [
        {
            "quote": "技术不是替代人类，而是放大人类的能力。",
            "topics": [
                "📱 AI 助手如何重构手机交互逻辑？",
                "🤖 端侧大模型会让手机更懂你吗？",
                "💡 隐私保护与个性化如何平衡？"
            ]
        },
        {
            "quote": "真正的创新，是让复杂的技术变得简单。",
            "topics": [
                "🔋 万毫安时代，充电速度还重要吗？",
                "📸 2 亿像素 vs 计算摄影，哪个更重要？",
                "🎯 折叠屏是未来还是过渡？"
            ]
        },
        {
            "quote": "存量市场的竞争，拼的是用户体验的最后一厘米。",
            "topics": [
                "⚡️ 涨价潮下，用户为什么还买单？",
                "🎨 同质化时代，差异化在哪里？",
                "🌐 生态壁垒 vs 开放合作，怎么选？"
            ]
        },
        {
            "quote": "硬件是载体，软件是灵魂，生态是护城河。",
            "topics": [
                "🔗 跨设备协同，谁做得最好？",
                "🏗️ 自研芯片 vs 高通联发科，优劣何在？",
                "📊 数据驱动决策，如何避免信息茧房？"
            ]
        },
        {
            "quote": "未来的手机，可能不再是我们认知中的手机。",
            "topics": [
                "👓 AR 眼镜会取代手机吗？",
                "🧠 脑机接口是下一个风口吗？",
                "🌌 元宇宙需要什么样的终端设备？"
            ]
        }
    ]
    
    # 根据日期选择洞察内容（每天不同）
    import hashlib
    date_hash = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    insight_index = date_hash % len(insights)
    insight = insights[insight_index]
    
    content += "## 💡 每日洞察\n\n"
    content += f"> **{insight['quote']}**\n\n"
    content += "**今日思考**：\n"
    for i, topic in enumerate(insight['topics'], 1):
        content += f"{i}. {topic}\n"
    content += "\n💬 欢迎在评论区分享你的观点~\n"
    
    return content, news_items, weather


def save_to_file(content):
    today = datetime.now()
    filepath = os.path.join(OUTPUT_DIR, f"手机行业晨报-{today.strftime('%Y%m%d')}.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已保存到：{filepath}")
    return filepath


def send_to_feishu_card(news_items, weather, image_path=None):
    """发送飞书卡片消息（支持配图）"""
    token = get_feishu_token()
    if not token:
        print("❌ 获取 Token 失败")
        return False
    
    today = datetime.now()
    
    # 上传图片到飞书（如果有图片）
    image_key = None
    if image_path and os.path.exists(image_path):
        image_key = upload_image_to_feishu(image_path, token)
    
    # 构建飞书交互式卡片
    elements = []
    
    # 添加图片（如果有）
    if image_key:
        elements.append({
            "tag": "img",
            "img_key": image_key,
            "alt": {"tag": "plain_text", "content": "手机行业晨报配图"}
        })
    
    # 添加新闻和头部信息
    elements.extend([
        {"tag": "div", "text": {"content": f"**📅 {today.strftime('%Y年%m月%d日')} | {today.strftime('%A')}**\n🌤️ 天气：{weather}", "tag": "lark_md"}},
        {"tag": "hr"},
        {"tag": "div", "text": {"content": "**🔥 头条新闻**", "tag": "lark_md"}}
    ])
    
    # 添加新闻（10 条）
    for i, news in enumerate(news_items[:10], 1):
        elements.append({
            "tag": "div",
            "text": {"content": f"**{i}. {news['title']}**\n\n{news['content']}\n\n👉 [查看详情]({news['url']})", "tag": "lark_md"}
        })
        elements.append({"tag": "hr"})
    
    elements.append({"tag": "div", "text": {"content": "**💡 每日洞察**\n\n> \"手机行业每天都在变化，保持关注才能抓住机会\"", "tag": "lark_md"}, "style": {"background_style": "grey"}})
    elements.append({"tag": "action", "actions": [{"tag": "button", "text": {"content": "✅ 已收到", "tag": "plain_text"}, "type": "primary"}]})
    
    card_content = {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "blue",
            "title": {"content": f"📱 手机行业晨报 - {today.strftime('%m月%d日')}", "tag": "plain_text"}
        },
        "elements": elements
    }
    
    # 发送卡片消息（使用 chat_id 发送到一人部门群）
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"receive_id": TARGET_CHAT_ID, "msg_type": "interactive", "content": json.dumps(card_content)}
    
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    result = resp.json()
    if result.get("code") == 0:
        print("✅ 飞书卡片推送成功")
        return True
    else:
        print(f"❌ 飞书推送失败：{result}")
        return False



def main():
    print("🦞 开始生成晨报（实时数据版 + 本地配图）...")
    
    # 生成晨报内容
    content, news_items, weather = generate_morning_report()
    
    # 获取今日配图（循环使用 5 张本地图片）
    print("\n🎨 获取晨报配图...")
    image_path = get_today_image()
    
    # 保存文件
    save_to_file(content)
    
    # 发送飞书卡片（带配图）
    send_to_feishu_card(news_items, weather, image_path)
    
    print("✅ 晨报生成完成！")


if __name__ == "__main__":
    main()
