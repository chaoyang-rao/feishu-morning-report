#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 晨报配图选择器
循环使用 5 张本地图片，每天自动轮换
"""

import os
import json
from datetime import datetime

# 配置
IMAGE_DIR = "/Users/Zhuanz1/.openclaw/workspace-assistant/images"
STATE_FILE = os.path.join(IMAGE_DIR, ".配图状态.json")

# 5 张配图列表（按顺序循环）
IMAGES = [
    "晨报配图 -1.png",
    "晨报配图 -2.png",
    "晨报配图 -3.png",
    "晨报配图 -4.png",
    "晨报配图 -5.png",
]


def get_last_used_index():
    """获取上次使用的图片索引"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('last_index', -1)
        except:
            pass
    return -1


def save_current_index(index):
    """保存当前使用的图片索引"""
    data = {
        'last_index': index,
        'last_date': datetime.now().strftime('%Y-%m-%d'),
        'image': IMAGES[index]
    }
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_today_image():
    """
    获取今日配图
    返回图片本地路径
    """
    # 获取上次使用的索引
    last_index = get_last_used_index()
    
    # 计算今日索引（循环 +1）
    today_index = (last_index + 1) % len(IMAGES)
    
    # 获取图片路径
    image_name = IMAGES[today_index]
    image_path = os.path.join(IMAGE_DIR, image_name)
    
    # 检查图片是否存在
    if not os.path.exists(image_path):
        print(f"⚠️ 图片不存在：{image_path}，使用备用图片")
        # 使用第一张存在的图片
        for img in IMAGES:
            path = os.path.join(IMAGE_DIR, img)
            if os.path.exists(path):
                image_path = path
                image_name = img
                break
    
    # 保存当前索引
    save_current_index(today_index)
    
    print(f"🖼️ 今日配图：{image_name} (第{today_index + 1}张)")
    return image_path


if __name__ == "__main__":
    # 测试
    image_path = get_today_image()
    print(f"✅ 配图路径：{image_path}")
