/**
 * @file utils/anomaly.ts
 * @description 卡住偵測 — 連續截圖 diff 比對，畫面無變化時警告
 */
/**
 * 比較當前截圖與前一張，回傳差異比例和卡住狀態
 * 使用簡化的像素比較（不依賴 pixelmatch，用 sharp 降解析度後逐 pixel 比）
 */
export declare function checkForStuck(currentScreenshot: Buffer): Promise<{
    diffRatio: number;
    isStuck: boolean;
    unchangedCount: number;
}>;
/**
 * 重置卡住偵測狀態
 */
export declare function resetStuckDetection(): void;
