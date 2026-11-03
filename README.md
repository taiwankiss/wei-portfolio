# Wei's Portfolio

從 WordPress（weilee01.com）搬出來的靜態作品集，部署在 GitHub + Cloudflare Pages。

## 結構

```
content/projects.json   37 件作品：標題、分類、中英文介紹、封面與圖片路徑
content/site.json       個人資料、經歷、技能（About 頁）
build.py                從 content/ 產生 public/ 裡的 HTML（不需安裝任何套件）
public/                 實際上線的網站
  media/<slug>/         各作品圖片（WebP；動圖為 MP4）
  assets/               style.css、main.js、logo、大頭照
  _redirects            舊 WordPress 網址轉址（Cloudflare Pages 讀取）
  _headers              快取設定
```

## 修改內容

1. 改 `content/*.json`（新增作品：把圖片放進 `public/media/<slug>/`，在 `projects.json` 加一筆）
2. 執行 `python3 build.py`
3. 本機預覽：`python3 -m http.server 8787 -d public` → http://localhost:8787
4. `git commit` + `git push`，Cloudflare Pages 會自動重新部署

## Cloudflare Pages 設定

- Framework preset：None
- Build command：（留空）
- Build output directory：`public`

網址維持舊站格式（`/portfolio/<slug>/`、`/about-me/`），所以舊連結和 Google 索引都不會壞。
