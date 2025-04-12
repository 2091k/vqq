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

# 显示提取的源数量
source_count = len(sources)
print(f"成功提取的源数量: {source_count}")
for source, episodes in sources.items():
    print(f"源 [{source}] 包含有效剧集数: {len(episodes)}")

# 使用Jinja2模板生成响应式页面（美化版本）
template = Template('''
<!DOCTYPE html>
<html>

<head>
    <title>{{ title }} - 在线播放</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #ff6b6b;
            --bg-color: #2d3436;
            --text-color: #ffffff;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
        }

        .source-tab.active {
            background-color: var(--primary-color);
            color: white;
        }

        .episode-btn.active {
            background-color: var(--primary-color);
        }

        /* 优化播放器在手机端的显示 */
        @media (max-width: 768px) {
            .aspect-video {
                aspect-ratio: 16 / 9;
                height: auto;
            }
            /* 调整手机端文字大小 */
            .source-tab,
            .episode-btn {
                font-size: 0.875rem; 
                padding: 0.25rem 0.5rem; 
            }
            h1 {
                font-size: 1.25rem; 
            }
            p {
                font-size: 0.875rem; 
            }
        }
    </style>
</head>

<body>
    <!-- 头部导航 -->
    <header class="fixed top-0 w-full bg-[rgba(45,52,54,0.95)] backdrop-blur-md p-4 shadow-md z-10 flex items-center justify-center gap-4">
        <a href="../index.html" class="text-gray-400 text-xl whitespace-nowrap overflow-hidden text-ellipsis absolute left-4">
            <i class="fa-solid fa-house"></i> 主页
        </a>
        <h1 class="text-xl font-bold text-[var(--primary-color)] whitespace-nowrap overflow-hidden text-ellipsis">{{ title }}</h1>
    </header>

    <!-- 内容容器 -->
    <main class="mt-20 p-4 md:max-w-4xl md:mx-auto md:mt-24 md:p-6">
        <!-- 显示提取的源数量 -->
        <p class="text-gray-400 mb-4">源数量: {{ source_count }}</p>
        <!-- 视频播放器 -->
        <div class="relative w-full aspect-video rounded-xl overflow-hidden bg-black mb-4">
            <iframe id="player" class="absolute top-0 left-0 w-full h-full border-0" allowfullscreen></iframe>
        </div>

        <!-- 播放源标签 -->
        <div class="flex gap-2 overflow-x-auto pb-2 mb-4">
            {% for source in sources %}
            <button class="source-tab px-4 py-2 rounded-full bg-[rgba(255,255,255,0.1)] text-white border-0 cursor-pointer transition-all" onclick="showSource('{{ source }}')">{{ source }} ({{ sources[source]|length }})</button>
            {% endfor %}
        </div>

        {% for source in sources %}
        <div class="grid grid-cols-[repeat(auto-fill,minmax(100px,1fr))] gap-2 mb-4 episodes" id="{{ source }}" style="display: none;">
            {% for episode in sources[source] %}
            <button class="episode-btn px-4 py-2 rounded-md bg-[rgba(255,255,255,0.1)] text-white cursor-pointer transition-all" onclick="playVideo('{{ episode.url }}', this)">{{ episode.name }}</button>
            {% endfor %}
        </div>
        {% endfor %}
    </main>

    <script>
        function showSource(sourceName) {
            document.querySelectorAll('.episodes').forEach(div => div.style.display = 'none');
            document.getElementById(sourceName).style.display = 'grid';
            document.querySelectorAll('.source-tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            // 清除所有剧集的高亮
            document.querySelectorAll('.episode-btn').forEach(btn => btn.classList.remove('active'));
        }

        function playVideo(url, btn) {
            const player = document.getElementById('player');
            player.src = url;
            player.scrollIntoView({ behavior: 'smooth' });
            // 添加当前剧集的高亮
            document.querySelectorAll('.episode-btn').forEach(btn => btn.classList.remove('active'));
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
   
# 拼接保存文件的完整路径
file_name = f"{title}.html"
save_path = os.path.join('/sdcard/download/py/', file_name)

with open(save_path, 'w', encoding='utf-8') as f:
    f.write(template.render(title=title, sources=sources))

print(f"播放页面已生成: {save_path}")
    