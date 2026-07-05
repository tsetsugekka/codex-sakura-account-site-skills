#!/usr/bin/env python3
import argparse
import getpass
from pathlib import Path

SECRET_TEMPLATE = """# Sakura deploy secrets
# Fill this file locally. Never commit it.
host: your-server.sakura.ne.jp
user: your-account
password: your-password
"""

MANIFEST_TEMPLATE = """# SFTP upload manifest example.
# Copy this file, replace placeholders, and keep only intended uploads.
# Upload new hashed assets before uploading the live index.html.
# Never add .env, user data, databases, caches, uploads, or LOCAL_DEPLOY_SECRETS.md.

# mkdir /home/your-account/www/assets
# put dist/assets/app.12345678.js /home/your-account/www/assets/app.12345678.js
# put dist/assets/app.12345678.css /home/your-account/www/assets/app.12345678.css
# put dist/index.html /home/your-account/www/index.html

# REQUIRED AFTER VERIFYING A STATIC LIVE PAGE WITH HASHED ASSETS:
# 1. Dry-run old asset cleanup:
#    node scripts/cleanup-remote-assets.mjs <target>
# 2. If the delete list only contains older hash assets:
#    node scripts/cleanup-remote-assets.mjs <target> --apply
# 3. Final verification:
#    node scripts/cleanup-remote-assets.mjs <target>
#    It must report delete=0.
"""

EXPECT_COMMON = r'''#!/usr/bin/expect -f
set timeout 180
set script_dir [file dirname [info script]]

proc find_secret_path {start_dir} {
  set dir [file normalize $start_dir]
  for {set i 0} {$i < 6} {incr i} {
    set candidate [file join $dir "LOCAL_DEPLOY_SECRETS.md"]
    if {[file exists $candidate]} {
      return $candidate
    }
    set parent [file dirname $dir]
    if {$parent eq $dir} {
      break
    }
    set dir $parent
  }
  return ""
}

set secret_path [find_secret_path $script_dir]

if {$secret_path eq "" || ![file exists $secret_path]} {
  puts "Missing LOCAL_DEPLOY_SECRETS.md"
  exit 2
}

set f [open $secret_path r]
set content [read $f]
close $f

set host ""
set user ""
set password ""
foreach line [split $content "\n"] {
  set t [string trim $line]
  if {$t eq "" || [string match "#*" $t]} {
    continue
  }
  if {[regexp -nocase {host\s*[:=：]\s*(.+)$} $t -> value]} {
    set host [string trim $value " `\"'"]
  } elseif {[regexp -nocase {user\s*[:=：]\s*(.+)$} $t -> value]} {
    set user [string trim $value " `\"'"]
  } elseif {[regexp -nocase {(password|pass|密码|密碼).*[:=：]\s*(.+)$} $t -> key value]} {
    set password [string trim $value " `\"'"]
  }
}

if {$host eq "" || $user eq "" || $password eq ""} {
  puts "Could not find host, user, and password in LOCAL_DEPLOY_SECRETS.md"
  exit 2
}
'''

SFTP_SCRIPT = EXPECT_COMMON + r'''
if {[llength $argv] < 1} {
  puts "Usage: expect scripts/sftp-with-local-secret.expect <batch-file>"
  exit 2
}
set batch_path [lindex $argv 0]
spawn sftp -oBatchMode=no -b $batch_path "$user@$host"
expect {
  -re "(?i)password:" {
    send -- "$password\r"
    exp_continue
  }
  eof
}
catch wait result
exit [lindex $result 3]
'''

SSH_SCRIPT = EXPECT_COMMON + r'''
if {[llength $argv] < 1} {
  puts "Usage: expect scripts/ssh-run-with-local-secret.expect <remote command...>"
  exit 2
}
spawn ssh -oBatchMode=no "$user@$host" {*}$argv
expect {
  -re "(?i)password:" {
    send -- "$password\r"
    exp_continue
  }
  eof
}
catch wait result
exit [lindex $result 3]
'''

def write_file(path: Path, content: str, executable: bool = False) -> None:
    if path.exists():
        print(f"skip existing {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)
    print(f"wrote {path}")

def ensure_gitignore(root: Path) -> None:
    path = root / ".gitignore"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if "LOCAL_DEPLOY_SECRETS.md" not in current.splitlines():
        suffix = "" if current.endswith("\n") or current == "" else "\n"
        path.write_text(current + suffix + "LOCAL_DEPLOY_SECRETS.md\n", encoding="utf-8")
        print(f"updated {path}")

def write_local_secret(root: Path, force: bool = False) -> None:
    path = root / "LOCAL_DEPLOY_SECRETS.md"
    if path.exists() and not force:
        print(f"skip existing {path}")
        return
    host = input("Sakura SSH host (example: your-server.sakura.ne.jp): ").strip()
    user = input("Sakura SSH user: ").strip()
    password = getpass.getpass("Sakura SSH password: ")
    if not host or not user or not password:
        raise SystemExit("host, user, and password are required")
    path.write_text(
        "# Sakura deploy secrets\n"
        "# Local only. Never commit this file.\n"
        f"host: {host}\n"
        f"user: {user}\n"
        f"password: {password}\n",
        encoding="utf-8",
    )
    path.chmod(0o600)
    print(f"wrote local secret {path}")

def safe_child_path(root: Path, value: str) -> Path:
    rel = Path(value)
    if rel.is_absolute():
        raise SystemExit(f"path must be relative to project root: {value}")
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise SystemExit(f"path escapes project root: {value}")
    return target

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--helper-dir", default="scripts", help="Helper script directory relative to project root, for example scripts or deploy/scripts.")
    parser.add_argument("--deploy-dir", default="_deploy", help="SFTP manifest directory relative to project root, for example _deploy or deploy/_deploy.")
    parser.add_argument("--write-local-secret", action="store_true", help="Prompt for Sakura SSH credentials and write ignored LOCAL_DEPLOY_SECRETS.md.")
    parser.add_argument("--force-local-secret", action="store_true", help="Overwrite existing LOCAL_DEPLOY_SECRETS.md when used with --write-local-secret.")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    helper_dir = safe_child_path(root, args.helper_dir)
    deploy_dir = safe_child_path(root, args.deploy_dir)
    write_file(root / "LOCAL_DEPLOY_SECRETS.example.md", SECRET_TEMPLATE)
    ensure_gitignore(root)
    write_file(deploy_dir / "SFTP_UPLOAD.example.txt", MANIFEST_TEMPLATE)
    write_file(helper_dir / "sftp-with-local-secret.expect", SFTP_SCRIPT, executable=True)
    write_file(helper_dir / "ssh-run-with-local-secret.expect", SSH_SCRIPT, executable=True)
    if args.write_local_secret:
        write_local_secret(root, force=args.force_local_secret)
    else:
        print("Run again with --write-local-secret to create LOCAL_DEPLOY_SECRETS.md through secure prompts.")

if __name__ == "__main__":
    main()
