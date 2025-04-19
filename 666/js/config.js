// js/config.js
// 跨域加速地址（可选，若 API 无需代理可忽略）
var PROXY_BASE = 'https://cors.zme.ink/';

// 搜索 API 组列表（每组包含关键词搜索和 ID 详情 API）
var SEARCH_API_GROUPS = [
  {
    name: '主站',
    keywordApi: 'https://newtv.2091k.cn/?keyword=',
    idApi: 'https://newtv.2091k.cn/?id='
  },
  {
    name: '备用站', 
    keywordApi: 'https://66tyyszy.com/api.php/provide/vod/?ac=videolist&wd=',
    idApi: 'https://66tyyszy.com/api.php/provide/vod/?ac=detail&ids='
  }
];