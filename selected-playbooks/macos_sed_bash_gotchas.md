---
type: playbook
title: macOS sed and bash scripting gotchas
agents: [seymour]
tags: [macos, sed, bash, scripting, bsd, gotcha]
created: 2026-04-21
updated: 2026-04-21
---

## Goal

Capture common sed and bash piping issues that silently fail on macOS and are easy to miss when porting from Linux.

## When to Use

- Writing bash scripts on macOS that must be portable or reliable
- Using sed for text substitution
- Complex bash pipelines with error propagation requirements

## Gotcha 1: BSD sed does not support `\b` word boundary

**Problem:** `sed 's/\bWord\b/replacement/g'` on macOS BSD sed silently matches nothing. The substitution never happens.

**Why:** macOS ships with BSD sed, not GNU sed. BSD sed does not recognize `\b` as a word boundary anchor.

**Solution:** Use plain regex without word boundaries:
```bash
# Instead of this:
sed 's/\bWord\b/replacement/g' file

# Do this:
sed 's/Word/replacement/g' file
```

Or use `sed 's/ Word / replacement /g'` if context-dependent matching is needed.

**When this bites you:** Porting bash scripts from Linux CI/CD to macOS, or when copying sed patterns from GNU sed documentation without checking BSD compatibility.

---

## Gotcha 2: `find | while read` with `set -euo pipefail` may not propagate errors correctly

**Problem:** In a bash script with `set -euo pipefail`, using `find | while read` may hide errors from the loop body. Errors inside the while loop don't propagate back to the main script exit status.

**Why:** The pipe creates a subshell. In bash, the subshell's exit status is the status of the rightmost command (the while loop), not the entire pipeline. If the loop encounters an error but completes, the script continues.

**Solution:** Use process substitution with null delimiters instead:
```bash
# Instead of this:
find . -name "*.txt" | while read -r file; do
  rm "$file"
done

# Do this:
while read -r file; do
  rm "$file"
done < <(find . -name "*.txt" -print0)
```

Or if you need the find exit status to matter:
```bash
set -euo pipefail
errors=0
find . -name "*.txt" | while read -r file; do
  rm "$file" || ((errors++))
done
# Check $errors afterward, or use a temp file to communicate status back
```

**When this bites you:** When file operations in the loop are critical and must fail fast, or when running under CI/CD with strict error handling.

---

## Related gotchas

- **rsync with `-a` from git repos:** See [[public_private_repo_sync]] for the `.git/` exclude issue
- **Homebrew Python and venv:** See [[macos_homebrew_python_venv_requirement]]
- **FAT32 file permissions:** See [[macos_fat32_file_permissions]]
