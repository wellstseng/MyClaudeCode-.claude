/**
 * @file test-framework/report.ts
 * @description 測試報告產生器 — Markdown 格式
 */
import type { TestTask } from "./task-runner.js";
/**
 * 產生 Markdown 測試報告
 */
export declare function generateReport(task: TestTask): string;
/**
 * 產生簡短摘要（適合 Discord 回覆）
 */
export declare function generateSummary(task: TestTask): string;
