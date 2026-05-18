---
name: git-push
description: Use when pushing a feature branch to remote. Runs full test suite first, then fetch + rebase onto origin/main, then force-with-lease push. Aborts if tests fail.
---

# Git Push Flow

Push 分支前必須確認測試全過，再 rebase 到最新的 origin/main，最後 force-with-lease push。

## Steps

### 1. 執行完整測試

```bash
cd server
NODE_OPTIONS='--experimental-vm-modules' npx jest --no-coverage 2>&1 | tail -10
```

- 若有任何 failing test → **停止，不繼續 push**，先修好測試
- 所有 tests pass 才繼續下一步

### 2. Fetch 遠端 main

```bash
git fetch origin main
git log --oneline HEAD..origin/main
```

- 確認遠端 main 有無新 commit

### 3. Rebase onto origin/main

```bash
git rebase origin/main
```

- 若有衝突 → 解完衝突後 `git rebase --continue`
- Rebase 完成才繼續

### 4. Force-with-lease Push

```bash
git push --force-with-lease origin <branch-name>
```

- `<branch-name>` 用 `git branch --show-current` 取得

## Rules

- **測試沒過不能 push** — 無例外
- 一定要 rebase，即使遠端 main 沒有新 commit
- 使用 `--force-with-lease` 而非 `--force`，避免覆蓋他人 push
