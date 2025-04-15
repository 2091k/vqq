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
        main_content = soup.find('div', id='content_left')
        if not main_content:
            main_content = soup

        # 查找所有标签中符合条件的src属性（不限于img标签）
        def is_valid_src(tag):
            src = tag.get('src')
            return src and src.startswith('https://t') and 'baidu.com' in src

        # 先在搜索结果的主要容器中查找
        for container in main_content.find_all('div', class_='c-container'):
            target = container.find(is_valid_src)
            if target:
                return target['src']

        all_matching = main_content.find_all(is_valid_src)
        if all_matching:
            return all_matching[0]['src']

        return None
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None


def read_image_urls_from_file():
    image_urls = {}
    if os.path.exists('img.txt'):
        try:
            with open('img.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open('img.txt', 'r', encoding='gbk') as f:
                lines = f.readlines()
        for i in range(0, len(lines), 2):
            video_name = lines[i].strip()
            image_url = lines[i + 1].strip() if i + 1 < len(lines) else None
            if video_name and image_url:
                image_urls[video_name] = image_url
    return image_urls


html_template = """
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
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
            font-family: Arial, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
        }

        /* 固定头部 */
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(45, 52, 54, 0.95);
            padding: 1rem;
            z-index: 1000;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .header svg {
            flex-shrink: 0;
        }

        .title {
            font-size: 1.5rem;
            margin-left: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* 搜索按钮 */
        .search-button {
            background: none;
            border: none;
            cursor: pointer;
            color: white;
            font-size: 1.2rem;
            transition: color 0.3s;
            margin-left: auto;
        }

        .search-button:hover {
            color: var(--primary-color);
        }

        /* 搜索弹窗及毛玻璃效果 */
        .search-modal {
            display: none;
            position: fixed;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 400px;
            padding: 20px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            z-index: 1001;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
        }

        .search-modal.active {
            display: block;
        }

        .search-modal input {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: none;
            border-radius: 4px;
            background: rgb(255 255 255 / 86%);
            color: #000000;
        }

        .search-modal button {
            padding: 10px 20px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.3s;
        }

        .search-modal button:hover {
            background: #ff4747;
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
            transition: background 0.3s, transform 0.3s;
        }

        .source-tab.active {
            background: var(--primary-color);
        }

        /* 视频列表 */
        .episodes {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        @media (max-width: 767px) {
            .episodes {
                grid-template-columns: repeat(3, 1fr);
            }
        }

        .episode {
            text-align: center;
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            transition: transform 0.3s;
        }

        .episode:hover {
            transform: scale(1.03);
        }

        .episode a {
            text-decoration: none;
            color: var(--text-color);
            display: block;
        }

        .episode img {
            width: 100%;
            height: auto;
            object-fit: cover;
            border-radius: 8px;
            transition: transform 0.3s;
        }

        .episode:hover img {
            transform: scale(1.05);
        }

        .episode .video-name {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.7);
            padding: 5px;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 0.9rem;
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
    <link rel="icon" href="https://v.qq.com/favicon.ico">
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?d69e07b9eec7a81616400c95de2448f4";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
})();
</script>

</head>

<body>
    <div class="header">
        <svg id="custom-logo" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
            <g clip-path="url(#clip0_265_223)">
                <path d="M6.1225 23.5028C6.801 28.0786 7.61233 31.518 12.9034 29.8054C17.9778 28.1705 22.8601 25.2644 27.1477 21.9701C28.6845 20.6519 31.3638 18.7922 31.4169 16.6075C31.3638 14.4146 28.6845 12.5631 27.1477 11.2429C22.856 7.94851 17.9778 5.04855 12.9034 3.4054C7.61233 1.69695 6.801 5.13848 6.1225 9.71014C5.59523 14.2926 5.59523 18.9204 6.1225 23.5028Z" fill="#0098FF"/>
                <path d="M1.5054 10.5641C2.0858 7.53743 2.9564 5.34049 6.85775 6.0946C6.52076 7.27918 6.27481 8.48778 6.12203 9.70984C5.59523 14.2926 5.59523 18.9199 6.12203 23.5025C6.27601 24.7244 6.52194 25.9329 6.85775 27.1177C2.95844 27.8718 2.08784 25.6749 1.5054 22.648L1.46452 22.4316L1.38688 21.9943C0.896432 18.4189 0.896432 14.7934 1.38688 11.2181L1.46452 10.7807L1.5054 10.5641Z" fill="#FF8800"/>
                <path d="M6.85821 6.09277C7.12798 6.14591 7.41409 6.21131 7.72881 6.29714C12.4619 7.57851 17.0213 9.84493 21.0249 12.4179C22.4554 13.4499 24.9569 14.8969 25.0059 16.6094C24.9569 18.322 22.4534 19.7689 21.0249 20.798C17.0213 23.3719 12.4619 25.6404 7.72881 26.9197C7.44221 27.0023 7.15165 27.0706 6.85821 27.1243C6.52143 25.9388 6.27548 24.7295 6.1225 23.5068C5.59523 18.9244 5.59523 14.2966 6.1225 9.71414C6.27562 8.49934 6.5195 7.29761 6.85209 6.11934L6.85821 6.09277Z" fill="#37E700"/>
                <path d="M9.65007 12.2585C9.65007 12.2585 9.35986 12.7286 9.35986 16.6156C9.35986 20.5026 9.65007 20.9482 9.65007 20.9482C9.74817 21.4305 9.94027 21.5837 10.4675 21.4611C10.4675 21.4611 11.3381 21.3262 14.8164 19.5564C18.2947 17.7866 18.8751 17.1183 18.8751 17.1183C19.2491 16.7403 19.3493 16.4889 18.8751 16.0965C18.8751 16.0965 17.9187 15.2136 14.8164 13.6053C11.7142 11.9969 10.4675 11.7456 10.4675 11.7456C10.0404 11.6229 9.76452 11.7619 9.65007 12.2585Z" fill="white"/>
            </g>
            <defs>
                <clipPath id="clip0_265_223">
                    <rect width="124" height="126" fill="white" transform="translate(1 2.73779)"/>
                </clipPath>
            </defs>
        </svg>
        <h1 class="title">{{ title }}</h1>
        <button class="search-button" onclick="openSearchModal()">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="#ffffff"/>
            </svg>
        </button>
    </div>

    <div class="search-modal" id="search-modal">
        <input type="text" id="search-input" placeholder="输入搜索关键词">
        <button onclick="searchVideos()">搜索</button>
    </div>

    <div class="container">
        <div class="source-tabs">
            {% for source in sources %}
            <button class="source-tab" onclick="showSource('{{ source }}')">
                {{ source }} ({{ sources[source]|length }})
            </button>
            {% endfor %}
        </div>
        {% for source in sources %}
        <div class="episodes" id="{{ source }}" style="display: none;">
            {% for episode in sources[source] %}
            <div class="episode" data-name="{{ episode.name }}" data-category="{{ source }}">
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

        function openSearchModal() {
            document.getElementById('search-modal').classList.add('active');
        }

        function closeSearchModal() {
            document.getElementById('search-modal').classList.remove('active');
        }

        function searchVideos() {
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const allEpisodes = document.querySelectorAll('.episode');
            let foundCategory = null;

            allEpisodes.forEach(episode => {
                const videoName = episode.dataset.name.toLowerCase();
                if (videoName.includes(searchTerm)) {
                    episode.style.display = 'block';
                    if (!foundCategory) {
                        foundCategory = episode.dataset.category;
                    }
                } else {
                    episode.style.display = 'none';
                }
            });

            if (foundCategory) {
                const categoryTab = Array.from(document.querySelectorAll('.source-tab'))
                    .find(tab => tab.textContent.includes(foundCategory));
                if (categoryTab) {
                    categoryTab.click();
                }
            }

            closeSearchModal();
        }

        document.addEventListener('click', function (event) {
            const searchModal = document.getElementById('search-modal');
            const searchButton = document.querySelector('.search-button');
            if (!searchModal.contains(event.target) && !searchButton.contains(event.target)) {
                closeSearchModal();
            }
        });

        // 默认显示第一个来源
        window.onload = () => {
            const firstTab = document.querySelector('.source-tab');
            if (firstTab) firstTab.click();
        };
    </script>
</body>

</html>
"""

class Video:
    def __init__(self, name, url, image_url):
        self.name = name
        self.url = url
        self.image_url = image_url


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
                        file_mtime = os.path.getmtime(video_url)
                        video = Video(video_name, video_url, image_url)
                        videos.append((file_mtime, video))
            videos.sort(key=lambda x: x[0], reverse=True)
            videos = [video for _, video in videos]
            if videos:
                sources[category] = videos
    return sources


def sort_videos_by_txt(sources):
    image_urls = read_image_urls_from_file()
    txt_order = list(image_urls.keys())
    for category in ['电影', '电视剧']:
        if category in sources:
            videos = sources[category]
            sorted_videos = []
            for name in txt_order:
                for video in videos:
                    if video.name == name:
                        sorted_videos.append(video)
                        videos.remove(video)
                        break
            sorted_videos.extend(videos)
            sources[category] = sorted_videos
    return sources


def generate_html(sources):
    template = jinja2.Template(html_template)
    html_content = template.render(title="魏无羡影院", sources=sources)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


if __name__ == "__main__":
    base_dir = '.'
    sources = find_videos(base_dir)
    sources = sort_videos_by_txt(sources)
    generate_html(sources)
    print("HTML 文件已生成：index.html")
