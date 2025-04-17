addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

const BASE_URL = 'http://www.cbbnb.com';
const DEFAULT_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Safari/537.36',
  'Referer': BASE_URL + '/'
};

async function handleRequest(request) {
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

  // 提取所有视频 ID
  const ids = [...searchHtml.matchAll(/href=\"\/view\/(\d+)\.html\"/g)].map(m => m[1]);
  const uniqueIds = Array.from(new Set(ids));

  // 无ID情况直接返回空数据
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

  const vodList = [];

  for (const vid of uniqueIds) {
    const item = await crawlDetail(vid);
    if (item) vodList.push(item);
  }

  const result = {
    code: 1,
    msg: '数据列表',
    page: 1,
    pagecount: 1,
    limit: '20',
    total: vodList.length,
    list: vodList
  };

  return new Response(JSON.stringify(result, null, 2), {
    headers: { 'Content-Type': 'application/json;charset=UTF-8' }
  });
}

async function crawlDetail(videoId) {
  const url = `${BASE_URL}/view/${videoId}.html`;
  const resp = await fetch(url, { headers: DEFAULT_HEADERS });
  if (!resp.ok) return null;
  const html = await resp.text();

  let title = '未知剧集';
  const ti = html.match(/<title>([\s\S]*?)<\/title>/);
  if (ti) {
    const raw = ti[1];
    const extracted = raw.split('《')[1]?.split('》')[0] || raw;
    title = extracted.replace(/电视剧|电影|动漫/g, '').trim();
  }

  const pic = html.match(/data-original=\"([^\"]+)\"/);
  const vodPic = pic ? pic[1] : '';

  const sources = {};
  const RE_UL = /<ul[^>]*class=["'][^"']*nav-tabs[^"']*["'][^>]*>([\s\S]*?)<\/ul>/;
  const RE_LI = /<li[^>]*>[\s\S]*?<a[^>]*href=["']#([^"']+)["'][^>]*>([^<]+)<\/a>[\s\S]*?<\/li>/g;
  const RE_PLAYLIST = /<ul[^>]*class=["'][^"']*stui-content__playlist[^"']*["'][^>]*>([\s\S]*?)<\/ul>/;
  const RE_EP = /<a[^>]*href=["']([^"']+)["'][^>]*>([^<]+)<\/a>/g;

  const ulMatch = html.match(RE_UL);
  if (ulMatch) {
    const ulContent = ulMatch[1];
    let liMatch;
    while ((liMatch = RE_LI.exec(ulContent))) {
      const tabId = liMatch[1];
      const sourceName = liMatch[2].trim();
      const divRegex = new RegExp(`<div[^>]*id=["']${tabId}["'][^>]*>([\\s\\S]*?)<\\/div>`);
      const divMatch = html.match(divRegex);
      if (divMatch) {
        const block = divMatch[1];
        const playMatch = block.match(RE_PLAYLIST);
        if (playMatch) {
          const listBlock = playMatch[1];
          let epMatch;
          const eps = [];
          while ((epMatch = RE_EP.exec(listBlock))) {
            const epPath = epMatch[1];
            const epName = epMatch[2].trim();
            const epUrl = await extractRealUrl(epPath);
            if (epUrl) eps.push({ name: epName, url: epUrl });
          }
          if (eps.length) sources[sourceName] = eps;
        }
      }
    }
  }

  return {
    vod_id: videoId,
    vod_name: title,
    vod_play_from: Object.keys(sources).join('|'),
    vod_play_url: Object.values(sources)
      .map(list => list.map(ep => `${ep.name}$${ep.url}`).join('|'))
      .join('$$$'),
    vod_pic: vodPic
  };
}

async function extractRealUrl(path) {
  try {
    const resp = await fetch(BASE_URL + path, { headers: DEFAULT_HEADERS });
    if (!resp.ok) return null;
    const txt = await resp.text();
    const playbox = txt.match(/<div id=["']playbox["'][\s\S]*?<iframe[^>]+src=["']([^"']+)["']/);
    return playbox ? playbox[1] : null;
  } catch (e) {
    return null;
  }
}
