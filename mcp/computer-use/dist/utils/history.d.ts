/**
 * @file utils/history.ts
 * @description 操作歷程記錄 — 每步操作的截圖 + 參數 + 時間戳
 */
export interface HistoryEntry {
    id: number;
    timestamp: string;
    tool: string;
    params: Record<string, unknown>;
    /** 操作前截圖（base64，縮圖） */
    screenshotBefore?: string;
    /** 操作後截圖（base64，縮圖） */
    screenshotAfter?: string;
    result?: Record<string, unknown>;
    durationMs?: number;
}
/**
 * 記錄一筆操作
 */
export declare function recordOperation(tool: string, params: Record<string, unknown>, result?: Record<string, unknown>, screenshotBefore?: string, durationMs?: number): Promise<HistoryEntry>;
/**
 * 取得最近 N 筆操作摘要
 */
export declare function getRecentHistory(count?: number): HistoryEntry[];
/**
 * 匯出 Markdown 報告
 */
export declare function exportMarkdownReport(): string;
/**
 * 清除歷程
 */
export declare function clearHistory(): Promise<void>;
