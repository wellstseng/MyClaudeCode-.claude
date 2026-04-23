/**
 * @file utils/safety.ts
 * @description 安全機制：座標邊界檢查、視窗白名單、操作速率限制
 */
export declare function validateCoordinates(x: number, y: number): Promise<void>;
export declare function isWindowAllowed(windowTitle: string): boolean;
export declare function checkRateLimit(): void;
