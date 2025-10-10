addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

const BASE_URL = 'http://www.qiyoudy4.com';
const DEFAULT_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Safari/537.36',
  'Referer': BASE_URL + '/'
};

async function handleRequest(request) {
  try {
    const url = new URL(request.url);
    const keyword = url.searchParams.get('keyword');
    const id = url.searchParams.get('id');
    const episodePath = url.searchParams.get('episodePath');

    if (id && episodePath) {
      const realUrl = await extractRealUrl(episodePath);
      return new Response(JSON.stringify({
        code: 1,
        url: realUrl || null
      }, null, 2), {
        headers: { 'Content-Type': 'application/json;charset=UTF-8' }
      });
    }

    if (id) {
      const detail = await crawlDetail(id);
      if (!detail) {
        return new Response(JSON.stringify({ error: '未找到对应ID的数据' }), {
          status: 404,
          headers: { 'Content-Type': 'application/json;charset=UTF-8' }
        });
      }
      return new Response(JSON.stringify({
        code: 1,
        msg: '数据详情',
        list: [detail]
      }, null, 2), {
        headers: { 'Content-Type': 'application/json;charset=UTF-8' }
      });
    }

    if (keyword) {
      const searchUrl = BASE_URL + '/search.php';
      const form = new URLSearchParams();
      form.set('searchword', keyword);

      const searchResp = await fetch(searchUrl, {
        method: 'POST',
        headers: {
          ...DEFAULT_HEADERS,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: form.toString()
      });
      const searchHtml = await searchResp.text();

      const ids = [...searchHtml.matchAll(/href=["']\/view\/(\d+)\.html["']/g)].map(m => m[1]);
      const uniqueIds = Array.from(new Set(ids));

      if (uniqueIds.length === 0) {
        return new Response(JSON.stringify({
          code: 1,
          msg: '没有找到相关数据',
          page: 1,
          pagecount: 1,
          limit: '20',
          total: 0,
          list: []
        }, null, 2), {
          headers: { 'Content-Type': 'application/json;charset=UTF-8' }
        });
      }

      const list = await Promise.all(uniqueIds.map(async (vid) => {
        const url = `${BASE_URL}/view/${vid}.html`;
        const resp = await fetch(url, { headers: DEFAULT_HEADERS });
        if (!resp.ok) {
          return {
            vod_id: vid,
            vod_name: '',
            vod_pic: '',
            vod_type: '',
            vod_area: '',
            vod_year: '',
            vod_actor: '',
            vod_director: '',
            vod_content: '',
            vod_play_from: '',
            vod_play_url: ''
          };
        }
        const html = await resp.text();

        // 提取基本信息
        const info = extractVideoInfo(html);
        
        return {
          vod_id: vid,
          vod_name: info.title,
          vod_pic: info.vod_pic,
          vod_type: info.vod_type,
          vod_area: info.vod_area,
          vod_year: info.vod_year,
          vod_actor: info.vod_actor,
          vod_director: info.vod_director,
          vod_content: info.vod_content,
          vod_play_from: '',
          vod_play_url: ''
        };
      }));

      const result = {
        code: 1,
        msg: '数据列表',
        page: 1,
        pagecount: 1,
        limit: '20',
        total: list.length,
        list
      };
      return new Response(JSON.stringify(result, null, 2), {
        headers: { 'Content-Type': 'application/json;charset=UTF-8' }
      });
    }

    return new Response(JSON.stringify({ error: '请提供 keyword 或 id 参数。例如: ?keyword=棋士 或 ?id=36010' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json;charset=UTF-8' }
    });
  } catch (error) {
    console.error('发生未知错误:', error);
    return new Response(JSON.stringify({ error: `发生未知错误: ${error.message}` }), {
      status: 500,
      headers: { 'Content-Type': 'application/json;charset=UTF-8' }
    });
  }
}

// 提取视频信息的函数
function extractVideoInfo(html) {
  let title = '未知剧集';
  const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/);
  if (titleMatch) title = titleMatch[1].trim();

  const picMatch = html.match(/data-original=["']([^"']+)["']/);
  const vodPic = picMatch ? picMatch[1] : '';

  // 匹配类型、地区、年份
  let vod_type = '', vod_area = '', vod_year = '';
  const dataBlock = html.match(/<p[^>]*class=["']data["'][^>]*>([\s\S]*?)<\/p>/);
  if (dataBlock) {
    const block = dataBlock[1];
    const typeMatch = block.match(/类型：<\/span>\s*<a[^>]*>([^<]+)<\/a>/);
    const areaMatch = block.match(/地区：<\/span>\s*([^<]+)/);
    const yearMatch = block.match(/年份：<\/span>\s*([^<]+)/);
    vod_type = typeMatch ? typeMatch[1].trim() : '';
    vod_area = areaMatch ? areaMatch[1].trim() : '';
    vod_year = yearMatch ? yearMatch[1].trim() : '';
  }

  // 主演
  let vod_actor = '';
  const actorMatch = html.match(/<span[^>]*>主演：<\/span>\s*([^<]+)/);
  if (actorMatch) vod_actor = actorMatch[1].trim();

  // 导演
  let vod_director = '';
  const directorMatch = html.match(/<span[^>]*>导演：<\/span>\s*([^<]+)/);
  if (directorMatch) vod_director = directorMatch[1].trim();

  // 简介
  let vod_content = '';
  const descMatch = html.match(/<span[^>]*>简介：<\/span>\s*([^<]+)/);
  if (descMatch) vod_content = descMatch[1].replace(/详情.*/, '').trim();

  return {
    title,
    vod_pic: vodPic,
    vod_type,
    vod_area,
    vod_year,
    vod_actor,
    vod_director,
    vod_content
  };
}


async function crawlDetail(videoId) {
  try {
    const url = `${BASE_URL}/view/${videoId}.html`;
    const resp = await fetch(url, { headers: DEFAULT_HEADERS });
    if (!resp.ok) return null;
    const html = await resp.text();

    // 使用提取函数获取基本信息
    const info = extractVideoInfo(html);

    const sources = {};
    const tabUlMatch = html.match(/<ul[^>]*class=["'][^"']*nav-tabs[^"']*["'][^>]*>([\s\S]*?)<\/ul>/);
    const tabLiRegex = /<li[^>]*>[\s\S]*?<a[^>]*href=["']#([^"']+)["'][^>]*>([^<]+)<\/a>[\s\S]*?<\/li>/g;
    if (tabUlMatch) {
      const ulContent = tabUlMatch[1];
      let liMatch;
      while ((liMatch = tabLiRegex.exec(ulContent))) {
        const tabId = liMatch[1];
        const sourceName = liMatch[2].trim();
        const divBlockRegex = new RegExp(`<div[^>]*id=["']${tabId}["'][^>]*>([\\s\\S]*?)<\\/div>`);
        const divMatch = html.match(divBlockRegex);
        const episodes = [];
        if (divMatch) {
          const blockHtml = divMatch[1];
          const playlistMatch = blockHtml.match(/<ul[^>]*class=["'][^"']*playlist[^"']*["'][^>]*>([\s\S]*?)<\/ul>/);
          if (playlistMatch) {
            const listHtml = playlistMatch[1];
            const episodeRegex = /<a[^>]*href=["']([^"']+)["'][^>]*>([^<]+)<\/a>/g;
            let epMatch;
            while ((epMatch = episodeRegex.exec(listHtml))) {
              const epPath = epMatch[1];
              const epName = epMatch[2].trim();
              episodes.push({ name: epName, path: epPath });
            }
          }
        }
        sources[sourceName] = episodes;
      }
    }

    const vodPlayFrom = Object.keys(sources).join('|');
    const vodPlayUrl = Object.values(sources)
      .map(list => list.map(ep => `${ep.name}$${ep.path}`).join('|'))
      .join('$$$');

    return {
      vod_id: videoId,
      vod_name: info.title,
      vod_pic: info.vod_pic,
      vod_type: info.vod_type,
      vod_area: info.vod_area,
      vod_year: info.vod_year,
      vod_actor: info.vod_actor,
      vod_director: info.vod_director,
      vod_content: info.vod_content,
      vod_play_from: vodPlayFrom,
      vod_play_url: vodPlayUrl
    };
  } catch (err) {
    console.error('crawlDetail 发生错误:', err);
    return null;
  }
}

async function extractRealUrl(path) {
  try {
    const fullUrl = path.startsWith('http') ? path : BASE_URL + path;
    const resp = await fetch(fullUrl, { headers: DEFAULT_HEADERS });
    if (!resp.ok) return null;
    const text = await resp.text();
    const match = text.match(/<div id=["']playbox["'][\s\S]*?<iframe[^>]+src=["']([^"']+)["']/);
    if (!match) return null;
    const src = match[1];
    return src.startsWith('http') ? src : BASE_URL + src;
  } catch (err) {
    console.error('extractRealUrl 发生错误:', err);
    return null;
  }
}
