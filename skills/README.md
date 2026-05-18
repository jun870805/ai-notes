# Codex Skills 安裝與使用說明

這個資料夾放的是可匯入本機 Codex 使用的 skills。每個 skill 都是一個獨立資料夾，資料夾內至少需要有一個 `SKILL.md`。

## 目錄結構

建議每個 skill 使用以下結構：

```text
skills/
  my-skill/
    SKILL.md
    scripts/
    references/
    assets/
```

必要檔案只有 `SKILL.md`，其他資料夾依需求加入：

- `scripts/`：放可執行腳本或輔助工具。
- `references/`：放較長的參考文件、範例、規則。
- `assets/`：放圖片、模板或其他靜態資源。

`SKILL.md` 開頭建議包含 frontmatter：

```markdown
---
name: my-skill
description: Use when ...
---

# My Skill

Describe how Codex should use this skill.
```

## 安裝到本機 Codex

Codex 預設會從以下位置讀取本機 skills：

```bash
~/.codex/skills/
```

在 macOS 上通常是：

```bash
/Users/<your-user-name>/.codex/skills/
```

如果要把此資料夾裡的所有 skills 安裝到本機 Codex，可在此 repo 根目錄執行：

```bash
mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

安裝單一 skill，例如 `mr-description`：

```bash
mkdir -p ~/.codex/skills
cp -R skills/mr-description ~/.codex/skills/
```

如果目標位置已經有同名 skill，請先確認是否要覆蓋。可以先列出目前已安裝的 skills：

```bash
ls ~/.codex/skills
```

## 重新載入

新增或更新 skills 後，需要重啟 Codex，新的 skill 才會被載入。

重啟後可以詢問：

```text
目前有什麼 skill？
```

或直接要求 Codex 使用某個 skill：

```text
請用 mr-description 幫我寫 MR 描述
```

## 使用方式

Codex 會根據 `SKILL.md` 裡的 `name` 與 `description` 判斷什麼時候要使用該 skill。

你也可以在訊息中直接指定 skill 名稱，例如：

```text
使用 tdd-workflow 幫我規劃這個功能的測試流程
```

或：

```text
請用 powerflow-code-review 幫我 review 這次改動
```

## 新增一個 skill

新增 skill 時，建立一個新的子資料夾，並加入 `SKILL.md`：

```bash
mkdir -p skills/my-new-skill
touch skills/my-new-skill/SKILL.md
```

`SKILL.md` 範例：

```markdown
---
name: my-new-skill
description: Use when Codex needs to ...
---

# My New Skill

## When to Use

Use this skill when ...

## Instructions

1. First, ...
2. Then, ...
3. Finally, ...
```

完成後再複製到本機 Codex skills 目錄：

```bash
cp -R skills/my-new-skill ~/.codex/skills/
```

最後重啟 Codex。

## 注意事項

- 每個 skill 都應該有唯一的 `name`。
- 資料夾名稱建議與 `SKILL.md` 裡的 `name` 一致。
- `description` 要清楚描述「什麼情境該使用這個 skill」。
- 不要把多個 skills 混在同一個資料夾裡；一個資料夾代表一個 skill。
- 如果 skill 需要腳本或參考文件，放在同一個 skill 資料夾底下，並在 `SKILL.md` 中說明何時讀取或執行。
