/**
 * @file tools/scroll.ts
 * @description computer_scroll — 滾輪操作
 */
export interface ScrollParams {
    x: number;
    y: number;
    direction: "up" | "down" | "left" | "right";
    amount?: number;
}
export declare function performScroll(params: ScrollParams): Promise<{
    success: boolean;
    timestamp: string;
}>;
