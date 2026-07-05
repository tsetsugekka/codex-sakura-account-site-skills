#!/usr/bin/env python3
import argparse
from pathlib import Path

SECRET_TEMPLATE = """# Sakura deploy secrets
# Fill this file locally. Never commit it.
host: your-server.sakura.ne.jp
user: your-account
password: your-password
"""

EXPECT_COMMON = r'''#!/usr/bin/expect -f
set timeout 180
set script_dir [file dirname [info script]]
set repo_root [file normalize [file join $script_dir ".."]]
set secret_path [file join $repo_root "LOCAL_DEPLOY_SECRETS.md"]

if {![file exists $secret_path]} {
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
  puts "Usage: expect scripts/ssh-with-local-secret.expect <remote command...>"
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

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    write_file(root / "LOCAL_DEPLOY_SECRETS.example.md", SECRET_TEMPLATE)
    ensure_gitignore(root)
    write_file(root / "scripts/sftp-with-local-secret.expect", SFTP_SCRIPT, executable=True)
    write_file(root / "scripts/ssh-with-local-secret.expect", SSH_SCRIPT, executable=True)
    print("Create LOCAL_DEPLOY_SECRETS.md locally from the example and fill real values outside Git.")

if __name__ == "__main__":
    main()

