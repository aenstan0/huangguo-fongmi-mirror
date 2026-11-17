# huangguo-fongmi-mirror

把官方 [SikROo/huangguo-spider](https://github.com/SikROo/huangguo-spider) 的旧格式 QuickJS 脚本，
自动转换成新版 FongMi/影视TV QuickJS 可用的格式（`class extends Spider` + `await net.req`）。

- `dist/huangguo_web_spider.js`：转换后的脚本（由 Actions 每天自动更新）
- `huangguo_config.json`：影视订阅配置，`api` 指向 jsdelivr 上的 dist 脚本
- `.github/workflows/sync.yml`：每天 03:00(UTC) 拉官方最新并转换，语法校验通过才提交
- `scripts/convert.py`：转换逻辑

## 影视订阅地址（填到 设置→点播）

```
https://cdn.jsdelivr.net/gh/aenstan0/huangguo-fongmi-mirror@main/huangguo_config.json
```

把 `aenstan0/huangguo-fongmi-mirror` 换成你实际的 GitHub 用户名/仓库名即可。
