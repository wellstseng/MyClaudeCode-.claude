/**
 * @file test-framework/task-template.ts
 * @description 測試任務模板定義 + 載入
 */
export interface TestStep {
    name: string;
    description: string;
    successCondition: string;
    /** 單步超時（毫秒），預設 60000 */
    timeoutMs?: number;
}
export interface TestTemplate {
    name: string;
    description: string;
    /** 全局超時（毫秒），預設 300000 */
    timeout: number;
    steps: TestStep[];
}
/**
 * 載入所有模板
 */
export declare function loadTemplates(): Promise<TestTemplate[]>;
/**
 * 按名稱載入模板
 */
export declare function loadTemplate(name: string): Promise<TestTemplate | null>;
