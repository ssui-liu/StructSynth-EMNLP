# Overleaf Git 同步指南

本项目的 GitHub 仓库包含多个子目录（`Latex-EMNLP/`、`Latex_Paper_KDD/` 等），但 Overleaf 项目只对应其中一个子目录。两个仓库的 git 历史完全独立，不能直接 push/pull，必须通过"克隆 → 复制 → 提交 → 推送"的方式同步。

## 项目对应关系

| 本地目录 | Overleaf 项目 ID |
|---|---|
| `Latex-EMNLP/` | `6a08ada80705b033f577754c` |

## 前置准备

1. 在 Overleaf Account Settings 中生成 Git Authentication Token（`olp_` 开头）
2. 确保本地安装了 `expect`（macOS 自带）和 `rsync`

## 同步步骤

### 1. 克隆 Overleaf 仓库到临时目录

```bash
expect -c '
spawn git clone https://git@git.overleaf.com/6a08ada80705b033f577754c /tmp/overleaf_sync
expect "Password"
send "<YOUR_TOKEN>\r"
expect eof
'
```

### 2. 同步本地内容（仅对应子目录）

```bash
rsync -av --delete --exclude='.git' Latex-EMNLP/ /tmp/overleaf_sync/
```

**关键参数说明**：
- `--exclude='.git'`：保留 Overleaf 的 git 历史，只替换文件内容
- `--delete`：删除 Overleaf 中已不存在于本地的文件（可选，视需要添加）
- 源路径 `Latex-EMNLP/` 末尾的 `/` 表示复制目录内容而非目录本身

### 3. 检查差异

```bash
cd /tmp/overleaf_sync
git status
git diff --stat
```

确认变更文件列表符合预期，避免推送无关文件。

### 4. 提交并推送

```bash
cd /tmp/overleaf_sync
git add -A
git commit -m "Sync from local: <简要描述变更>"

expect -c '
spawn git push origin master
expect "Password"
send "<YOUR_TOKEN>\r"
expect eof
'
```

### 5. 清理临时目录

```bash
rm -rf /tmp/overleaf_sync
```

## 常见问题

### Q1: 推送的文件范围不对（多推或少推）

**原因**：本地 GitHub 仓库根目录 ≠ Overleaf 项目根目录。如果直接把整个仓库推到 Overleaf，会把 `Latex_Paper_KDD/`、`Plan/` 等无关目录也推上去。

**解决**：始终用 `rsync` 只同步对应子目录（如 `Latex-EMNLP/`），而不是整个仓库。推送前用 `git diff --stat` 确认文件列表。

### Q2: git 历史/源不一致（push 被拒绝）

**原因**：本地 GitHub 和 Overleaf 的 git 历史完全独立（不同的 initial commit），不能互相 push/pull。

**解决**：永远不要给本地仓库添加 Overleaf remote 再直接 push。正确做法是每次克隆 Overleaf 仓库到临时目录，在它的历史上创建新 commit，再 push 回去。

### Q3: Overleaf 上有人改了内容，本地也改了，如何合并？

```bash
# 1. 克隆最新 Overleaf 内容
expect -c '
spawn git clone https://git@git.overleaf.com/<PROJECT_ID> /tmp/overleaf_sync
expect "Password"
send "<YOUR_TOKEN>\r"
expect eof
'

# 2. 对比差异，手动决定保留哪些
diff -rq Latex-EMNLP/ /tmp/overleaf_sync/ --exclude='.git'

# 3. 确认后再 rsync 同步
```

### Q4: Token 认证失败

- Overleaf token 有有效期，过期需在 Account Settings 重新生成
- URL 格式必须是 `https://git@git.overleaf.com/<PROJECT_ID>`
- 用户名是 `git`，密码是 token（`olp_` 开头）

## 一键同步脚本（可选）

将以下内容保存为项目根目录下的 `sync-to-overleaf.sh`：

```bash
#!/bin/bash
set -e

OVERLEAF_PROJECT="6a08ada80705b033f577754c"
LOCAL_DIR="Latex-EMNLP"
TMP_DIR="/tmp/overleaf_sync_$$"
MESSAGE="${1:-Sync from local}"

if [ -z "$OVERLEAF_TOKEN" ]; then
    echo "Error: set OVERLEAF_TOKEN env var first"
    echo "  export OVERLEAF_TOKEN=olp_xxxxx"
    exit 1
fi

echo "==> Cloning Overleaf repo..."
expect -c "
spawn git clone https://git@git.overleaf.com/$OVERLEAF_PROJECT $TMP_DIR
expect \"Password\"
send \"$OVERLEAF_TOKEN\r\"
expect eof
" > /dev/null 2>&1

echo "==> Syncing $LOCAL_DIR/ -> Overleaf..."
rsync -av --exclude='.git' "$LOCAL_DIR/" "$TMP_DIR/" > /dev/null

echo "==> Changes:"
cd "$TMP_DIR"
git diff --stat

echo ""
read -p "Proceed with push? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    rm -rf "$TMP_DIR"
    exit 0
fi

git add -A
git commit -m "$MESSAGE"

echo "==> Pushing to Overleaf..."
expect -c "
spawn git push origin master
expect \"Password\"
send \"$OVERLEAF_TOKEN\r\"
expect eof
" 2>&1 | grep -E "(master|fatal|error)"

rm -rf "$TMP_DIR"
echo "==> Done."
```

使用方式：

```bash
export OVERLEAF_TOKEN=olp_xxxxx
./sync-to-overleaf.sh "Update abstract and introduction"
```
