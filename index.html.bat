<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>魏无羡影院 - 在线视频播放</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <style>
        :root {
            --primary-color: #ff6b6b;
            --bg-color: #2d3436;
            --text-color: #ffffff;
        }
		/* —— 顶部分类 Tab —— */
.category-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  overflow-x: auto;
}
.category-tab {
  padding: 8px 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-color);
  border: none;
  cursor: pointer;
  transition: background 0.3s, transform 0.3s;
}
.category-tab.active {
  background: var(--primary-color);
}
	/* —— 新增 Spinner 样式 —— */
    .spinner-overlay {
      position: fixed;
      top: 0; left: 0;
      width: 100%; height: 100%;
      background: rgba(45,52,54,0.5);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 2000;
    }
    .spinner {
      width: 50px;
      height: 50px;
      border: 6px solid rgba(255,255,255,0.3);
      border-top-color: var(--primary-color);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
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
    /* 新增遮罩层样式 */
    .search-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(8px);  /* 减少遮罩层模糊度 */
        z-index: 998;  /* 层级在弹窗之下 */
        display: none;
    }

    /* 修改搜索弹窗样式 */
    .search-modal {
        display: none;
        position: fixed;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        max-width: 500px;
        padding: 30px;
        border-radius: 20px;
        background: rgb(45 52 54 / 0%); /* 使用主题背景色 */
        backdrop-filter: blur(30px); /* 加强弹窗自身模糊 */
        z-index: 999; /* 确保在遮罩层之上 */
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        opacity: 0;
        transition: all 0.3s ease;
    }

    .search-modal.active {
        display: block;
        opacity: 1;
        animation: modalSlideIn 0.3s ease;
    }

    @keyframes modalSlideIn {
        from {
            transform: translate(-50%, -60%);
            opacity: 0;
        }
        to {
            transform: translate(-50%, -50%);
            opacity: 1;
        }
    }

    .search-modal input {
        width: 100%;
        padding: 15px 25px;
        margin-bottom: 20px;
        border: none;
        border-radius: 50px;
        background: rgba(255, 255, 255, 0.9);
        color: #2d3436;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .search-modal input:focus {
        outline: none;
        background: rgba(255, 255, 255, 1);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    .search-modal button {
        width: 100%;
        padding: 15px;
        background: linear-gradient(135deg, #ff6b6b 0%, #ff4747 100%);
        color: white;
        border: none;
        border-radius: 50px;
        cursor: pointer;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }

    .search-modal button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }

    .search-modal button:active {
        transform: translateY(0);
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
		/* 公告遮罩层 */
.notice-overlay {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(8px);
    z-index: 1500;
    display: none;
}

/* 公告弹窗 */
.notice-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgb(255 255 255 / 19%);
    backdrop-filter: blur(15px);
    color: white;
    padding: 30px;
    border-radius: 20px;
    width: 90%;
    max-width: 400px;
    z-index: 1501;
    display: none;
    text-align: center;
    box-shadow: 0 6px 30px rgba(0, 0, 0, 0.4);
    animation: fadeIn 0.5s ease;
}

.notice-modal h2 {
    font-size: 1.5rem;
    margin-bottom: 15px;
}

.notice-modal p {
    font-size: 1rem;
    margin-bottom: 20px;
}

.notice-modal button {
    padding: 10px 25px;
    border: none;
    border-radius: 25px;
    background: var(--primary-color);
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.3s;
}

.notice-modal button:hover {
    background: #ff4c4c;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translate(-50%, -60%); }
    to { opacity: 1; transform: translate(-50%, -50%); }
}

    </style>
    <link rel="icon" href="https://v.qq.com/favicon.ico">
</head>
<body>
    <div class="header">
        <a href="http://vqq.2091k.cn" style="display:flex;align-items:center;">            <svg id="custom-logo" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
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
            </svg></a>
        <h1 class="title">魏无羡影院</h1>
        <button class="search-button" onclick="openSearchModal()">🔍</button>
    </div>

    <div class="search-overlay" id="search-overlay" onclick="closeSearchModal()"></div>
    <div class="search-modal" id="search-modal">
        <input type="text" id="search-input" placeholder="🔍 输入影片名称...">
        <button onclick="performSearch()">立即搜索</button>
    </div>

	
	<div class="container" id="main-container">
  <!-- 顶部分类 Tab 挂载点 -->
  <div class="category-tabs" id="category-tabs"></div>
  <!-- 列表区挂载点 -->
  <div id="video-lists"></div>
  </div>

    <div class="spinner-overlay" id="spinner-overlay"><div class="spinner"></div></div>

    <script>
        // 两个 API
  const PROXY_BASE = 'https://jasu.2091k.cn/';
  const NEWTV_BASE  = 'https://jasu.2091k.cn/https://newtv.2091k.cn/';
  const DATA = {};   // 存放拿到的两类列表

  function showSpinner()   { document.getElementById('spinner-overlay').style.display = 'flex'; }
  function hideSpinner()   { document.getElementById('spinner-overlay').style.display = 'none'; }
  function showError(msg)  { alert(msg); }

  // 拉数据并初始化 tab + 默认渲染
  async function init() {
    showSpinner();
    try {
      // 并行拉电影和电视剧
      const [movies, tvs] = await Promise.all([
        fetchHome('电影'),
        fetchHome('电视剧')
      ]);
      DATA['电影']  = movies;
      DATA['电视剧'] = tvs;

      renderTabs();              // 生成顶部分类按钮
      switchCategory('电影');    // 默认显示电影
    } catch (e) {
      console.error(e);
      showError('列表加载失败');
    } finally {
      hideSpinner();
    }
  }

  // 通用 fetchHome，返回规范数据
  async function fetchHome(type) {
    const url = encodeURIComponent(`https://vqqadmin.2091k.cn/?type=${type}&page=1`);
    const res = await fetch(PROXY_BASE + url);
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    return data.map(item => ({
      vod_id:      item.id,
      vod_name:    item.title,
      vod_pic:     item.img,
      vod_feature: item.path
    }));
  }

  // 渲染顶部分类按钮
  function renderTabs() {
    const tabs = document.getElementById('category-tabs');
    tabs.innerHTML = '';
    Object.keys(DATA).forEach(type => {
      const btn = document.createElement('button');
      btn.className = 'category-tab';
      btn.textContent = `${type} (${DATA[type].length})`;
      btn.onclick = () => switchCategory(type);
      tabs.appendChild(btn);
    });
  }

  // 点击切换分类
  function switchCategory(type) {
    // 高亮
    document.querySelectorAll('.category-tab').forEach(btn => {
      btn.classList.toggle('active', btn.textContent.startsWith(type));
    });
    // 渲染对应列表
    renderList(DATA[type]);
  }

  // 渲染影片卡片
// 修改renderList函数中的点击处理
function renderList(list) {
  const wrap = document.getElementById('video-lists');
  wrap.innerHTML = '';
  const grid = document.createElement('div');
  grid.className = 'episodes';

  list.forEach(item => {
    const ep = document.createElement('div');
    ep.className = 'episode';
    ep.innerHTML = `
      <img src="${item.vod_pic.replace('http://','https://')}"
           onerror="this.src='https://placehold.co/195x260?text=封面加载失败'">
      <div class="video-name">${item.vod_name}</div>`;

    ep.onclick = () => {
      try {
        // 核心优化：简化的路径处理逻辑
        const currentPath = window.location.pathname
          .replace(/\/index\.html$/i, '')  // 移除index.html
          .replace(/\/$/, '');             // 移除末尾斜杠

        // 路径标准化处理
        const featurePath = (item.vod_feature || '')
          .replace(/^\/*/, '')    // 移除开头斜杠
          .replace(/\/*$/, '');   // 移除结尾斜杠

        // 使用URL对象自动处理路径拼接
        const targetUrl = new URL(
          `${currentPath}/${featurePath}`,
          window.location.origin
        );

        window.location.href = targetUrl.href;
      } catch (error) {
        console.error('跳转失败:', error);
        alert('路径错误，请联系管理员');
      }
    };

    grid.appendChild(ep);
  });

  wrap.appendChild(grid);
}
        // ===== 搜索功能 =====
        async function performSearch() {
            const keyword = document.getElementById('search-input').value.trim();
            if (!keyword) { showError('请输入搜索内容'); return; }
            showSpinner();
            try {
                const res = await fetch(`${NEWTV_BASE}?keyword=${encodeURIComponent(keyword)}`);
                if (!res.ok) throw new Error(res.status);
                const data = await res.json();
                if (!data.list || !data.list.length) { showError('未找到相关内容'); return; }
                renderSearchResults(data.list);
            } catch (err) {
                console.error(err); showError('搜索失败: ' + err.message);
            } finally { hideSpinner(); closeSearchModal(); }
        }

        function renderSearchResults(list) {
            const container = document.getElementById('main-container'); container.innerHTML = '';
            const div = document.createElement('div'); div.className = 'episodes'; div.id = 'search-results';
            list.forEach(item => {
                const ep = document.createElement('div'); ep.className = 'episode';
                ep.innerHTML = `
                    <img src="${item.vod_pic}" onerror="this.src='https://placehold.co/195x260?text=封面加载失败'">
                    <div class="video-name">${item.vod_name}</div>`;
                ep.onclick = () => loadDetail(item.vod_id);
                div.appendChild(ep);
            });
            container.appendChild(div);
        }

        // ===== 详情加载 & 播放 =====
        async function loadDetail(id) {
            showSpinner();
            try {
                const res = await fetch(`${NEWTV_BASE}?id=${encodeURIComponent(id)}`);
                if (!res.ok) throw new Error(res.status);
                const data = await res.json();
                const info = data.list && data.list[0]; if (!info) throw new Error('无视频数据');
                const playerData = { title: info.vod_name, playFrom: info.vod_play_from.split('|'), playUrl: info.vod_play_url.split('$$$').map(g=>g.split('|').map(p=>{const [n,u]=p.split('$');return{name:n,url:u};})), cover: info.vod_pic };
                const key = 'playerData_' + Date.now(); localStorage.setItem(key, JSON.stringify(playerData));
                window.location.href = `player.html?key=${key}`;
            } catch (err) { console.error(err); showError('加载详情失败: ' + err.message); }
            finally { hideSpinner(); }
        }

        // ===== 弹窗 & 初始 =====
        function openSearchModal(){document.getElementById('search-overlay').style.display='block';document.getElementById('search-modal').classList.add('active');setTimeout(()=>document.getElementById('search-input').focus(),100);}        
        function closeSearchModal(){document.getElementById('search-overlay').style.display='none';document.getElementById('search-modal').classList.remove('active');}
        document.addEventListener('keydown',e=>e.key==='Escape'&&closeSearchModal());
        window.addEventListener('DOMContentLoaded',init);
		  // 回车触发搜索
  const input = document.getElementById('search-input');
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      performSearch();
    }
  });
    </script>
	<!-- 公告遮罩层 -->
<div class="notice-overlay" id="noticeOverlay"></div>

<!-- 公告弹窗 -->
<div class="notice-modal" id="noticeModal">
  <h2>📢 公告</h2>
  <p>本站资源均采集自网络，仅供学习交流，切勿用于商业用途。如有侵权，请及时联系删除。</p>
  <p>• 添加全网搜索功能</p>
  <button onclick="closeNotice()">我知道了</button>
</div>
<script>
  window.addEventListener('load', () => {
    const noticeOverlay = document.getElementById('noticeOverlay');
    const noticeModal = document.getElementById('noticeModal');
    // 显示公告
    noticeOverlay.style.display = 'block';
    noticeModal.style.display = 'block';
  });

  function closeNotice() {
    document.getElementById('noticeOverlay').style.display = 'none';
    document.getElementById('noticeModal').style.display = 'none';
  }
</script>

</body>
</html>
