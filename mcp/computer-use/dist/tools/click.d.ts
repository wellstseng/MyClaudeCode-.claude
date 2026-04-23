/**
 * @file tools/click.ts
 * @description computer_click — 滑鼠點擊指定座標
 */
export interface ClickParams {
    x: number;
    y: number;
    button?: "left" | "right" | "middle";
    clicks?: number;
    modifiers?: Array<"ctrl" | "alt" | "shift" | "meta" | "cmd">;
    holdMs?: number;
}
export declare function performClick(params: ClickParams): Promise<{
    success: boolean;
    clickedAt: {
        x: number;
        y: number;
    };
    button: string;
    timestamp: string;
}>;
