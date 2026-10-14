// Validate every .. mermaid:: block in the docs.
// Usage:  node check.mjs [docs/source]     (exit code 1 when a diagram is invalid)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";

const here = path.dirname(fileURLToPath(import.meta.url));
const DOCS = process.argv[2] || path.resolve(here, "../docs/source");

const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>");
global.window = dom.window;
global.document = dom.window.document;
try { Object.defineProperty(global, "navigator", { value: dom.window.navigator, configurable: true }); } catch {}
global.Element = dom.window.Element;
global.SVGElement = dom.window.SVGElement;
global.HTMLElement = dom.window.HTMLElement;
global.DOMParser = dom.window.DOMParser;

const mermaid = (await import("mermaid")).default;
mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });

const files = [];
(function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) { if (!/build|_shared|[.]git/.test(p)) walk(p); }
    else if (e.name.endsWith(".rst")) files.push(p);
  }
})(DOCS);

let total = 0;
const fails = [];
for (const f of files) {
  const lines = fs.readFileSync(f, "utf8").split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    if (!/^\s*[.][.] mermaid::/.test(lines[i])) continue;
    const indent = lines[i].match(/^\s*/)[0].length;
    const body = [];
    let j = i + 1;
    for (; j < lines.length; j++) {
      const l = lines[j];
      if (l.trim() && l.match(/^\s*/)[0].length <= indent) break;
      body.push(l);
    }
    const text = body.join("\n").trim();
    if (!text) continue;
    total++;
    try { await mermaid.parse(text); }
    catch (e) {
      fails.push({ rel: path.relative(DOCS, f), line: i + 1, msg: String(e.message || e).split("\n")[0], text });
    }
    i = j - 1;
  }
}

console.log("mermaid diagrams checked: " + total + " | invalid: " + fails.length);
for (const x of fails) {
  console.log("\n=== " + x.rel + ":" + x.line + " ===");
  console.log("  " + x.msg);
  for (const l of x.text.split("\n")) console.log("  |" + l);
}
process.exit(fails.length ? 1 : 0);
