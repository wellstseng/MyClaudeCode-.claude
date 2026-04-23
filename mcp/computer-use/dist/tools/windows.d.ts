/**
 * @file tools/windows.ts
 * @description computer_windows — 視窗列表、聚焦、最小化/最大化/關閉
 */
export interface WindowsParams {
    action: "list" | "focus" | "minimize";
    title?: string;
    pid?: number;
}
export declare function performWindows(params: WindowsParams): Promise<Record<string, unknown>>;
