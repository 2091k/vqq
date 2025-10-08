export default {
  async fetch(request, env, ctx) {
    return await handleRequest(request, env);
  }
}

const REPO_OWNER = '2091k';
const REPO_NAME = 'vqq';
const PAGE_SIZE = 36; // 修改分页大小为36

// 修改：同时返回cover列表（顺序）以及映射
async function fetchCoverData() {
  const res = await fetch('https://vqqimg.2091k.cn/', {
    headers: {
      'User-Agent': 'Cloudflare-Worker'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch image list JSON');
  const coverList = await res.json();
  const coverMap = {};
  for (const item of coverList) {
    coverMap[item.title] = item.img;
  }
  return { coverList, coverMap };
}

async function fetchFiles(directory, token) {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${encodeURIComponent(directory)}`;
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Cloudflare-Worker'
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch files from GitHub: ${response.statusText}`);
  }

  return await response.json();
}

function getQueryParam(url, key, defaultValue = '') {
  const parsed = new URL(url);
  return parsed.searchParams.get(key) || defaultValue;
}

async function handleRequest(request, env) {
  try {
    const url = new URL(request.url);
    const type = getQueryParam(request.url, 'type', '电视剧');
    const page = parseInt(getQueryParam(request.url, 'page', '1'), 10);
    const validTypes = ['电视剧', '电影', '动漫'];

    if (!validTypes.includes(type)) {
      return new Response('Invalid type parameter', { status: 400 });
    }

    // 获取cover数据及其顺序
    const { coverList, coverMap } = await fetchCoverData();
    const list = await fetchFiles(type, env.GITHUB_TOKEN);

    let files = [];

    for (const file of list) {
      const title = file.name.replace('.html', '');
      const img = coverMap[title] || '';
      files.push({
        title,
        path: `${type}/${file.name}`,
        img,
        // 保留原来的created_at字段（如果后续有其它用途）
        created_at: file.git_url ? file.git_url.match(/\/commits\/(.+)$/)?.[1] : ''
      });
    }

    // 新的排序：依据 coverList 中的 title 顺序排序
    // 如果 coverList 中存在对应 title，则按照 coverList 的索引排序
    // 如果不在 coverList 中，则排在后面，按标题字母顺序排列
    files.sort((a, b) => {
      const indexA = coverList.findIndex(item => item.title === a.title);
      const indexB = coverList.findIndex(item => item.title === b.title);
      if (indexA === -1 && indexB === -1) {
        return a.title.localeCompare(b.title);
      }
      if (indexA === -1) {
        return 1; // a 未在coverList中，排后面
      }
      if (indexB === -1) {
        return -1;
      }
      return indexA - indexB;
    });

    // 分页处理，每页最多显示36个条目，page=1显示第1~36个
    const start = (page - 1) * PAGE_SIZE;
    const paginated = files.slice(start, start + PAGE_SIZE);

    return new Response(JSON.stringify(paginated), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (e) {
    return new Response(`Error: ${e.message}`, { status: 500 });
  }
}
