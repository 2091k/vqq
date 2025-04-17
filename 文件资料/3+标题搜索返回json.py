import sys
import requests
from urllib.parse import quote
import re
from bs4 import BeautifulSoup
import json
import os


def main_crawl(video_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://www.cbbnb.com/'
    }
    base_url = "http://www.cbbnb.com"
    session = requests.Session()

    def extract_real_video_url(episode_path):
        full_url = f"{base_url}{episode_path}"
        try:
            response = session.get(full_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"请求失败: {full_url} 状态码: {response.status_code}")
                return None
            soup = BeautifulSoup(response.text, 'html.parser')
            playbox_div = soup.find('div', id='playbox')
            if playbox_div:
                iframe = playbox_div.find('iframe')
                if iframe and iframe.get('src'):
                    video_url = iframe['src']
                    print(f"成功提取视频地址: {video_url}")
                    return video_url
            print(f"未找到视频iframe: {full_url}")
            return None
        except Exception as e:
            print(f"提取视频地址异常: {str(e)}")
            return None

    url = f'http://www.cbbnb.com/view/{video_id}.html'
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        title = soup.title.get_text().split('《')[-1].split('》')[0]
        keywords = ["电视剧", "电影", "动漫"]
        for keyword in keywords:
            title = title.replace(keyword, "")
    except:
        title = "未知剧集"

    # 提取封面地址
    cover_img = soup.find('img', {'data-original': True})
    if cover_img:
        vod_pic = cover_img['data-original']
    else:
        vod_pic = ""

    sources = {}
    source_tabs = soup.select('ul.nav.nav-tabs.pull-right li')

    for tab in source_tabs:
        source_name = tab.get_text(strip=True)
        target_id = tab.a['href'].replace('#', '')
        container = soup.find('div', id=target_id)
        if container:
            episodes = []
            for a in container.select('ul.stui-content__playlist a'):
                episode_path = a['href']
                video_url = extract_real_video_url(episode_path)
                if video_url:
                    episodes.append({'name': a.get_text(strip=True), 'url': video_url})
            if episodes:
                sources[source_name] = episodes

    # 构建符合 CMS API 格式的 JSON 数据
    vod = {
        "vod_id": video_id,
        "vod_name": title,
        "vod_play_from": "|".join(sources.keys()),
        "vod_play_url": "$$$".join([
            "|".join([f"{ep['name']}${ep['url']}" for ep in episodes])
            for episodes in sources.values()
        ]),
        "vod_pic": vod_pic
    }
    return vod


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请按格式输入: python 1.py 关键词 (例如: python 1.py 棋士)")
        sys.exit(1)

    keyword = sys.argv[1]
    search_url = "http://www.cbbnb.com/search.php"
    encoded_keyword = quote(keyword, encoding='utf-8')
    payload = f"searchword={encoded_keyword}"

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 14; MEIZU 20 Pro Build/UKQ1.230917.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.135 Mobile Safari/537.36",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'Accept-Encoding': "gzip, deflate",
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "max-age=0",
        'Origin': "http://www.cbbnb.com",
        'Upgrade-Insecure-Requests': "1",
        'X-Requested-With': "mark.via",
        'Referer': "http://www.cbbnb.com/",
        'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",

    }

    response = requests.post(search_url, data=payload, headers=headers)
    html_content = response.text

    pattern = r'href="/view/(\d+)\.html"'
    video_ids = re.findall(pattern, html_content)
    if not video_ids:
        print("未找到视频ID")
        sys.exit(1)

    # …（前面部分保持不变）…

    vod_list = []
    for idx, video_id in enumerate(video_ids, 1):
        print(f"找到第 {idx} 个视频ID: {video_id}, 开始爬取详细信息…")
        vod = main_crawl(video_id)
        vod_list.append(vod)

    # —— 在这里增加去重逻辑 —— 
    # 用 vod_id 作为 key，后出现的同 id 会覆盖前一个，达到去重效果
    unique_dict = { vod['vod_id']: vod for vod in vod_list }
    deduped_list = list(unique_dict.values())

    # 构建最终的 JSON 数据
    result = {
        "code": 1,
        "msg": "数据列表",
        "page": 1,
        "pagecount": 1,
        "limit": "20",
        "total": len(deduped_list),        # 用去重后的数量
        "list": deduped_list               # 用去重后的列表
    }

    # 输出 JSON 数据
    print(json.dumps(result, ensure_ascii=False, indent=4))

    