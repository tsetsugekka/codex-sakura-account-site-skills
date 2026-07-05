# Deploy Runbook

Use this sequence for Sakura deploys:

1. Build locally.
2. Prepare a deploy directory or manifest.
3. Upload new hashed assets first.
4. Upload API/static files.
5. Upload `index.html` last.
6. Run remote syntax checks.
7. Verify the public URL.
8. Run old asset cleanup in dry-run mode.
9. Apply cleanup only if the delete list contains old generated assets, not production data.

Recommended remote checks:

```bash
/usr/local/bin/php -l /home/USER/www/api/file.php
/bin/sh -n /home/USER/jobs/run_cron.sh
/usr/local/bin/python3 -m py_compile /home/USER/jobs/script.py
```

Use absolute remote paths in deploy manifests. Keep private data and logs outside `www`.

