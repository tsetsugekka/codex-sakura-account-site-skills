# Deploy Runbook

Use this sequence for Sakura deploys:

1. Build locally.
2. Prepare a whitelist SFTP manifest that lists only intended files.
3. Upload new hashed assets first.
4. Upload API/static files.
5. Upload `index.html` last.
6. Run remote syntax checks.
7. Verify the public URL.
8. Run old asset cleanup in dry-run mode.
9. Apply cleanup only if the delete list contains old generated assets, not production data.
10. Run a final dry-run cleanup check; it must report `delete=0`.

Never deploy by recursively uploading the full repository, a full `dist`, `.env`, databases, user JSON, private settings, cache directories, upload directories, or `node_modules`.

Recommended remote checks:

```bash
/usr/local/bin/php -l /home/USER/www/api/file.php
/bin/sh -n /home/USER/jobs/run_cron.sh
/usr/local/bin/python3 -m py_compile /home/USER/jobs/script.py
```

Use absolute remote paths in deploy manifests. Keep private data and logs outside `www`.

Asset cleanup rules:

- Keep every asset referenced by the current live `index.html`.
- Keep the previous release cluster when the cleanup script can identify it by mtime.
- Delete only older generated hash `.js`, `.css`, and `.map` files.
- Never delete an assets directory, `index.html`, JSON, PHP, databases, user uploads, or cache files.
- If the deploy is a PHP/account-site update that only uploads non-hash shared assets such as `app.css`, skip hashed asset cleanup and say why.
