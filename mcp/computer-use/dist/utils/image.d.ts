/**
 * @file utils/image.ts
 * @description 圖片處理：縮放、base64 轉換
 *
 * Anthropic Vision 最佳實踐：長邊 ≤1568px，短邊 ≤768px
 * 超過時自動等比縮放，減少 token 消耗
 */
export interface ImageResult {
    base64: string;
    mimeType: "image/png" | "image/jpeg";
    width: number;
    height: number;
    originalWidth: number;
    originalHeight: number;
}
/**
 * 將原始截圖 buffer 縮放到適合 Vision API 的尺寸
 * @param buf 原始圖片 buffer（PNG）
 * @param scale 手動縮放比例（0.1-1.0），null = 自動
 */
export declare function processScreenshot(buf: Buffer, scale?: number | null): Promise<ImageResult>;
/**
 * 裁切圖片指定區域
 */
export declare function cropImage(buf: Buffer, region: {
    x: number;
    y: number;
    width: number;
    height: number;
}): Promise<Buffer>;
