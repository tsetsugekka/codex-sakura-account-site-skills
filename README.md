# Sakura Account Site Skills

> Sakura Server 上に、SSH 配布・メール送信元・認証付き Web サイト・cron/crawler 運用・公開ページ SEO を安全に整えるための Codex Skill Suite。

![Skill Suite](https://img.shields.io/badge/Codex-Skill%20Suite-4f46e5)
![Sakura Server](https://img.shields.io/badge/Sakura%20Server-ready-22c55e)
![Language](https://img.shields.io/badge/Language-日本語-blue)
![Secrets](https://img.shields.io/badge/Secrets-not%20included-critical)

## これは何か

このリポジトリは、新しい Sakura Server 上で「アカウント制 Web サイト」を立ち上げるための公開用 Codex Skills です。

既存の Sakura 運用で使った安全な型を、公開できる形に抽象化しています。実ドメイン、実ユーザー名、サーバーパス、メールアドレス、パスワード、運用ログは含めません。

主なゴールは次の 6 つです。どの skill を使うかは、「今なにを作りたいか」で選びます。

### 1. Sakura への自動デプロイ準備

`sakura-ssh-deploy-setup`

- **困りごと:** Sakura Server へサイトをアップロードしたいが、毎回パスワード入力や手作業の SFTP をしたくない。
- **Codex がすること:** Sakura の接続情報をローカル秘密ファイルに保存し、SSH/SFTP helper、アップロード許可リスト、`.gitignore`、確認手順を作る。
- **できあがる状態:** Codex が以後のデプロイで、許可されたファイルだけを Sakura にアップロードできる。秘密情報は Git に入らない。

### 2. Sakura メール送信元の準備

`sakura-mailbox-setup`

- **困りごと:** サイトから登録確認メール、設定確認メール、cron 失敗通知を送りたい。
- **Codex がすること:** Sakura の実メールボックスを作成または確認し、送信元、envelope sender、DNS、PHP `mail()` / sendmail、メールヘッダー、テスト送信を確認する。
- **できあがる状態:** 存在する Sakura メールアドレスを送信元にした通知メール基盤ができる。管理画面には送信元設定を出さず、通知先だけ編集する。

### 3. ログイン・ユーザー権限付きサイトの構築

`sakura-auth-site-setup`

- **困りごと:** Sakura 上のサイトにログイン、ユーザーグループ、ページ権限、登録確認メール、管理画面を追加したい。
- **Codex がすること:** ユーザー保存場所、password hash、メール確認 token、ロール別ページ権限、管理画面、cron 失敗通知設定をサイトに組み込む。
- **できあがる状態:** 登録確認後のユーザー、staff/admin などの権限、保護ページ、管理画面を持つアカウント制サイトになる。

### 4. cron・crawler の安全運用

`cron-crawler-safety`

- **困りごと:** cron で動く crawler や scraper が、失敗時に気づけない。二重起動、途中書き込み、古い JSON 上書き、過剰アクセス、SEO 注入ブロック消失が怖い。
- **Codex がすること:** まず既存の cron wrapper、Python/JS crawler、README/SPEC/CHANGELOG を読み、実際の運用から data ownership、cache、batch、SEO marker、restore 手順を確認する。そのうえで per-host random sleep、lock/stamp、timeout、atomic write、last-good 保護、failure-only mail、ログ、デプロイ時の live HTML marker マージを整える。
- **できあがる状態:** crawler は source に連続高頻度アクセスせず、失敗時だけ通知し、成功・lock skip・no-op・予定された defer ではメールしない。公開 JSON/HTML は壊れにくく、cron が作った live data や `<noscript>` SEO をデプロイで消しにくくなる。

### 5. 静的ページ公開後の表示崩れ・古いファイル対策

`static-deploy-refresh-check`

- **困りごと:** 新ページ公開後に古い CSS/JS が残る。Sakura 上に古い assets が増える。cron が作る JSON や HTML 注入を上書きしたくない。
- **Codex がすること:** ページに一度だけ動く更新チェックを入れ、古い hashed assets は「現在 + 直前」だけ残す運用にし、live data と cron 注入済み HTML を保護する。
- **できあがる状態:** ユーザーに手動リロードを頼まず新しい表示へ移行でき、更新用の `__deploy_v` は読み込み後に URL から消え、Sakura 上の不要な古い assets も安全に整理できる。

### 6. 公開ページの SEO 補強

`public-page-seo-assist`

- **困りごと:** JavaScript アプリや静的ツールページが、検索エンジンには空に近く見える。SNS 共有カード、検索説明文、`noscript` の静的説明、cron が更新する SEO ブロックの扱いもページごとにばらつく。
- **Codex がすること:** 公開ページだけを対象に、title、description、canonical、OGP、Twitter Card、WebSite/WebApplication JSON-LD、`h1`、`noscript` fallback、cron 管理 marker を整える。データ更新時刻やニュース時刻は `data-nosnippet` で Google snippet に拾わせない。
- **できあがる状態:** JS が動く前でもページ内容が検索エンジンに伝わり、共有カードも安定する。ユーザーには更新時刻を見せつつ、検索結果には古い「ページ公開日」のように見える時刻を出しにくくする。

## 推奨 companion skill

GitHub 新規リポジトリ作成、初回 commit/push、以後の intended branch 公開運用も Codex に任せたい場合は、別配布の companion skill `github-repo-publish-setup` を併用します。配布リポジトリ名は `codex-github-publish-workflow-skill` です。

この Sakura suite は GitHub 公開運用を内蔵しません。Sakura セットアップと GitHub 公開は独立した関心事なので、GitHub 側は汎用 skill として管理します。

```text
この Sakura プロジェクトを公開する前に、$github-repo-publish-setup で GitHub リポジトリを新規作成または接続してください。
```

## 特徴

- **機密情報を含まない公開設計**  
  サーバー名、ユーザー名、パスワード、メールパスワード、API キー、実運用パスは含めません。

- **Sakura Server 前提の実務フロー**  
  SSH/SFTP、Sakura コントロールパネル、sendmail、メールボックス、非公開データ配置を前提にしています。

- **Codex automation-first**
  Codex が実行できる作業は Codex が行います。Sakura の既存ログイン状態・承認済み資格情報が使える場合はそのまま進め、ユーザーの役割は、認証コード、ログイン/2FA、SSH ユーザー名・パスワードなど本人しか扱えない入力が必要な場面に限ります。

- **ブラウザ操作は隔離して実行**
  Sakura コントロールパネルの操作は、利用可能なら Codex in-app browser を優先します。ユーザーが明示しない限り、現在操作中の Chrome タブやウィンドウを奪いません。

- **確認は最小限**
  ユーザーが明確に委任した作業で、後から容易に戻せる通常操作は追加確認なしで進めます。削除、課金、公開範囲の拡大、秘密情報の変更、復旧困難な変更だけ短く確認します。

- **許可リスト型のデプロイ**
  リポジトリ全体や `dist` 全体を再帰アップロードせず、SFTP manifest に書いたファイルだけを配布します。

- **cron/crawler を安全運用**
  既存の cron wrapper、Python/JS crawler、README/SPEC/CHANGELOG を先に読み、現在の live data 契約を壊さない形で整えます。同一 host への連続アクセスにはランダム sleep を入れ、cache-first、batch 上限、timeout、retry 上限、lock/stamp、atomic write、last-good 保護を入れます。通知は failure-only にし、成功・lock skip・no-op・予定された defer ではメールしません。

- **公開後の古いスタイル対策**
  新しいページやスタイルを公開した後、ユーザーに手動リロードを求めず、ページ側で同一オリジンの JS/CSS 参照変更を検出して一度だけ更新します。更新用の `__deploy_v` は `history.replaceState` で表示 URL から消し、Sakura 上の古い hash assets は「現在 + 直前」の世代だけ残し、cron 生成データやサーバー注入 HTML は保護します。

- **公開ページだけを SEO 対象にする**
  `public-page-seo-assist` は、ログイン不要で index してよいページだけに使います。title、description、canonical、OGP、Twitter Card、JSON-LD、`noscript` を整えますが、管理画面・保護ページ・Pro 専用情報には indexable な静的 fallback を作りません。

- **Google snippet に出したくない時刻を分離**
  データ更新時刻、投稿時刻、ニュース時刻、生成時刻、Reviewed/Updated 系の状態時刻は、ユーザー向け UI では表示しつつ `data-nosnippet` を付けます。`noscript` や静的 SEO 文には実日時を書かず、必要な鮮度表現は `T-1 日中取引` や `最新市場ナラティブ` のような相対 batch 表現にします。

- **ページ権限の引き継ぎを明確化**
  ロールごとのページ権限はアカウントシステムが保持し、保護ページの PHP 入口が `window.SITE_AUTH.pagePermission` のような実行時値を注入します。ページ側はロール名ではなく、そのページ用の permission key を見ます。

- **日本語サイト向け**  
  認証画面、管理画面、通知メールは日本語を標準にします。必要に応じて多言語化できます。

- **既存サイトの雰囲気を尊重**  
  管理画面は既存サイトの色、余白、角丸、ナビゲーション、ヘッダー、タイポグラフィに寄せる方針です。

## 推奨リポジトリ構成

```text
skills/
  sakura-ssh-deploy-setup/
  sakura-mailbox-setup/
  sakura-auth-site-setup/
  cron-crawler-safety/
  static-deploy-refresh-check/
  public-page-seo-assist/
```

このリポジトリをそのまま参照して使うことも、必要な skill フォルダだけを自分の Codex skill ディレクトリへコピーして使うこともできます。

## 使用例

```text
新しい Sakura Server サイトに、パスワードを Git に残さない SSH/SFTP デプロイ手順を整えるため、$sakura-ssh-deploy-setup を使ってください。
```

```text
実在する通知送信元メールボックスを作成し、サイトからのメール送信を確認するため、$sakura-mailbox-setup を使ってください。
```

```text
この Sakura ホストのサイトに、日本語ログイン、ユーザーグループ、登録確認メール、cron 失敗通知を追加するため、$sakura-auth-site-setup を使ってください。
```

```text
cron で動く crawler を、二重起動防止、timeout、atomic write、last-good 保護、失敗時だけのメール通知付きにするため、$cron-crawler-safety を使ってください。
```

```text
既存の静的ページへ一度だけ動くデプロイ更新チェックを追加し、新規ページにも同じ挙動を入れるため、$static-deploy-refresh-check を使ってください。
```

```text
公開 JavaScript ツールページに、安定した日本語 SEO タグ、canonical と og:url、sitemap、必要な場合だけの共有カード、noscript fallback、cron 管理 SEO marker、Google snippet に安全な時刻表示を整えるため、$public-page-seo-assist を使ってください。
```

## セキュリティ方針

- 実パスワードやトークンは Git に入れない。
- `LOCAL_DEPLOY_SECRETS.md` などのローカル秘密ファイルは `.gitignore` に入れる。
- メール送信元は存在する実メールボックスを使う。
- 新規メールボックスが必要な依頼では、ユーザーが browser/computer use を許可しているなら Codex が Sakura コントロールパネルで作成を進める。既存のログイン状態が使える場合、ユーザーに再ログインを求めない。作成または既存 mailbox の存在確認が終わるまで「完了」と言わない。
- メールボックス作成は Sakura コントロールパネルで行う。SSH は作成後の sendmail/PHP mail 確認、私密設定、コード配置、cron テストに使う。
- 既存のローカル秘密ファイルや承認済み資格情報がある場合、Codex は値を出力せずに読み取り、SSH で既存 mailbox とメール関連コマンドを確認してからコントロールパネル作成へ進む。
- Sakura のサーバーアカウント/ドメイン資格情報は SSH/SFTP とコントロールパネルの両方で使います。Codex は資格情報の由来を確認し、Sakura 用として収集・承認された値だけを出力せずに再利用する。
- サイト名、公開 URL、送信元メール、送信元名、envelope sender はサーバー側の私密設定に置き、管理画面で編集させない。
- 管理画面で編集できるメール項目は、原則として cron 失敗通知の受信先だけにする。
- ユーザー DB、設定ファイル、cron ログは Web 公開ディレクトリの外に置く。
- 登録確認 token は平文保存せず、hash と有効期限だけを保存する。
- crawler は公開 API、feed、sitemap、またはアクセス許可されたページを優先する。認証が必要な場合は、権限のある公式 API、正規ログイン、ユーザー承認済み session、または手動 export を使う。paywall、CAPTCHA、login、bot 防御、rate limit を回避する実装はしない。
- 同じ host に対して高頻度・無間隔で連続 request しない。URL が違っても host が同じなら per-host throttle を通し、ランダム sleep/jitter を入れる。
- cron crawler は既存の README/SPEC/CHANGELOG と実スクリプトを確認してから変更する。lock、stamp、timeout、request timeout、retry 上限、batch 上限、atomic write、出力 validation を持つ。失敗時だけメールし、成功・no-op・lock skip・予定された defer では通知しない。
- cron が生成する公開 JSON、分日アーカイブ、ランキング、feed inventory、chart data、`noscript` SEO marker は、通常の静的 deploy で上書きしない。必要な場合は live 版を取得してから最小差分でマージする。
- crawler のログや通知には、cookie、authorization header、API key、個人情報、巨大な raw response を入れない。
- 公開ページは、サイドバーの表示位置に関係なく、ロール権限設定に入れない。
- 静的サイトの配布では、新しい hashed assets を先に上げ、最後に live `index.html` を上げる。
- 静的ページの cache-busting は、同一ページの JS/CSS 参照変更だけを見て一度だけ更新し、読み込み後に `__deploy_v` を `history.replaceState` で URL から消す。生産 JSON、cron 出力、scraper 管理の SEO ブロックは触らない。
- Sakura 上の古い assets を削除する場合は、ページ単位で dry-run し、現在の live HTML が参照する assets と直前世代を残す。cron が更新する HTML 領域は、公開前にオンラインの最新 HTML からマージしてから上書きする。
- 公開ページ SEO では、`noscript`、静的概要、SEO fallback、JSON-LD、HTML コメントに実日時を書かない。日時がユーザーに必要な場合は可視 UI に残し、該当要素へ `data-nosnippet` を付ける。
- 記事ページではないツール、ダッシュボード、ランキング、feed には、`<time datetime>`、`datePublished`、`dateModified`、Article/NewsArticle 系 JSON-LD を付けない。
- Codex が自動で SSH/SFTP を実行する場合でも、初回のユーザー承認とスコープ確認を前提にする。GitHub repo 作成や commit/push は companion skill `github-repo-publish-setup` の publish discipline に従う。

## 免責

この Skill Suite は Sakura Internet 公式の製品ではありません。各環境の契約、管理画面、PHP バージョン、メール設定、GitHub 権限に合わせて確認してください。
