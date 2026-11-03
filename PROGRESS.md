# 進度紀錄 — Wei's Portfolio

更新：2026-11-03

## 已完成
- 從 WordPress（weilee01.com）搬出 37 件作品、292 張圖，轉成靜態網站（`build.py` 產生 `public/`）。
- 設計定版（目前 `main`）：深色底、橘色 `#F4A711` 輔助色、履歷網站同款字體（Instrument Serif / Geist Mono / Noto Serif TC）、紙紋與飄移格線。
- 首頁：「Wei's Portfolio.」大標、拿相機直式照片（`photo/` 原檔，`public/assets/img/wei-camera.webp`）、旋轉圓標、滑鼠互動（卡片傾斜反光、照片雜訊扭曲、字母上浮變橘斜體、磁吸圓鈕）。
- 作品卡片：hover 才浮現名稱與分類（手機一直顯示）；篩選時動畫重排。
- 作品內頁：標題一行（依最長標題「小瓦掃地機器人募資頁」計算字級）、分類膠囊在右上、無專案編號。
- About 頁 = `../Resume` 履歷網站，build 時自動複製、改深色與橘色、換成網站 header；自我介紹第二段改用桌面 `李建緯_WeiLee_Resume.jpg` 的版本。
- 所有橘底 hover 一律黑字。CSS/JS 網址帶內容雜湊（避免快取舊檔）。
- 後台設定 `.pages.yml`（Pages CMS）已寫好：可編作品（標題、slug、分類、封面、作品圖、中英文介紹、外部連結）與首頁文字。
- GitHub：私人 repo https://github.com/taiwankiss/wei-portfolio 已推上。
- Pages CMS 已授權並實測存檔（2026-11-03）。rich-text 欄位設 `format: html`（預設會把全部介紹改存成 Markdown）；CMS 存檔會用 `<strong>`、段落間不換行，`content/projects.json` 已統一成這個格式。
- Cloudflare Pages 專案 `wei-portfolio` 已上線：https://wei-portfolio.pages.dev ，push 到 `main`（含後台存檔）會自動重新部署。注意建立時要走「Pages」而不是「Workers」流程（Workers 流程會多一欄 `npx wrangler deploy`）。

## 分支
- `main`：目前定版（= `about-style`）
- `light`：淺色版（米色底、粗體無襯線）
- `dark-theme`：深色、粗體無襯線版
- `about-style`：同 `main`

## 下一步
1. **網域**：把 weilee01.com 的 DNS 移到 Cloudflare（在 Hostinger 改 nameserver），於 Pages 加上自訂網域；確認上線後再取消 Hostinger 方案。
2. 從後台上傳的新圖片不會自動壓縮 — 若常上傳，可在 `build.py` 加自動縮圖。

## 重要檔案
- `content/projects.json`（格式 `{"projects": [...]}`，包一層才能讓後台收合並顯示作品名）、`content/site.json`：內容
- `build.py`：產生網站、複製履歷成 About（找不到 `../Resume` 時保留現有 `public/about-me/`）
- `public/assets/style.css`、`public/assets/main.js`：樣式與互動
- `public/_redirects`、`public/_headers`：Cloudflare 轉址與快取
- `.pages.yml`：後台設定
- `photo/`：hero 原始照片（不進 git）
