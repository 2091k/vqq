import os
import jinja2
import requests
from bs4 import BeautifulSoup


def get_first_image_url(query):
    url = f"https://www.baidu.com/s?ie=UTF-8&wd={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 定位搜索结果中的图片模块（通常在含有图片的搜索结果条目中）
        image_containers = soup.find_all('div', class_='c-container')
        for container in image_containers:
            # 查找以 txx.baidu.com 开头的图片标签
            img_tag = container.find('img', src=lambda x: x and x.startswith('https://t') and 'baidu.com' in x)
            if img_tag:
                img_url = img_tag.get('src')
                return img_url

        # 若未找到，尝试直接搜索所有以 txx.baidu.com 开头的 img 标签
        img_tags = soup.find_all('img', src=lambda x: x and x.startswith('https://t') and 'baidu.com' in x)
        if img_tags:
            return img_tags[0]['src']
        return None
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None


# 定义模板
html_template = """
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
            text-align: center;
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
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .episode {
            text-align: center;
            position: relative;
        }

        .episode a {
            display: block;
            text-decoration: none;
            color: var(--text-color);
        }

        .episode img {
            width: 100%;
            height: auto;
            object-fit: contain;
            border-radius: 8px;
            margin-bottom: 10px;
        }

        .episode .video-name {
            position: absolute;
            bottom: 10px;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.7);
            padding: 5px;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .episode-btn {
            display: none;
        }

        @media (min-width: 768px) {
            .container {
                max-width: 1200px;
                margin: 90px auto 0;
                padding: 20px;
            }

            .episodes {
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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
        <h1 class="title">{{ title }}</h1>
    </div>

    <div class="container">
        <div class="source-tabs">
            {% for source in sources %}
            <button class="source-tab" onclick="showSource('{{ source }}')">{{ source }} ({{ sources[source]|length }})</button>
            {% endfor %}
        </div>

        {% for source in sources %}
        <div class="episodes" id="{{ source }}" style="display: none;">
            {% for episode in sources[source] %}
            <div class="episode">
                <a href="{{ episode.url }}">
                    <img src="{{ episode.image_url }}" alt="{{ episode.name }} 封面">
                    <div class="video-name">{{ episode.name }}</div>
                </a>
            </div>
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

        // 默认显示第一个源
        window.onload = () => {
            const firstTab = document.querySelector('.source-tab');
            if (firstTab) firstTab.click();
        };
    </script>
</body>

</html>
"""


# 定义视频类
class Video:
    def __init__(self, name, url, image_url):
        self.name = name
        self.url = url
        self.image_url = image_url


# 查找视频文件
def find_videos(base_dir):
    sources = {}
    categories = ['电影', '电视剧', '动漫']
    for category in categories:
        category_dir = os.path.join(base_dir, category)
        if os.path.exists(category_dir):
            videos = []
            for root, _, files in os.walk(category_dir):
                for file in files:
                    if file.endswith(('.html', '.mp4', '.avi', '.mkv')):
                        video_url = os.path.join(root, file).replace('\\', '/')
                        video_name = os.path.splitext(file)[0]
                        image_url = get_first_image_url(video_name)
                        if not image_url:
                            image_url = "https://picsum.photos/200/300"
                        video = Video(video_name, video_url, image_url)
                        videos.append(video)
            if videos:
                sources[category] = videos
    return sources


# 生成 HTML 文件
def generate_html(sources):
    template = jinja2.Template(html_template)
    html_content = template.render(title="视频在线播放", sources=sources)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == "__main__":
    base_dir = '.'
    sources = find_videos(base_dir)
    generate_html(sources)
    print("HTML 文件已生成：index.html")
    