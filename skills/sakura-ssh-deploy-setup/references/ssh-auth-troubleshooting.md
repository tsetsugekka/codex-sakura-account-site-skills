# SSH/SFTP Authentication Troubleshooting

Use this runbook when a Sakura SSH/SFTP connection fails or behaves differently between a normal terminal and Codex, CI, or another restricted execution environment.

## 1. Preserve Evidence and Avoid Repeated Password Attempts

- Use the exact SSH account name with `user@host`.
- Set `NumberOfPasswordPrompts=1` during diagnostics.
- Do not rotate or rewrite the stored password merely because an automated helper failed.
- Do not print the password or run a command that expands it into process arguments, shell history, environment-variable values, or logs.
- If one submitted password is rejected, stop automated retries and ask the user to verify the account or perform one manual login.

## 2. Identify the Failure Stage

Use a low-impact verbose connection without submitting a password when needed:

```bash
ssh -vv -oBatchMode=yes -oPreferredAuthentications=none user@example.sakura.ne.jp
```

Interpret the last successful stage:

| Evidence | Meaning | Next action |
| --- | --- | --- |
| DNS failure, timeout, or connection refused | Transport did not reach SSH authentication | Check host, network, service availability, and port |
| Server host key displayed or verified | TCP and initial SSH negotiation succeeded | Continue to key exchange/authentication evidence |
| Post-quantum KEX warning followed by authentication methods | Connection succeeded without a post-quantum KEX; this is not an authentication failure | Keep working on authentication; ask the provider about a server upgrade separately |
| `Authentications that can continue: publickey,password` | Server reached user authentication and allows the listed methods | Verify explicit username and the intended credential source |
| `Permission denied` after a password was submitted | Credential or account authentication failed | Do not retry automatically; verify account/user/password manually |
| `no matching key exchange method` or `no matching host key type` | Algorithm negotiation failed | Confirm the exact missing algorithm; use only a host-scoped temporary override if necessary |
| SSH command works but SFTP batch fails | Authentication succeeded; failure is in batch path, permission, or transfer behavior | Inspect the SFTP batch and remote permissions |

## 3. Understand the Post-Quantum Warning

Recent OpenSSH clients may warn that a connection does not use a post-quantum key-exchange algorithm. The warning describes resistance to future decryption of captured traffic. It does not mean:

- the password is wrong;
- the SSH server is unreachable;
- `ssh-rsa` must be re-enabled;
- host-key checking should be disabled.

The preferred remediation is provider/server support for a current post-quantum or hybrid KEX. Do not globally suppress the warning. If the user accepts the risk and only wants less noise, any warning suppression must be host-scoped and must not change authentication or host-key verification.

## 4. Use AskPass Only When the Prompt Is Unavailable

Some restricted terminals launch SSH successfully but do not expose the password prompt to Expect. A manual terminal login can still work with the same local secret.

Fallback requirements:

1. First try normal interactive SSH/SFTP.
2. Track whether the helper actually saw and submitted a password.
3. Retry once with AskPass only if the prompt was unavailable, no password was submitted, and authentication failed.
4. Set `SSH_ASKPASS` to a minimal executable helper that reads the ignored mode-`0600` local secret file at invocation time.
5. Set `SSH_ASKPASS_REQUIRE=force` and a dummy `DISPLAY` only for the fallback connection.
6. Keep `StrictHostKeyChecking` at its normal verified setting.
7. If a restricted sandbox cannot update `known_hosts`, `UpdateHostKeys=no` may be set for that scoped command after the existing host key is verified. This prevents automatic host-key-file rewriting; it does not disable host-key verification.

Never embed the password in the AskPass script. Never set the password itself as an environment variable. Delete task-only temporary helpers after use; keep only deliberately generated, public-safe helper code.

## 5. Verify Recovery

Run one harmless SSH command and one non-mutating SFTP batch:

```bash
expect scripts/ssh-run-with-local-secret.expect 'pwd'
expect scripts/sftp-with-local-secret.expect deploy/_deploy/SFTP_LIST_ONLY.txt
```

Confirm that:

- the exit status is zero;
- the remote username/path is the intended target;
- no credential appears in output;
- host-key verification remains enabled;
- the helper used AskPass only if the normal prompt was unavailable.
