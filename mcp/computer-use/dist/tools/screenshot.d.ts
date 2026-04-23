/**
 * @file tools/screenshot.ts
 * @description computer_screenshot — 截取螢幕或指定區域/視窗
 */
export interface ScreenshotParams {
    windowTitle?: string;
    region?: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
    scale?: number;
    monitor?: number;
}
export interface ScreenshotResult {
    base64: string;
    mimeType: string;
    width: number;
    height: number;
    originalWidth: number;
    originalHeight: number;
}
export declare function takeScreenshot(params: ScreenshotParams): Promise<ScreenshotResult>;
