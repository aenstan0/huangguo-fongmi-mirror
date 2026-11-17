#!/usr/bin/env python3
# 把官方 SikROo/huangguo-spider 的旧格式 QuickJS 脚本(dong步 req / export default 对象)
# 转换成新版 FongMi QuickJS 可用的格式(async + class extends Spider)。
# 用法: python3 scripts/convert.py
# 成功后写 dist/huangguo_web_spider.js；node --check 不过则退出非0(不覆盖线上)。
import re, sys, urllib.request, subprocess, os, tempfile

UPSTREAM = "https://raw.githubusercontent.com/SikROo/huangguo-spider/main/huangguo_web_spider.js"
OUT = os.path.join(os.path.dirname(__file__), "..", "dist", "huangguo_web_spider.js")

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")

def convert(src: str) -> str:
    # 必须在旧脚本自己的模态里: 顶部引入 Spider/net，注入同步->异步
    s = "import {Spider, net} from 'catvod';\n" + src

    # 内部工具函数(会发网络)前面的调用改成 await，声明改成 async
    helpers = ['reqJson', 'getJson', 'getSiteJson', 'archivesVideoId', 'archivesVideoUrl',
               'postSiteJson', 'postVideos', 'listPage']
    for n in helpers:
        s = re.sub(r'(?<![\w])' + n + r'\(', 'await ' + n + '(', s)
        s = s.replace('function await ' + n + '(', 'async function ' + n + '(')

    # 旧全局同步 req -> 新异步 net.req
    s = s.replace('const r = req(u, opts);', 'const r = await net.req(u, opts);')
    # 源站域名跟随(旧域名常失效)
    s = s.replace("const SITE = 'https://huangguoai.com';", "const SITE = 'https://huangguoai.io';")

    # 旧 export default { home(){} ... } -> 内部 object，再包新 class
    s = s.replace('export default {', 'const __legacy = {')
    for n in ['home', 'homeVod', 'category', 'search', 'detail', 'play']:
        s = re.sub(r'(?m)^  ' + n + r'\(', '  async ' + n + '(', s)

    s += r'''
function __decode(v) { return typeof v === 'string' ? JSON.parse(v) : v; }
export default class HuangguoSpider extends Spider {
  init(ext) { let cfg = ext; if (typeof ext === 'string') { try { cfg = JSON.parse(ext); } catch (e) { cfg = {}; } } if (__legacy.init) __legacy.init(cfg || {}); }
  async homeContent(filter) { return __decode(await __legacy.home(filter)); }
  async homeVideoContent() { return __decode(await __legacy.homeVod()); }
  async categoryContent(tid, pg, filter, extend) { return __decode(await __legacy.category(tid, pg, filter, extend)); }
  async searchContent(key, quick, pg) { return __decode(await __legacy.search(key, quick, pg)); }
  async detailContent(ids) { return __decode(await __legacy.detail(Array.isArray(ids) ? ids[0] : ids)); }
  async playerContent(flag, id, flags) { return __decode(await __legacy.play(flag, id, flags)); }
}
'''
    return s

def check(js: str) -> bool:
    # node --check 需要合法 module：占位符/import 用临时文件
    with tempfile.NamedTemporaryFile('w', suffix='.mjs', delete=False) as f:
        f.write(js)
        p = f.name
    try:
        r = subprocess.run(['node', '--check', p], capture_output=True, text=True)
        if r.returncode != 0:
            print("SYNTAX FAIL:\n", r.stderr[-800:], file=sys.stderr)
        return r.returncode == 0
    finally:
        os.unlink(p)

def main():
    print("fetching upstream ...")
    src = fetch(UPSTREAM)
    print("upstream bytes:", len(src))
    out = convert(src)
    if not check(out):
        print("convert failed syntax check; keep existing dist", file=sys.stderr)
        sys.exit(1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print("wrote", OUT, len(out), "bytes")

if __name__ == "__main__":
    main()
