/**
 * @file utils/dpi.ts
 * @description DPI scaling 偵測與座標換算
 *
 * macOS Retina: 邏輯座標 × 2 = 實際 pixel
 * Windows 150%: 邏輯座標 × 1.5 = 實際 pixel
 * nut.js 操作使用邏輯座標，截圖回傳實際 pixel
 */
/**
 * 取得主螢幕 DPI 縮放因子
 * macOS: 從 system_profiler 取得 pixel/point 比
 * Windows: 從 registry 或 WMI 取得
 */
export declare function getDisplayScale(): number;
/**
 * 邏輯座標 → 截圖 pixel 座標（截圖用）
 */
export declare function logicalToPixel(x: number, y: number): {
    x: number;
    y: number;
};
/**
 * 截圖 pixel 座標 → 邏輯座標（nut.js 操控用）
 */
export declare function pixelToLogical(x: number, y: number): {
    x: number;
    y: number;
};
/**
 * 清除快取（螢幕設定變更時）
 */
export declare function resetScaleCache(): void;
