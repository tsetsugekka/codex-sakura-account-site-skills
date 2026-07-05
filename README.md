# Sakura Account Site Skills

> Sakura Server 上に、SSH 配布・GitHub 公開運用・メール送信元・認証付き Web サイトを安全に整えるための Codex Skill Suite。

![Skill Suite](https://img.shields.io/badge/Codex-Skill%20Suite-4f46e5)
![Sakura Server](https://img.shields.io/badge/Sakura%20Server-ready-22c55e)
![Language](https://img.shields.io/badge/Language-日本語-blue)
![Secrets](https://img.shields.io/badge/Secrets-not%20included-critical)

## これは何か

このリポジトリは、新しい Sakura Server 上で「アカウント制 Web サイト」を立ち上げるための公開用 Codex Skills です。

既存の Sakura 運用で使った安全な型を、公開できる形に抽象化しています。実ドメイン、実ユーザー名、サーバーパス、メールアドレス、パスワード、運用ログは含めません。

主なゴールは次の 4 つです。

| Skill | 目的 |
| --- | --- |
| `sakura-ssh-deploy-setup` | Codex が Sakura SSH/SFTP 配布を自動実行できる状態まで整える |
| `github-repo-publish-setup` | Codex が GitHub 新規リポジトリ作成と継続的な公開運用を整える |
| `sakura-mailbox-setup` | Sakura の実メールボックス作成または存在確認、送信元、DNS、送信テストを整える |
| `sakura-auth-site-setup` | ユーザー、ロール、登録確認メール、cron 失敗通知、ページ権限を持つサイトを構築する |

## 特徴

- **機密情報を含まない公開設計**  
  サーバー名、ユーザー名、パスワード、メールパスワード、API キー、実運用パスは含めません。

- **Sakura Server 前提の実務フロー**  
  SSH/SFTP、Sakura コントロールパネル、sendmail、メールボックス、非公開データ配置を前提にしています。

- **Codex automation-first**
  Codex が実行できる作業は Codex が行います。ユーザーの役割は、GitHub の認証コード入力、Sakura のログイン/2FA、Sakura SSH ユーザー名・パスワードの安全入力など、本人しか扱えない入力に限ります。

- **許可リスト型のデプロイ**
  リポジトリ全体や `dist` 全体を再帰アップロードせず、SFTP manifest に書いたファイルだけを配布します。

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
  github-repo-publish-setup/
  sakura-mailbox-setup/
  sakura-auth-site-setup/
```

このリポジトリをそのまま参照して使うことも、必要な skill フォルダだけを自分の Codex skill ディレクトリへコピーして使うこともできます。

## 使用例

```text
Use $sakura-ssh-deploy-setup to prepare password-safe SSH/SFTP deployment for a new Sakura Server site.
```

```text
Use $sakura-mailbox-setup to create a real notification sender mailbox and verify website mail delivery.
```

```text
Use $github-repo-publish-setup to create a GitHub repository and set up safe future Codex commits and pushes.
```

```text
Use $sakura-auth-site-setup to add Japanese login, user groups, registration email verification, and cron failure alerts to this Sakura-hosted website.
```

## セキュリティ方針

- 実パスワードやトークンは Git に入れない。
- `LOCAL_DEPLOY_SECRETS.md` などのローカル秘密ファイルは `.gitignore` に入れる。
- メール送信元は存在する実メールボックスを使う。
- 新規メールボックスが必要な依頼では、ユーザーが browser/computer use を許可しているなら Codex が Sakura コントロールパネルで作成を進める。作成または既存 mailbox の存在確認が終わるまで「完了」と言わない。
- メールボックス作成は Sakura コントロールパネルで行う。SSH は作成後の sendmail/PHP mail 確認、私密設定、コード配置、cron テストに使う。
- サイト名、公開 URL、送信元メール、送信元名、envelope sender はサーバー側の私密設定に置き、管理画面で編集させない。
- 管理画面で編集できるメール項目は、原則として cron 失敗通知の受信先だけにする。
- ユーザー DB、設定ファイル、cron ログは Web 公開ディレクトリの外に置く。
- 登録確認 token は平文保存せず、hash と有効期限だけを保存する。
- 公開ページは、サイドバーの表示位置に関係なく、ロール権限設定に入れない。
- 静的サイトの配布では、新しい hashed assets を先に上げ、最後に live `index.html` を上げる。
- Codex が自動で SSH/SFTP や GitHub push を実行する場合でも、初回のユーザー承認とスコープ確認を前提にする。

## 免責

この Skill Suite は Sakura Internet 公式の製品ではありません。各環境の契約、管理画面、PHP バージョン、メール設定、GitHub 権限に合わせて確認してください。
