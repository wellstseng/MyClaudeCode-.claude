/**
 * @file index.ts
 * @description CatClaw Playwright MCP Server
 *
 * 封裝 @playwright/mcp，提供 headless 瀏覽器自動化。
 * 預設 headless + chromium，可透過環境變數覆寫。
 *
 * 環境變數：
 *   PLAYWRIGHT_HEADLESS     - "true"(預設) / "false"
 *   PLAYWRIGHT_BROWSER      - "chromium"(預設) / "firefox" / "webkit"
 *   PLAYWRIGHT_VIEWPORT     - "1280x720"(預設)
 *   PLAYWRIGHT_USER_DATA    - 持久化 profile 路徑（預設 isolated）
 *   PLAYWRIGHT_TIMEOUT      - action timeout ms（預設 10000）
 *   PLAYWRIGHT_NAV_TIMEOUT  - navigation timeout ms（預設 60000）
 */
export {};
