/**
 * @file tools/type.ts
 * @description computer_type — 鍵盤輸入文字或按鍵組合
 */
export interface TypeParams {
    text?: string;
    keys?: string[];
    delayMs?: number;
}
export declare function performType(params: TypeParams): Promise<{
    success: boolean;
    typed?: string;
    pressed?: string[];
    timestamp: string;
}>;
