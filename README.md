# Sakura Account Site Skills

> Sakura Server 上に、SSH 配布・メール送信元・認証付き Web サイト・API 秘密情報・cron/crawler 運用・データ増加監視・公開ページ SEO を安全に整えるための Codex Skill Suite。

![Skill Suite](https://img.shields.io/badge/Codex-Skill%20Suite-4f46e5)
![Sakura Server](https://img.shields.io/badge/Sakura%20Server-ready-22c55e)
![Language](https://img.shields.io/badge/Language-日本語-blue)
![Secrets](https://img.shields.io/badge/Secrets-not%20included-critical)

## これは何か

このリポジトリは、新しい Sakura Server 上で「アカウント制 Web サイト」を立ち上げるための公開用 Codex Skills です。

既存の Sakura 運用で使った安全な型を、公開できる形に抽象化しています。実ドメイン、実ユーザー名、サーバーパス、メールアドレス、パスワード、運用ログは含めません。

## リポジトリの運用ルール（AGENTS.md）

[AGENTS.md](AGENTS.md) に、関連 cron の統合、不要な起動の削減、正確な時刻判定と導入後の検証ルールをまとめています。各プロジェクトの運用に合わせて取り込めます。

## 収録 Skill

| Skill | 主な用途 |
| --- | --- |
| `sakura-ssh-deploy-setup` | local-only secret と SFTP allowlist による安全な SSH 配布 |
| `sakura-mailbox-setup` | Sakura mailbox、DNS、sender、PHP/sendmail、配信確認 |
| `sakura-auth-site-setup` | 登録、メール確認、パスワード回復、session、role/page/API 権限 |
| `sakura-api-secrets-deploy` | API credential/model 設定の private store、明示的 source policy、atomic migration、API gate、CSRF、SSRF、防漏洩 deploy |
| `cron-crawler-safety` | crawler の throttle、lock、atomic write、failure-only alert |
| `data-growth-guard` | 無制限に増えるファイルの監査、守衛構築、公開/非公開データ・分割・snapshot 設計 |
| `static-deploy-refresh-check` | stale asset 回避、live data 保護、旧 hash asset cleanup |
| `public-page-seo-assist` | 公開 SPA/静的ページの metadata、noscript、SEO marker |

主なゴールは次の 8 つです。どの skill を使うかは、「今なにを作りたいか」で選びます。

### 1. Sakura への自動デプロイ準備

`sakura-ssh-deploy-setup`

- **困りごと:** Sakura Server へサイトをアップロードしたいが、毎回パスワード入力や手作業の SFTP をしたくない。
- **Codex がすること:** Sakura の接続情報をローカル秘密ファイルに保存し、通常の対話認証を優先して必要時だけ AskPass へ一度フォールバックする SSH/SFTP helper、アップロード許可リスト、`.gitignore`、確認手順を作る。接続失敗時は PQ 警告、鍵交換、ユーザー認証、転送を切り分ける。
- **できあがる状態:** Codex が以後のデプロイで、許可されたファイルだけを Sakura にアップロードできる。秘密情報は Git に入らない。

### 2. Sakura メール送信元の準備

`sakura-mailbox-setup`

- **困りごと:** サイトから登録確認メール、設定確認メール、cron 失敗通知を送りたい。
- **Codex がすること:** Sakura の実メールボックスを作成または確認し、送信元、envelope sender、DNS、PHP `mail()` / sendmail、メールヘッダー、テスト送信を確認する。
- **できあがる状態:** 存在する Sakura メールアドレスを送信元にした通知メール基盤ができる。管理画面には送信元設定を出さず、通知先だけ編集する。

### 3. ログイン・ユーザー権限付きサイトの構築

`sakura-auth-site-setup`

- **困りごと:** Sakura 上のサイトにログイン、メール確認付き登録、確認メール再送、メールからのパスワード再設定、ユーザーグループ、ページ/API 権限、管理画面を追加したい。
- **Codex がすること:** private user store、password hash、CSRF、session 失効、確認/再設定 token の hash・期限・単回使用、ロール別ページ権限、保護 API、管理画面を組み込む。実メールボックスと配信基盤は `sakura-mailbox-setup` と組み合わせる。
- **できあがる状態:** 登録・メール確認・パスワード回復・ユーザーグループ・保護ページ/API・管理画面を持つアカウント制サイトになる。

### 4. API 秘密情報と実行設定の安全な配備

`sakura-api-secrets-deploy`

- **困りごと:** 外部 API credential と model 設定を Sakura の PHP、Python、cron から共通利用したいが、process environment と private file の優先順位が曖昧、`.env` の公開、設定重複、鍵ファイルの分散、書き換え途中の破損、無認証 proxy、CSRF、SSRF、配布 manifest への混入が怖い。
- **Codex がすること:** web root 外の application 単位 private store、canonical configuration key、`managed-file-only` または `injection-first` の明示的 source policy、PHP/Python/shell 共通 resolver、同時 read と atomic replace、非対称 private key の分離、API gate、CSRF、SSRF 防御、段階的 migration と低頻度検証を整える。
- **できあがる状態:** 秘密値を browser や Git に出さず、複数 runtime が同じ完全な設定を安全に読み、旧 key file や shell export を検証後に除去し、SFTP allowlist で安全に配備できる。

### 5. cron・crawler の安全運用

`cron-crawler-safety`

- **困りごと:** cron で動く crawler や scraper が、失敗時に気づけない。二重起動、途中書き込み、古い JSON 上書き、過剰アクセス、SEO 注入ブロック消失が怖い。
- **Codex がすること:** まず既存の cron wrapper、Python/JS crawler、README/SPEC/CHANGELOG を読み、実際の運用から data ownership、cache、batch、SEO marker、restore 手順を確認する。そのうえで per-host random sleep、lock/stamp、timeout、atomic write、last-good 保護、failure-only mail、ログ、デプロイ時の live HTML marker マージを整える。
- **できあがる状態:** crawler は source に連続高頻度アクセスせず、失敗時だけ通知し、成功・lock skip・no-op・予定された defer ではメールしない。公開 JSON/HTML は壊れにくく、cron が作った live data や `<noscript>` SEO をデプロイで消しにくくなる。

### 6. 静的ページ公開後の表示崩れ・古いファイル対策

`static-deploy-refresh-check`

- **困りごと:** 新ページ公開後に古い CSS/JS が残る。Sakura 上に古い assets が増える。cron が作る JSON や HTML 注入を上書きしたくない。
- **Codex がすること:** ページに一度だけ動く更新チェックを入れ、古い hashed assets は「現在 + 直前」だけ残す運用にし、live data と cron 注入済み HTML を保護する。
- **できあがる状態:** ユーザーに手動リロードを頼まず新しい表示へ移行でき、更新用の `__deploy_v` は読み込み後に URL から消え、Sakura 上の不要な古い assets も安全に整理できる。

### 7. 公開ページの SEO 補強

`public-page-seo-assist`

- **困りごと:** JavaScript アプリや静的ツールページが、検索エンジンには空に近く見える。SNS 共有カード、検索説明文、`noscript` の静的説明、cron が更新する SEO ブロックの扱いもページごとにばらつく。
- **Codex がすること:** 公開ページだけを対象に、title、description、canonical、OGP、Twitter Card、WebSite/WebApplication JSON-LD、`h1`、`noscript` fallback、cron 管理 marker を整える。データ更新時刻やニュース時刻は `data-nosnippet` で Google snippet に拾わせない。
- **できあがる状態:** JS が動く前でもページ内容が検索エンジンに伝わり、共有カードも安定する。ユーザーには更新時刻を見せつつ、検索結果には古い「ページ公開日」のように見える時刻を出しにくくする。

### 8. データ無制限増加の監査と保存構造の設計

`data-growth-guard`

- **困りごと:** JSON、履歴、feed、cache、export が大きくなり続けているが、単に大きいだけか、rolling window か、上限なく蓄積しているのか分からない。公開データと private state が混ざり、frontend が履歴 shard を大量に読む構造も整理したい。
- **Codex がすること:** 1 回の size では断定せず、複数回の観測で「最古レコードが固定されたまま byte が増え続ける」ファイルを特定し、実測増加率と保持期間到達時の推定 size を報告する。private state、lock、Markdown report、cron 例を持つ guard を dry-run-first で生成し、公開/非公開境界、日/月 shard、index、consumer 別の有界 snapshot、detail の正確な shard 読み、atomic write、retention、2 段階 migration の guidebook を提供する。
- **できあがる状態:** 大きいが有界な rolling file を誤報せず、無制限 accumulator を継続監視できる。frontend の一覧は小さな snapshot、detail と履歴は authoritative shard を読む、復旧可能で上限の明確な data architecture になる。

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

- **SSH 認証を段階的に診断**
  post-quantum KEX の警告をパスワード失敗や `ssh-rsa` 互換性問題と混同せず、接続段階を確認します。通常の password prompt を最初に使い、制限環境で prompt が取得できず、まだ password を送信していない場合だけ、ローカル秘密ファイルを読む AskPass で一度再試行します。host key verification は無効化しません。

- **cron/crawler を安全運用**
  既存の cron wrapper、Python/JS crawler、README/SPEC/CHANGELOG を先に読み、現在の live data 契約を壊さない形で整えます。同一 host への連続アクセスにはランダム sleep を入れ、cache-first、batch 上限、timeout、retry 上限、lock/stamp、atomic write、last-good 保護を入れます。通知は failure-only にし、成功・lock skip・no-op・予定された defer ではメールしません。

- **file size ではなく growth shape を監視**
  `data-growth-guard` は、最古レコードの移動と実測 byte 増加を run 間で比較します。最古日が前進する rolling window、size が安定する working set、`YYYY-MM.json` / `YYYY-MM-DD.json` の期間 shard は無制限 accumulator と区別します。観測 state と report は web root 外に置き、finding は通知しても本体 job を止めません。

- **archive・index・snapshot の役割を分離**
  長期履歴は access pattern に合う期間 shard を authority とし、stable ID/date index で正確に位置決めします。list/home/widget は用途ごとに bounded snapshot を持ち、detail は必要な account/category/date shard だけを読みます。raw acquisition cache、cursor、failure state、lock、log、backup は公開しません。

- **公開後の古いスタイル対策**
  新しいページやスタイルを公開した後、ユーザーに手動リロードを求めず、ページ側で同一オリジンの JS/CSS 参照変更を検出して一度だけ更新します。更新用の `__deploy_v` は `history.replaceState` で表示 URL から消し、Sakura 上の古い hash assets は「現在 + 直前」の世代だけ残し、cron 生成データやサーバー注入 HTML は保護します。

- **公開ページだけを SEO 対象にする**
  `public-page-seo-assist` は、ログイン不要で index してよいページだけに使います。title、description、canonical、OGP、Twitter Card、JSON-LD、`noscript` を整えますが、管理画面・保護ページ・Pro 専用情報には indexable な静的 fallback を作りません。

- **Google snippet に出したくない時刻を分離**
  データ更新時刻、投稿時刻、ニュース時刻、生成時刻、Reviewed/Updated 系の状態時刻は、ユーザー向け UI では表示しつつ `data-nosnippet` を付けます。`noscript` や静的 SEO 文には実日時を書かず、必要な鮮度表現は `T-1 日中取引` や `最新市場ナラティブ` のような相対 batch 表現にします。

- **ページ権限の引き継ぎを明確化**
  ロールごとのページ権限はアカウントシステムが保持し、保護ページの PHP 入口が `window.SITE_AUTH.pagePermission` のような実行時値を注入します。ページ側はロール名ではなく、そのページ用の permission key を見ます。

- **API credential・model 設定と business API の境界を統一**
  API credential と model/runtime 設定は web root 外の application 単位 private store に置き、PHP・Python・cron で同じ canonical key と明示した source policy を使います。managed-file-only では同名 process environment を無視し、injection-first は明示的に選んだ場合だけ使います。同時 read は許可し、更新は同一 directory の `0600` temporary file から atomic rename します。非対称 private key 本文は別の `0600` PEM に置きます。browser API は server-side login・permission・CSRF、bearer API は token scope、共通 PHP は direct `404`、worker は HTTP `404` に分けます。

- **認証ロジックとメール基盤を分離して連携**
  `sakura-auth-site-setup` は確認/再設定 token、account state、session、CSRF、role permission を担当し、`sakura-mailbox-setup` は Sakura mailbox、DNS、From/envelope sender、sendmail/PHP mail、delivery verification を担当します。どちらか一方だけで登録メール認証完了とは扱いません。

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
  sakura-api-secrets-deploy/
  cron-crawler-safety/
  data-growth-guard/
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
この Sakura ホストのサイトに、日本語ログイン、メール確認付き登録、確認メール再送、メールからのパスワード再設定、ユーザーグループ、ページ/API 権限を追加し、$sakura-mailbox-setup の実メール送信基盤と連携するため、$sakura-auth-site-setup を使ってください。
```

```text
この Sakura サイトの PHP・Python・cron で使う API credential と model 設定を web root 外へ統合し、managed-file-only policy、atomic update、非対称 private key の分離、business API の認証・CSRF・SSRF 防御を整えて安全に配備するため、$sakura-api-secrets-deploy を使ってください。
```

```text
cron で動く crawler を、二重起動防止、timeout、atomic write、last-good 保護、失敗時だけのメール通知付きにするため、$cron-crawler-safety を使ってください。
```

```text
このサーバーの JSON・履歴・cache を監査し、rolling window と無制限 accumulator を区別した report を作り、private state と weekly cron を持つ守衛を整えるため、$data-growth-guard を使ってください。公開/非公開境界、期間 shard、index、consumer 別 snapshot、detail 読み取りもあわせて設計してください。
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
- data growth の観測 state、report、lock、notification hook は Web 公開ディレクトリの外に置く。1 回の size や date span だけで無制限増加と断定せず、十分に古い baseline と最古レコードの移動を比較する。
- 登録確認 token は平文保存せず、hash と有効期限だけを保存する。
- パスワード再設定 token も hash・目的・有効期限・単回使用で扱い、再設定成功後は既存 session を失効する。確認再送と再設定依頼は account enumeration を避ける応答と cooldown を持つ。
- 認証系の token lifecycle、role transition、session、CSRF は `sakura-auth-site-setup` が担当し、mailbox skill は token を生成・保存・検証・記録しない。
- API credential と model/runtime 設定は web root 外の application 単位 private store に置き、directory は正確に `0700`、file は正確に `0600` とする。source policy は managed-file-only または injection-first を明示し、全 runtime で統一する。managed-file-only では同名 environment と path override を読まない。
- 同じ private store は複数 program が同時 read してよい。更新は同じ private directory に完全な `0600` temporary file を作り、重複と必須項目を検証して atomic rename する。live file を in-place truncate/append しない。
- 非対称署名 API の private key 本文は別の `0700` directory / `0600` PEM に置き、共通 store には app/client ID、allowlisted signing algorithm、private-key path だけを保存する。
- migration 後は全 runtime を検証してから旧 provider 別 key file と shell profile/cron export を削除し、temporary incoming file を残さない。
- browser-facing business API はページ入口とは別に server-side login と page permission を検証し、cookie 認証の mutation・quota call・job control は CSRF を必須にする。
- user-controlled URL fetch は public HTTP(S) の必要 port だけを許可し、A/AAAA、private/loopback/link-local/reserved address、DNS pinning、redirect 各 hop、size/timeout を検証する。
- crawler は公開 API、feed、sitemap、またはアクセス許可されたページを優先する。認証が必要な場合は、権限のある公式 API、正規ログイン、ユーザー承認済み session、ブラウザ操作、または手動 export を使う。paywall、CAPTCHA、login、bot 防御、rate limit に遭遇した場合、Codex は独断で回避しない。まず開発を止めてユーザーと十分に相談し、ユーザーにアクセス権、目的、リスク、許容できる方法を論証してもらってから次の進め方を決める。source 側の制限に対しては、cache、slot、batch 上限、per-host throttle、random sleep、retry 上限で運用する。
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
