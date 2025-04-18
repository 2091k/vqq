addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

const BASE_URL = 'http://www.cbbnb.com';
const DEFAULT_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Safari/537.36',
  'Referer': BASE_URL + '/'
};

async function handleRequest(request) {
  try {
    const url = new URL(request.url);
    const keyword = url.searchParams.get('keyword');
    if (!keyword) {
      return new Response(JSON.stringify({ error: '请提供 keyword 参数。例如: ?keyword=棋士' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json;charset=UTF-8' }
      });
    }

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

    // 提取所有视频 ID（更宽松正则匹配所有 view/*.html 链接）
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

    const vodList = await Promise.all(uniqueIds.map(crawlDetail));
    const validVodList = vodList.filter(item => item);

    const result = {
      code: 1,
      msg: '数据列表',
      page: 1,
      pagecount: 1,
      limit: '20',
      total: validVodList.length,
      list: validVodList
    };

    return new Response(JSON.stringify(result, null, 2), {
      headers: { 'Content-Type': 'application/json;charset=UTF-8' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: '发生未知错误' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json;charset=UTF-8' }
    });
  }
}

async function crawlDetail(videoId) {
  try {
    const url = `${BASE_URL}/view/${videoId}.html`;
    const resp = await fetch(url, { headers: DEFAULT_HEADERS });
    if (!resp.ok) return null;
    const html = await resp.text();

    let title = '未知剧集';
    const titleMatch = html.match(/<title>(.*?)<\/title>/);
    if (titleMatch) {
      const raw = titleMatch[1];
      const extracted = raw.split('《')[1]?.split('》')[0] || raw;
      title = extracted.replace(/电视剧|电影|动漫/g, '').trim();
    }

    const picMatch = html.match(/data-original="([^"]+)"/);
    const vodPic = picMatch ? picMatch[1] : '';

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
              const realUrl = await extractRealUrl(epPath);
              episodes.push({
                name: epName,
                url: realUrl || null
              });
            }
          }
        }
        sources[sourceName] = episodes;
      }
    }

    const vodPlayFrom = Object.keys(sources).join('|');
    const vodPlayUrl = Object.values(sources)
      .map(list => list.map(ep => `${ep.name}$${ep.url || ''}`).join('|'))
      .join('$$$');

    return {
      vod_id: videoId,
      vod_name: title,
      vod_play_from: vodPlayFrom,
      vod_play_url: vodPlayUrl,
      vod_pic: vodPic,
  
    };
  } catch (err) {
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
    return null;
  }
}
