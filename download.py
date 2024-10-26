#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import requests
import os
import time
from tqdm import tqdm  # 导入tqdm库用于下载进度条
from requests.exceptions import RequestException

# 全局变量
base_download_dir = "images"

def search_images(keyword, page):
    """从百度图片搜索获取指定关键词和页码的图片 URL"""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/84.0.4147.125 Safari/537.36'
        ),
        'Referer': 'https://image.baidu.com/'
    }
    url = f"https://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={keyword}&pn={(page - 1) * 30}"
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return re.findall(r'"objURL":"(.*?)",', response.text, re.S)
    return []

def download_image(url, keyword, filename):
    """下载图片到按关键词分类的目录并显示进度条"""
    try:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/84.0.4147.125 Safari/537.36'
            ),
            'Referer': 'https://image.baidu.com/'
        }
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()

        # 为关键词创建目录
        keyword_dir = os.path.join(base_download_dir, keyword)
        os.makedirs(keyword_dir, exist_ok=True)

        filepath = os.path.join(keyword_dir, filename)
        
        # 使用tqdm显示下载进度
        total_size = int(response.headers.get('content-length', 0))
        with open(filepath, 'wb') as file, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(1024):
                file.write(chunk)
                bar.update(len(chunk))
        return f"{filename} 下载成功到 {keyword_dir}"
    except RequestException:
        return f"下载失败：{url}"

def bulk_download_images(urls, keyword):
    """批量下载指定的图片 URL 列表到按关键词分类的目录，并显示进度"""
    result = []
    for idx, url in enumerate(urls):
        filename = f"image_{idx + 1}.jpg"
        result.append(download_image(url, keyword, filename))
    return "\n".join(result)

if __name__ == '__main__':
    while True:
        user_input = input("请输入关键词（输入 'exit' 退出程序）: ")
        if user_input.lower() == 'exit':
            print("程序已退出")
            break
        else:
            page = int(input("请输入要下载的页数: "))
            for p in range(1, page + 1):
                bulk_download_images(search_images(user_input, p), user_input)
            print("下载完成！")