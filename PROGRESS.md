# 進度紀錄 — Wei's Portfolio

更新：2026-11-24

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
- 後台新增作品實測（2026-11-04）：「Add an entry」存成 `content/projects/<slug>.json`，`date` 自動填入現在時間，網站首頁排第一；刪除後網站恢復。實測發現沒填作品圖時 CMS 會整個省略 `gallery`（`link`、`categories` 同理）、空的英文介紹存成 `<p></p>`，原本會讓 build 失敗，已在 `build.py` 的 `load_project` 補預設值。
- 首頁圓標 W：滑鼠實點會以新分頁（`target="_blank"`）開後台。
- `.pages.yml` 的 projects 已加 `subfolders: false`，後台列表不再有「新增資料夾」按鈕。
- 2026-11-05 版面調整：
  - 首頁大標改成「AI-free Portfolio.」；首頁分頁標題改讀 `content/site.json` 的 `title`（現為「AI-free Portfolio — Wei Lee」），後台「首頁設定」可改。
  - 作品卡片與作品頁圖片圓角 24px → 12px（`.card-media`、`.shot`）。
  - Helix2h Icon System（封面＋5 張）與 Helix2h Box（6 張作品圖）原本是透明 PNG 轉的 webp，已直接合成白底重存。
  - 桌機 hero 壓在一屏內（`style.css` 的 `@media (min-width: 901px)` 區塊：標題、數字依 vh 縮放，照片卡最高一屏、照片從頂端裁到胸腰）。
  - 手機 hero：照片排在最上面（`order: -1`），高度依螢幕高度算，照片＋大標題都在第一屏（375×812、375×667 實測）。
  - Ai Work（`~/Documents/WEI/Ai/Ai Portfolio`）裡本專案的 `aifree-1`、`aifree-2`、`aifree-m` 截圖和 `aifree.mp4`、`aifree-m.mp4` 錄影已換成新版面（Playwright 逐格截圖＋ffmpeg）。之後版面再大改要記得重拍。

## 分支
- `main`：目前定版（2026-11-23 起 = `taste` 改版）
- `taste`：taste-skill 改版（已合併進 main）
- `light`：淺色版（米色底、粗體無襯線）
- `dark-theme`：深色、粗體無襯線版
- `about-style`：同 `main`

## 下一步
1. **網域搬遷（✅ 2026-11-24 全部完成）**
   - ✅ Cloudflare 已加入 `weilee01.com`（Free 方案）。從 Hostinger 匯入 6 筆紀錄（`ftp` A、根網域 2 筆 A + 2 筆 AAAA、`www` CNAME 指向 `www.weilee01.com.cdn.hstgr.net`），**全部設成 DNS only（灰雲）**，讓舊 WordPress 在過渡期照常運作。沒有 MX（無網域信箱），DNSSEC 原本就是關的。
   - ✅ Hostinger 名稱伺服器已改成 `desiree.ns.cloudflare.com`、`ram.ns.cloudflare.com`（Hostinger 後台內建瀏覽器無法登入，改用 Claude in Chrome 操作）。
   - ✅ Nameserver 已生效、Cloudflare 顯示 Active（2026-11-04）。
   - ✅ Pages `wei-portfolio` →「Custom domains」已加 `weilee01.com` 與 `www.weilee01.com`。加的時候 Cloudflare 自動把根網域 2 A + 2 AAAA、`www` 的 Hostinger CNAME 換成指向 `wei-portfolio.pages.dev` 的 CNAME（Proxied）。
   - ✅ 驗證（直接對 Cloudflare IP 測）：首頁、www、作品頁、About 都 200 且內容與 pages.dev 相同；HTTPS 憑證 CN=weilee01.com；http 會 301 到 https；`_redirects` 的 `/contact/`、`/blog/*`、`/portfolio-category/:cat/`、`/portfolio/` 轉址正確。部分公共 DNS（如 1.1.1.1）當天仍快取舊的 Hostinger 紀錄，最多 48 小時內會全部更新。
   - ⏳ 還剩 `ftp` A 紀錄（145.79.25.98，指向 Hostinger）先留著（使用者決定，2026-11-04），取消 Hostinger 時再刪。
   - 注意：Cloudflare 預設開「Email Address Obfuscation」，會把頁面上的 mailto 改成 `/cdn-cgi/l/email-protection`（有 JS 時照常可點）。要關可到 weilee01.com →「Security」→「Settings」。
   - 之後：網域註冊轉移到 Cloudflare（Hostinger 取得 EPP 授權碼 → Cloudflare「Transfer Domains」→ 使用者本人付款約 US$10.44，到期日會從 2027-03-08 延到 2028-03-08）；開 Auto-renew。網域是 Hostinger 方案送的，Hostinger 續約價 146.99（幣別看起來是人民幣）。
   - ✅ 網域註冊已轉到 Cloudflare（2026-11-24 WHOIS 確認：Registrar = Cloudflare, Inc.，到期日 2028-03-08）。轉移後 5 天內 WHOIS 會顯示 `transferperiod`，屬正常。
   - ✅ Hostinger 主機方案已取消（使用者 2026-11-24 自行操作）。
   - ✅ Cloudflare DNS 的 `ftp` A 紀錄（145.79.25.98，舊 Hostinger 主機）已刪除（2026-11-24，使用者授權）。DNS 只剩 `weilee01.com`、`www` 兩筆指向 `wei-portfolio.pages.dev` 的 CNAME。網域搬遷全部完成。
2. 從後台上傳的新圖片不會自動壓縮 — 若常上傳，可在 `build.py` 加自動縮圖。

## 注意事項
- Pages CMS 改設定後第一次打開常顯示舊快取（空清單或錯誤），重新整理一兩次即可；**空清單時不要按 Save**，會蓋掉資料。
- 刪掉的頁面在 Cloudflare 邊緣快取可能還會多留一陣子（實測 `/portfolio/cms-test/` 刪除後仍短暫回 200，加 `?v=` 繞過快取則是 404）。
- Pages CMS 不支援在頂層陣列檔案上設 `collapsible`（會變成空白表單）。

## 重要檔案
- `content/projects/*.json`（一件一檔，`build.py` 依 `date` 新到舊排序）、`content/site.json`：內容
- `build.py`：產生網站、複製履歷成 About（找不到 `../Resume` 時保留現有 `public/about-me/`）
- `public/assets/style.css`、`public/assets/main.js`：樣式與互動
- `public/_redirects`、`public/_headers`：Cloudflare 轉址與快取
- `.pages.yml`：後台設定
- `photo/`：hero 原始照片（不進 git）

## 2026-11-05：/my-score 轉址
- `public/_redirects` 加了 `/my-score`、`/my-score/*` → https://my-score-share.pages.dev/ （302）。My Score 分享版已從 Hostinger 搬到 Cloudflare Pages 專案 `my-score-share`，取消 Hostinger 不會影響它。

## 2026-11-05：weilee01.com 根目錄改給 Ai Work，這個作品集搬到 /ai-free/
- Cloudflare Worker `weilee01-router`（`~/Documents/WEI/Ai/weilee01-router`，README 有完整對照表）掛在 `weilee01.com/*`、`www.weilee01.com/*`，網址列保持 weilee01.com。根目錄是 Ai Work，本站在 **weilee01.com/ai-free/**（Worker 從 wei-portfolio.pages.dev 取內容，HTML 裡 `/` 開頭的路徑自動加上 `/ai-free`）。
- 舊網址 `/portfolio/…`、`/portfolio-category/…`、`/about-me/`、`/contact/`、`/blog/…` 由 Worker 301 到 `/ai-free/…`；`/my-score` → `/myscore/`。本站 `public/_redirects` 在 weilee01.com 上已不會被用到（wei-portfolio.pages.dev 上仍有效）。
- Pages 的自訂網域 weilee01.com 沒拿掉；Worker 路由在它前面。

## 2026-11-23：taste-skill 改版（https://github.com/Leonxlnx/taste-skill）
- 字體：Instrument Serif / Noto Serif TC 全部換成 Geist（英文）＋ Noto Sans TC（中文），全站與 About 一致。
- 拿掉：「01 — 作品集」類編號小標、所有「—」破折號、飄移格線與十字記號、橘色光暈、狀態圓點、About 的大型 01/02/03 與右下角區段指示、直排「李建緯」。
- 圓角統一：圖片 12px、大區塊 16px、可點的都是膠囊或圓形。
- 深色／淺色兩種模式：預設跟系統，頁首圓形太陽／月亮按鈕可切換（存 localStorage `aifree-theme`）。淺色用履歷紙色 `#EFEBE3`，小字橘色在淺色版改 `#9a5f00`。
- 頁首：Work／About 是會左右滑動的膠囊（換頁前先滑、下一頁接著滑進來）；Email 是圓形信封 icon。icon 用 PulsoIcon 的靜態 SVG（sun、moon、mail），hover 動畫用 CSS 重做。
- Email 連結按下去會同時複製信箱並跳出提示（沒有郵件 App 時 mailto 不會有反應）。
- 首頁 hero：照片改正方形（到腰部）、右欄變窄；拿掉介紹下的兩顆按鈕（跟頁首重複）；分隔線移到「Selected Work」上方。
- 進度條與照片捲動漂移改用 CSS scroll timeline（不再監聽 scroll 事件）；不支援的瀏覽器不顯示進度條。
- About 頁改版寫在 `about-taste.css`，`build.py` 的 `build_about()` 複製履歷網站後套上（含 HTML 替換、移除背景標記與 scroll 監聽的 JS），`../Resume` 本身沒動。
- 共用互動在 `public/assets/ui.js`（主題按鈕、Email 複製提示、Work/About 滑動）。
- 2026-11-24：作品介紹文字裡的「—」全部清掉（25 個作品檔、48 處，使用者逐處確認過）。中文「——」改成「，」或「：」（ttri 改寫成「B2B「高間距織物（Spacer Fabric）」技術」）；英文成對的插入語改成逗號，單個的改成逗號（jpbc 改冒號）；uspace-video 改成 `point: “Can’t find a parking spot?”, and`，順便把反的開頭引號改正。
- 2026-11-24：Ai Work 裡本專案的 9 個截圖／錄影（aifree-1～4、aifree-m／m2／m3、aifree.mp4、aifree-m.mp4）其實 11/23 改版後就重拍成新版面，只是沒 commit；已在 Ai Portfolio commit 4c98050 上線。taste 改版待辦全部完成。
