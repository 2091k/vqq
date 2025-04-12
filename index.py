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

        # 定位搜索结果中的主要内容区域（可根据百度页面结构调整）
        main_content = soup.find('div', id='content_left')  # 百度搜索结果主区域
        if not main_content:
            main_content = soup  # 若找不到，使用整个页面

        # 查找所有标签中符合条件的src属性（不限于img标签）
        def is_valid_src(tag):
            src = tag.get('src')
            return src and src.startswith('https://t') and 'baidu.com' in src

        # 先在搜索结果的主要容器中查找
        for container in main_content.find_all('div', class_='c-container'):
            target = container.find(is_valid_src)  # 查找第一个符合条件的标签
            if target:
                return target['src']

        # 若未找到，在整个页面中查找所有符合条件的src
        all_matching = main_content.find_all(is_valid_src)
        if all_matching:
            return all_matching[0]['src']  # 返回第一个匹配的链接

        return None
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None


# 从 img.txt 文件中读取视频名称和图片链接
def read_image_urls_from_file():
    image_urls = {}
    if os.path.exists('img.txt'):
        try:
            # 尝试以 utf-8 编码读取文件
            with open('img.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # 如果 utf-8 解码失败，尝试以 gbk 编码读取文件
            with open('img.txt', 'r', encoding='gbk') as f:
                lines = f.readlines()
        for i in range(0, len(lines), 2):
            video_name = lines[i].strip()
            image_url = lines[i + 1].strip() if i + 1 < len(lines) else None
            if video_name and image_url:
                image_urls[video_name] = image_url
    return image_urls


# 定义模板
html_template = """
<!DOCTYPE html>
<html>

<head>
    <title>{{ title }} - 在线视频播放</title>
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
    image_urls = read_image_urls_from_file()
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
                        image_url = image_urls.get(video_name)
                        if not image_url:
                            image_url = get_first_image_url(video_name)
                        if not image_url:
                            image_url = "https://picsum.photos/200/300"
                        # 获取文件修改时间
                        file_mtime = os.path.getmtime(video_url)
                        video = Video(video_name, video_url, image_url)
                        videos.append((file_mtime, video))
            # 按文件修改时间排序，最新的放在最前面
            videos.sort(key=lambda x: x[0], reverse=True)
            # 只保留 Video 对象
            videos = [video for _, video in videos]
            if videos:
                sources[category] = videos
    return sources


# 生成 HTML 文件
def generate_html(sources):
    template = jinja2.Template(html_template)
    html_content = template.render(title="魏无羡影院", sources=sources)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == "__main__":
    base_dir = '.'
    sources = find_videos(base_dir)
    generate_html(sources)
    print("HTML 文件已生成：index.html")
    