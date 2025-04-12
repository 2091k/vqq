import requests
from bs4 import BeautifulSoup
from jinja2 import Template
import os

# 配置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'http://www.cbbnb.com/'
}

base_url = "http://www.cbbnb.com"
session = requests.Session()  # 保持会话

def extract_real_video_url(episode_path):
    """从剧集详情页提取真实视频地址"""
    full_url = f"{base_url}{episode_path}"
    try:
        response = session.get(full_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"请求失败: {full_url} 状态码: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        # 定位播放器iframe
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

# 主爬取流程
url = 'http://www.cbbnb.com/view/34758.html#'
response = session.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 提取电视剧标题
try:
    title = soup.title.get_text().split('《')[-1].split('》')[0]
    # 移除关键词
    keywords = ["电视剧", "电影", "动漫"]
    for keyword in keywords:
        title = title.replace(keyword, "")
except:
    title = "未知剧集"

sources = {}
# 定位播放源选项卡
source_tabs = soup.select('ul.nav.nav-tabs.pull-right li')

for tab in source_tabs:
    source_name = tab.get_text(strip=True)
    target_id = tab.a['href'].replace('#', '')
    container = soup.find('div', id=target_id)

    if container:
        episodes = []
        # 提取所有剧集链接
        for a in container.select('ul.stui-content__playlist a'):
            episode_path = a['href']
            video_url = extract_real_video_url(episode_path)
            if video_url:
                episodes.append({
                    'name': a.get_text(strip=True),
                    'url': video_url
                })
        if episodes:
            sources[source_name] = episodes

# 调试输出
print(f"成功提取的源数量: {len(sources)}")
for name, eps in sources.items():
    print(f"源 [{name}] 包含有效剧集数: {len(eps)}")

# 使用Jinja2模板生成响应式页面
template = Template('''
<!DOCTYPE html>
<html>

<head>
    <title>{{ title }} - 在线播放</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <style>
        :root {
            --primary-color: #ff6b6b;
            --bg-color: #2d3436;
            --text-color: #ffffff;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
        }

        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(45, 52, 54, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        }

        .header a {
            font-size: 1.5rem;
            color: var(--primary-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-decoration: none;
            position: absolute;
            left: 1rem;
        }

        .title {
            font-size: 1.5rem;
            color: var(--primary-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .container {
            margin-top: 70px;
            padding: 15px;
        }

        .source-tabs {
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        .source-tab {
            flex-shrink: 0;
            padding: 8px 20px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-color);
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }

        .source-tab.active {
            background: var(--primary-color);
            color: white;
        }

        .episodes {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }

        .episode-btn {
            padding: 8px 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-color);
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .episode-btn:hover {
            background: var(--primary-color);
        }

        #player-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            margin-top: 20px;
            border-radius: 12px;
            overflow: hidden;
            background: #000;
        }

        #player {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }

        @media (min-width: 768px) {
            .container {
                max-width: 1200px;
                margin: 90px auto 0;
                padding: 20px;
            }

            .episodes {
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            }

            .source-tabs {
                flex-wrap: wrap;
                overflow-x: visible;
            }
        }
    </style>
</head>

<body>
    <div class="header">
        <a href="../index.html">主页</a>
        <h1 class="title">{{ title }}</h1>
    </div>

    <div class="container">
        <div id="player-container">
            <iframe id="player" allowfullscreen></iframe>
        </div>
        <br>
        <div class="source-tabs">
            {% for source in sources %}
            <button class="source-tab" onclick="showSource('{{ source }}')">{{ source }} ({{ sources[source]|length }})</button>
            {% endfor %}
        </div>

        {% for source in sources %}
        <div class="episodes" id="{{ source }}" style="display: none;">
            {% for episode in sources[source] %}
            <button class="episode-btn" onclick="playVideo('{{ episode.url }}')">{{ episode.name }}</button>
            {% endfor %}
        </div>
        {% endfor %}

    </div>

    <script>
        function showSource(sourceName) {
            document.querySelectorAll('.episodes').forEach(div => div.style.display = 'none');
            document.getElementById(sourceName).style.display = 'grid';
            document.querySelectorAll('.source-tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
        }

        function playVideo(url) {
            const player = document.getElementById('player');
            player.src = url;
            player.scrollIntoView({ behavior: 'smooth' });
        }

        // 默认显示第一个源
        window.onload = () => {
            const firstTab = document.querySelector('.source-tab');
            if (firstTab) firstTab.click();
        };

        // 横竖屏适配
        window.addEventListener("resize", () => {
            const player = document.getElementById('player');
            player.style.height = player.offsetWidth * 9 / 16 + 'px';
        });
    </script>
</body>

</html>
''')

# 拼接保存文件的完整路径
file_name = f"{title}.html"
save_path = os.path.join('/sdcard/download/py/', file_name)

with open(save_path, 'w', encoding='utf-8') as f:
    f.write(template.render(title=title, sources=sources))

print(f"播放页面已生成: {save_path}")
    