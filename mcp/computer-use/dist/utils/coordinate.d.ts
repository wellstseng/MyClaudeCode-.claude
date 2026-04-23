/**
 * @file utils/coordinate.ts
 * @description 截圖座標 ↔ 螢幕座標 換算
 *
 * AI 看到的是縮放後的截圖（例如 1024px），回傳的座標基於截圖空間。
 * 實際操控螢幕需要原始座標。此模組記住最後一次截圖的縮放比例，
 * 自動將 AI 座標轉換為螢幕座標。
 */
/**
 * 截圖後更新縮放比例
 */
export declare function updateScreenshotScale(screenshotWidth: number, originalWidth: number): void;
/**
 * 將 AI 座標（截圖空間）轉為螢幕座標
 */
export declare function screenshotToScreen(x: number, y: number): {
    x: number;
    y: number;
};
/**
 * 取得目前的縮放比例（debug 用）
 */
export declare function getScreenshotScale(): number;
