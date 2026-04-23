/**
 * @file test-framework/task-runner.ts
 * @description 測試任務執行器 — 管理測試生命週期
 *
 * 注意：實際的步驟執行由 CatClaw agent loop 驅動。
 * 這裡只負責狀態管理和報告收集。
 */
import type { TestTemplate, TestStep } from "./task-template.js";
export type StepStatus = "pending" | "running" | "passed" | "failed" | "skipped";
export interface StepResult {
    step: TestStep;
    status: StepStatus;
    startTime?: string;
    endTime?: string;
    durationMs?: number;
    notes?: string;
    screenshotBase64?: string;
}
export interface TestTask {
    id: string;
    template: TestTemplate;
    status: "pending" | "running" | "completed" | "failed" | "aborted";
    startTime?: string;
    endTime?: string;
    currentStepIndex: number;
    stepResults: StepResult[];
}
/**
 * 建立新測試任務
 */
export declare function createTask(template: TestTemplate): TestTask;
/**
 * 開始執行測試
 */
export declare function startTask(taskId: string): TestTask;
/**
 * 標記當前步驟完成，推進到下一步
 */
export declare function completeStep(taskId: string, passed: boolean, notes?: string, screenshot?: string): TestTask;
/**
 * 中止測試
 */
export declare function abortTask(taskId: string): TestTask;
export declare function getTask(taskId: string): TestTask | undefined;
export declare function listTasks(): TestTask[];
