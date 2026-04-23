/**
 * @file tools/cursor.ts
 * @description computer_cursor — 移動游標、取得位置、拖曳
 */
export interface CursorParams {
    action: "move" | "position" | "drag";
    x?: number;
    y?: number;
    startX?: number;
    startY?: number;
}
export declare function performCursor(params: CursorParams): Promise<Record<string, unknown>>;
