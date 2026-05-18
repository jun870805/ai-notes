# Scripts

`infra/scripts/` 放本機開發或部署輔助腳本。

可能用途：

- 等待資料庫啟動。
- 匯入 seed data。
- 執行 migration。
- 清理本機測試資料。

腳本應避免寫死 secret，必要設定請透過環境變數傳入。
