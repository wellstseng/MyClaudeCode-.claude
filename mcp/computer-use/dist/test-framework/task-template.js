/**
 * @file test-framework/task-template.ts
 * @description 測試任務模板定義 + 載入
 */
import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
const TEMPLATES_DIR = new URL("../../templates", import.meta.url).pathname;
/**
 * 載入所有模板
 */
export async function loadTemplates() {
    try {
        const files = await readdir(TEMPLATES_DIR);
        const templates = [];
        for (const f of files) {
            if (!f.endsWith(".json"))
                continue;
            const raw = await readFile(join(TEMPLATES_DIR, f), "utf8");
            templates.push(JSON.parse(raw));
        }
        return templates;
    }
    catch {
        return [];
    }
}
/**
 * 按名稱載入模板
 */
export async function loadTemplate(name) {
    const all = await loadTemplates();
    return all.find(t => t.name === name) ?? null;
}
//# sourceMappingURL=task-template.js.map