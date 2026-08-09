export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    // 判断路径必须以 /img.txt 结尾，严格匹配后缀
    if (!url.pathname.endsWith('/img.txt')) {
      return new Response('Not Found', { status: 404 });
    }

    // 从环境变量中获取 GitHub Token
    const token = env.YOU_GITHUB_TOKEN;
    const owner = '2091k';
    const repo = 'vqq';
    const imgPath = 'img.txt';

    const headers = {
      'User-Agent': 'Cloudflare-Worker',
      'Accept': 'application/vnd.github.v3+json',
      'Authorization': `token ${token}`
    };

    // 获取 img.txt 文件
    const imgRes = await fetch(`https://raw.githubusercontent.com/${owner}/${repo}/main/${imgPath}`, { headers });

    if (!imgRes.ok) {
      return new Response('Error fetching img.txt', { status: 500 });
    }

    // 获取文件内容
    const imgBuffer = await imgRes.arrayBuffer();

    // 解码
    const text = new TextDecoder('utf-8').decode(imgBuffer);

    // 打印文件内容到 Worker 的日志中
    console.log(text);

    // 解析文件内容
    const imgList = [];
    const lines = text.split(/\r?\n/); // 按行分割文本
    for (let i = 0; i < lines.length - 1; i += 2) {
      const title = lines[i].trim(); // 影片标题
      const img = lines[i + 1].trim(); // 对应的封面链接
      if (title && img) {
        imgList.push({ title, img });
      }
    }

    return new Response(JSON.stringify(imgList, null, 2), {
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
