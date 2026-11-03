# Wei's Portfolio

從 WordPress（weilee01.com）搬出來的靜態作品集，部署在 GitHub + Cloudflare Pages。

## 結構

```
content/projects.json   作品：標題、分類、中英文介紹、封面與圖片路徑
content/site.json       首頁文字、Email、所在地
build.py                從 content/ 產生 public/ 裡的 HTML，並複製履歷網站成 About 頁（不需安裝套件）
.pages.yml              後台（Pages CMS）設定
public/                 實際上線的網站
  media/<slug>/         各作品圖片（WebP；動圖為 MP4）
  assets/               style.css、main.js、logo、大頭照
  _redirects            舊 WordPress 網址轉址（Cloudflare Pages 讀取）
  _headers              快取設定
```

## 修改內容

**後台（建議）**：到 https://app.pagescms.org 用 GitHub 登入、選這個 repo，就能新增／編輯作品、上傳圖片、改首頁文字。
存檔會直接 commit 到 GitHub，Cloudflare Pages 自動重新建置，約 1 分鐘後上線。設定在 `.pages.yml`。

從後台上傳的圖片會原檔上線，建議先輸出成寬 1800px 以內的 JPG/WebP 再上傳。

**手動**：
1. 改 `content/*.json`
2. 執行 `python3 build.py`
3. 本機預覽：`python3 -m http.server 8787 -d public` → http://localhost:8787
4. `git commit` + `git push`

**About 頁**是 `../Resume` 履歷網站的複本：`build.py` 找得到那個資料夾時會重新複製一次（改成網站的橘色、換成網站的 header）。改完履歷後在本機跑一次 `python3 build.py` 再 push。

## Cloudflare Pages 設定

- Framework preset：None
- Build command：`python3 build.py`
- Build output directory：`public`

網址維持舊站格式（`/portfolio/<slug>/`、`/about-me/`），所以舊連結和 Google 索引都不會壞。
