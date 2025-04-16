import sys
import requests
from urllib.parse import quote
import re
from bs4 import BeautifulSoup
from jinja2 import Template
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

    # 使用Jinja2模板生成页面
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
    <link rel="icon" href="https://v.qq.com/favicon.ico">
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

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = f"{title}.html"
    save_path = os.path.join(current_dir, file_name)

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(template.render(title=title, sources=sources))

    print(f"播放页面已生成: {save_path}")

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
        'Cookie': "Hm_lvt_bca0f97a5bfbba7244d2080b450a7a6e=1718420268; Hm_lpvt_bca0f97a5bfbba7244d2080b450a7a6e=1720134321; HMACCOUNT=A99877DD3807AFE9; Hm_lvt_95e474ed3079bebafe8bb81eabeaa79d=1720254587; Hm_lpvt_95e474ed3079bebafe8bb81eabeaa79d=1721017989; _ga=GA1.1.1819058507.1721344325; Hm_lvt_368d4793d70ace4b30c9f157d880fa55=1722252106; Hm_lpvt_368d4793d70ace4b30c9f157d880fa55=1722816310; Hm_lvt_02c70d8c388f2bd1465f564448222659=1723244373; Hm_lpvt_02c70d8c388f2bd1465f564448222659=1723979706; Hm_lvt_abd066ce1fdf7644bccf9684a3880263=1724107814; Hm_lpvt_abd066ce1fdf7644bccf9684a3880263=1725376803; Hm_lvt_1eabfb92210b9cb64382409b0ba63b51=1725459177; Hm_lpvt_1eabfb92210b9cb64382409b0ba63b51=1726702617; Hm_lvt_c602a7983d4e9fd290bb6a38d7b85df5=1727310152; Hm_lpvt_c602a7983d4e9fd290bb6a38d7b85df5=1728137038; Hm_lvt_d3f084809913f9ea27128f1d2f429481=1728344912; Hm_lpvt_d3f084809913f9ea27128f1d2f429481=1729607209; Hm_lvt_4095585d6a6fcfe66f0b0eb7ce221fdd=1729726551; Hm_lpvt_4095585d6a6fcfe66f0b0eb7ce221fdd=1730811568; Hm_lvt_7ce0154e85f7c04752fba118829fa930=1731025369,1731328191; _ga_62FZQRKWKM=GS1.1.1731328191.57.0.1731328191.0.0.0; Hm_lpvt_7ce0154e85f7c04752fba118829fa930=1732178947; Hm_lvt_3615dfde9e6c0d1b3d5562822fa95794=1733713226; Hm_lpvt_3615dfde9e6c0d1b3d5562822fa95794=1733983562; Hm_lvt_40166ba9331070f733b2a65333a9be65=1734105666; Hm_lpvt_40166ba9331070f733b2a65333a9be65=1735604132; Hm_lvt_9ac0ff3b8237c724c3c2acf872a2062a=1741910525; Hm_lpvt_9ac0ff3b8237c724c3c2acf872a2062a=1742114575; Hm_lvt_10340372112b7e3d43ee7c33e8eb1348=1742218669; Hm_lpvt_10340372112b7e3d43ee7c33e8eb1348=1743521078; Hm_lvt_1ce14f7f5cd05ebf8946e23b15856f75=1744038597; recente=%5B%7B%22vod_name%22%3A%22%E7%99%BD%E6%97%A5%E4%B9%8B%E4%B8%8B%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwww.cbbnb.com%2Fplay%2F30372-0-1.html%22%2C%22vod_part%22%3A%22HD%E5%9B%BD%E8%AF%AD%22%7D%2C%7B%22vod_name%22%3A%22%E6%97%A0%E5%BF%A7%E6%B8%A1%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwww.cbbnb.com%2Fplay%2F36387-0-8.html%22%2C%22vod_part%22%3A%22%E7%AC%AC9%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E5%B0%84%E9%9B%95%E8%8B%B1%E9%9B%84%E4%BC%A0%EF%BC%9A%E4%BE%A0%E4%B9%8B%E5%A4%A7%E8%80%85%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwww.cbbnb.com%2Fplay%2F35170-0-0.html%23%22%2C%22vod_part%22%3A%22%E9%AB%98%E6%B8%85%22%7D%2C%7B%22vod_name%22%3A%22%E8%90%BD%E5%87%A1%E5%B0%98%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwww.cbbnb.com%2Fplay%2F32362-0-0.html%22%2C%22vod_part%22%3A%22%E6%99%AE%E9%80%9A%E8%AF%9D%22%7D%2C%7B%22vod_name%22%3A%22%E7%8B%AE%E5%AD%90%E7%8E%8B%EF%BC%9A%E6%9C%A8%E6%B3%95%E6%B2%99%E4%BC%A0%E5%A5%87%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwww.cbbnb.com%2Fplay%2F35466-0-0.html%22%2C%22vod_part%22%3A%22HD%E4%B8%AD%E5%AD%97%22%7D%2C%7B%22vod_name%22%3A%22%E5%93%AA%E5%90%92%E4%B9%8B%E9%AD%94%E7%AB%A5%E9%99%8D%E4%B8%96%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwww.cbbnb.com%2Fplay%2F12584-0-0.html%22%2C%22vod_part%22%3A%22%E9%AB%98%E6%B8%85%22%7D%2C%7B%22vod_name%22%3A%22%E5%88%B6%E6%9A%B4%EF%BC%9A%E6%97%A0%E9%99%90%E6%9D%80%E6%9C%BA%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwww.cbbnb.com%2Fplay%2F36272-0-0.html%22%2C%22vod_part%22%3A%22HD%E4%B8%AD%E5%AD%97%22%7D%2C%7B%22vod_name%22%3A%22%E6%A3%8B%E5%A3%AB%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwww.cbbnb.com%2Fplay%2F36010-0-1.html%22%2C%22vod_part%22%3A%22%E7%AC%AC2%E9%9B%86%22%7D%5D; Hm_lpvt_1ce14f7f5cd05ebf8946e23b15856f75=1744793395"
    }

    response = requests.post(search_url, data=payload, headers=headers)
    html_content = response.text

    pattern = r'href="/view/(\d+)\.html"'
    video_ids = re.findall(pattern, html_content)
    if not video_ids:
        print("未找到视频ID")
        sys.exit(1)
    video_id = video_ids[0]

    print(f"找到视频ID: {video_id}, 开始爬取详细信息...")
    main_crawl(video_id)
    
        # 新增遍历所有视频ID的逻辑
    for idx, video_id in enumerate(video_ids, 1):
        print(f"找到第 {idx} 个视频ID: {video_id}, 开始爬取详细信息...")
        main_crawl(video_id)