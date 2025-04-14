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
url = 'http://www.cbbnb.com/view/35170.html#'
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
    <title>{{ title }} - 魏无羡影院在线播放</title>
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
            background: #808080; /* 源高亮用灰色 */
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

        .episode-btn.active {
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
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?d69e07b9eec7a81616400c95de2448f4";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
})();
</script>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PG5zMDpzdmcgeG1sbnM6bnMwPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiB2aWV3Qm94PSIwIDAgMzIgMzIiIGZpbGw9Im5vbmUiPjxuczA6ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfMjY1XzIyMykiPjxuczA6cGF0aCBkPSJNNi4xMjI1IDIzLjUwMjhDNi44MDEgMjguMDc4NiA3LjYxMjMzIDMxLjUxOCAxMi45MDM0IDI5LjgwNTRDMTcuOTc3OCAyOC4xNzA1IDIyLjg2MDEgMjUuMjY0NCAyNy4xNDc3IDIxLjk3MDFDMjguNjg0NSAyMC42NTE5IDMxLjM2MzggMTguNzkyMiAzMS40MTY5IDE2LjYwNzVDMzEuMzYzOCAxNC40MTQ2IDI4LjY4NDUgMTIuNTYzMSAyNy4xNDc3IDExLjI0MjlDMjIuODU2IDcuOTQ4NTEgMTcuOTc3OCA1LjA0ODU1IDEyLjkwMzQgMy40MDU0NUM3LjYxMjMzIDEuNjk2OTUgNi44MDEgNS4xMzg0OCA2LjEyMjUgOS43MTAxNEM1LjU5NTIzIDE0LjI5MjYgNS41OTUyMyAxOC45MjA0IDYuMTIyNSAyMy41MDI4WiIgZmlsbD0iIzAwOThGRiIgLz48bnMwOnBhdGggZD0iTTEuNTA1NCAxMC41NjQxQzIuMDg1OCA3LjUzNzQzIDIuOTU2NCA1LjM0MDQ5IDYuODU3NzUgNi4wOTQ2QzYuNTIwNzYgNy4yNzkxOCA2LjI3NDgxIDguNDg3NzggNi4xMjIwMyA5LjcwOTg0QzUuNTk2ODEgMTQuMjkyNCA1LjU5NjgxIDE4LjkxOTkgNi4xMjIwMyAyMy41MDI1QzYuMjc2MDEgMjQuNzI0NCA2LjUyMTk0IDI1LjkzMjkgNi44NTc3NSAyNy4xMTc3QzIuOTU4NDQgMjcuODcxOCAyLjA4Nzg0IDI1LjY3NDkgMS41MDU0IDIyLjY0ODJMMS40NjQ1MiAyMi40MzE2TDEuMzg2ODggMjEuOTk0M0MwLjg5NjQzMiAxOC40MTg5IDAuODk2NDMyIDE0Ljc5MzQgMS4zODY4OCAxMS4yMTgxTDEuNDY0NTIgMTAuNzgwN0wxLjUwNTQgMTAuNTY0MVoiIGZpbGw9IiNGRjg4MDAiIC8+PG5zMDpwYXRoIGQ9Ik02Ljg1ODIxIDYuMDkyNzdDNy4xMjc5OCA2LjE0NTkxIDcuNDE0MDkgNi4yMTEzMSA3LjcyODgxIDYuMjk3MTRDMTIuNDYxOSA3LjU3ODUxIDE3LjAyMTMgOS44NDQ5MyAyMS4wMjQ5IDEyLjQxNzlDMjIuNDU1NCAxMy40NDk5IDI0Ljk1NjkgMTQuODk2OSAyNS4wMDU5IDE2LjYwOTRDMjQuOTU2OSAxOC4zMjIgMjIuNDUzNCAxOS43Njg5IDIxLjAyNDkgMjAuNzk4OUMxNy4wMjEzIDIzLjM3MTkgMTIuNDYxOSAyNS42NDA0IDcuNzI4ODEgMjYuOTE5N0M3LjQ0MjIxIDI3LjAwMjMgNy4xNTE2NSAyNy4wNzA2IDYuODU4MjEgMjcuMTI0MUM2LjUyMTQzIDI1LjkzODggNi4yNzU0OCAyNC43Mjk1IDYuMTIyNSAyMy41MDY4QzUuNTk1MjMgMTguOTI0NCA1LjU5NTIzIDE0LjI5NjYgNi4xMjI1IDkuNzE0MTRDNi4yNzU2MiA4LjQ5OTM0IDYuNTE5NSA3LjI5NzcxIDYuODUyMDkgNi4xMTkzNEw2Ljg1ODIxIDYuMDkyNzdaIiBmaWxsPSIjNDNFNzAwIiAvPjxuczA6cGF0aCBkPSJNOS42NTAwNyAxMi4yNTg1QzkuNjUwMDcgMTIuMjU4NSA5LjM1OTg2IDEyLjcyODYgOS4zNTk4NiAxNi42MTU2QzkuMzU5ODYgMjAuNTAyNiA5LjY1MDA3IDIwLjk0ODIgOS42NTAwNyAyMC45NDgyQzkuNzQ4MTcgMjEuNDMwNSA5Ljk0MDI3IDIxLjU4MzcgMTAuNDY3NSAyMS40NjExQzEwLjQ2NzUgMjEuNDYxMSAxMS4zMzgxIDIxLjMyNjIgMTQuODE2NCAxOS41NTY0QzE4LjI5NDcgMTcuNzg2NiAxOC44NzUxIDE3LjExODMgMTguODc1MSAxNy4xMTgzQzE5LjI0OTEgMTYuNzQwMyAxOS4zNDkzIDE2LjQ4ODkgMTguODc1MSAxNi4wOTY1QzE4Ljg3NTEgMTYuMDk2NSAxNy45MTg3IDE1LjIxMzYgMTQuODE2NCAxMy42MDUzQzExLjcxNDIgMTEuOTk2OSAxMC40Njc1IDExLjc0NTYgMTAuNDY3NSAxMS43NDU2QzEwLjA0MDQgMTEuNjIyOSA5Ljc2NDUyIDExLjc2MTkgOS42NTAwNyAxMi4yNTg1WiIgZmlsbD0id2hpdGUiIC8+PC9uczA6Zz48bnMwOmRlZnM+PG5zMDpjbGlwUGF0aCBpZD0iY2xpcDBfMjY1XzIyMyI+PG5zMDpyZWN0IHdpZHRoPSIxMjQiIGhlaWdodD0iMTI2IiBmaWxsPSJ3aGl0ZSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMSAyLjczNzc5KSIgLz48L25zMDpjbGlwUGF0aD48L25zMDpkZWZzPjwvbnMwOnN2Zz4=">
</head>

<body>
    <div class="header">
        <a href="../index.html">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" width="24" height="24">
    <path fill="gray" d="M575.8 255.5c0 18-15 32.1-32 32.1h-32l.7 160.2c0 2.7-.2 5.4-.5 8.1V472c0 22.1-17.9 40-40 40H456c-1.1 0-2.2 0-3.3-.1c-1.4 .1-2.8 .1-4.2 .1H416 392c-22.1 0-40-17.9-40-40V448 384c0-17.7-14.3-32-32-32H256c-17.7 0-32 14.3-32 32v64 24c0 22.1-17.9 40-40 40H160 128.1c-1.5 0-3-.1-4.5-.2c-1.2 .1-2.4 .2-3.6 .2H104c-22.1 0-40-17.9-40-40V360c0-.9 0-1.9 .1-2.8V287.6H32c-18 0-32-14-32-32.1c0-9 3-17 10-24L266.4 8c7-7 15-8 22-8s15 2 21 7L564.8 231.5c8 7 12 15 11 24z"/>
</svg>    
        </a>
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
            <button class="episode-btn" onclick="playVideo('{{ episode.url }}', this)">{{ episode.name }}</button>
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
            // 切换源时移除所有集数按钮的高亮
            document.querySelectorAll('.episode-btn').forEach(btn => btn.classList.remove('active'));
        }

        function playVideo(url, btn) {
            const player = document.getElementById('player');
            player.src = url;
            player.scrollIntoView({ behavior: 'smooth' });
            // 移除所有集数按钮的高亮
            document.querySelectorAll('.episode-btn').forEach(btn => btn.classList.remove('active'));
            // 为当前点击的集数按钮添加高亮
            btn.classList.add('active');
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

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 拼接保存文件的完整路径
file_name = f"{title}.html"
save_path = os.path.join(current_dir, file_name)

with open(save_path, 'w', encoding='utf-8') as f:
    f.write(template.render(title=title, sources=sources))

print(f"播放页面已生成: {save_path}")    