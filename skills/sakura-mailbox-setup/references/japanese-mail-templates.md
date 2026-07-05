# Japanese Mail Templates

## Cron Failure Recipient Confirmation

Subject:

```text
cron失敗通知先を設定しました
```

Body:

```text
cron 失敗通知先メールアドレスを設定しました。

今後は、対象の処理が失敗した場合のみ、このメールアドレスに通知します。
成功時、対象処理なし、ロックによるスキップ時には送信しません。

この設定に心当たりがない場合は、管理画面で cron 失敗通知先を空にしてください。
```

## Account Verification

Subject:

```text
アカウント確認のお願い
```

Body:

```text
アカウント登録を完了するには、24 時間以内に次のリンクを開いてメールアドレスを確認してください。

{verification_url}

この登録に心当たりがない場合は、このメールを無視してください。
```

## Cron Failure Alert

Subject:

```text
[サイト通知] 定期処理が失敗しました
```

Body:

```text
定期処理が失敗しました。

処理名: {job}
状態: {status}
時刻: {time}

詳細と直近ログを下に記載します。
```
