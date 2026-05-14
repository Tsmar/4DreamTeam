#!/usr/bin/env bun

import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";

type SourceRoot = {
  id: string;
  path: string;
  type: string;
  purpose?: string;
  writePolicy?: string;
  changelogPolicy?: string;
};

type FileRef = {
  path: string;
  description: string;
};

type SourceGroup = {
  id: string;
  area: string;
  root: string;
  type?: string;
  title: string;
  purpose: string;
  usedBy: string[];
  keywords: string[];
  primaryQuestions: string[];
  primaryFiles: FileRef[];
  supportingFiles: FileRef[];
  relatedWikiPages: string[];
  updateTriggers: string[];
  notes: string[];
};

type SourceMapIndex = {
  project: string;
  indexVersion: number;
  generatedAt: string;
  sourceMapPath: string;
  sourceMapSha256: string;
  roots: SourceRoot[];
  groups: SourceGroup[];
};

type Manifest = {
  project: string;
  indexVersion: number;
  generatedAt: string;
  sourceMapPath: string;
  sourceMapSha256: string;
  groupCount: number;
};

const INDEX_VERSION = 1;

function usage(exitCode = 1): never {
  console.error(`Usage:
  bun skill/tools/wiki.ts index build <docs-project-path>
  bun skill/tools/wiki.ts index check <docs-project-path>
  bun skill/tools/wiki.ts search <docs-project-path> <query>
`);
  process.exit(exitCode);
}

function sha256(content: string): string {
  return createHash("sha256").update(content).digest("hex");
}

function kebab(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function parseMeta(raw: string): Record<string, string> {
  const meta: Record<string, string> = {};
  for (const line of raw.split(/\r?\n/)) {
    const match = line.match(/^\s*([a-zA-Z0-9_-]+)\s*:\s*(.*?)\s*$/);
    if (!match) continue;
    meta[match[1].replace(/_([a-z])/g, (_, char: string) => char.toUpperCase())] = match[2];
  }
  return meta;
}

function splitCsv(value?: string): string[] {
  if (!value) return [];
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

function section(body: string, label: string): string {
  const lines = body.split(/\r?\n/);
  const start = lines.findIndex((line) => line.trim() === `${label}:`);
  if (start === -1) return "";
  const out: string[] = [];
  for (let i = start + 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (/^#{2,6}\s+/.test(line)) break;
    if (/^[A-Z][A-Za-z ]+:\s*$/.test(line.trim())) break;
    if (/^<!--\s*source-/.test(line.trim())) break;
    out.push(line);
  }
  return out.join("\n").trim();
}

function parseBullets(raw: string): string[] {
  return raw
    .split(/\r?\n/)
    .map((line) => line.match(/^\s*-\s+(.*?)\s*$/)?.[1] ?? "")
    .filter(Boolean);
}

function parseFileRefs(raw: string): FileRef[] {
  return parseBullets(raw).map((line) => {
    const match = line.match(/^`([^`]+)`\s*(?:[-–—]\s*(.*))?$/);
    if (!match) return { path: line, description: "" };
    return { path: match[1], description: match[2]?.trim() ?? "" };
  });
}

function firstParagraph(raw: string): string {
  return raw
    .split(/\n\s*\n/)
    .map((part) => part.trim())
    .find(Boolean) ?? "";
}

function parseSourceMap(projectPath: string): SourceMapIndex {
  const sourceMapFile = path.join(projectPath, "source-map.md");
  if (!existsSync(sourceMapFile)) {
    throw new Error(`Missing source map: ${sourceMapFile}`);
  }

  const markdown = readFileSync(sourceMapFile, "utf8");
  const blocks = [...markdown.matchAll(/<!--\s*(source-root|source-group)\s*([\s\S]*?)-->/g)];
  const roots: SourceRoot[] = [];
  const groups: SourceGroup[] = [];

  for (let i = 0; i < blocks.length; i += 1) {
    const match = blocks[i];
    const kind = match[1];
    const meta = parseMeta(match[2]);
    const bodyStart = (match.index ?? 0) + match[0].length;
    const bodyEnd = i + 1 < blocks.length ? blocks[i + 1].index ?? markdown.length : markdown.length;
    const body = markdown.slice(bodyStart, bodyEnd);

    if (kind === "source-root") {
      roots.push({
        id: meta.id || kebab(meta.path || "source-root"),
        path: meta.path || "",
        type: meta.type || "unknown",
        purpose: meta.purpose,
        writePolicy: meta.writePolicy,
        changelogPolicy: meta.changelogPolicy,
      });
      continue;
    }

    const title = body.match(/^#{2,4}\s+(.+?)\s*$/m)?.[1]?.trim() ?? meta.id ?? "Untitled group";
    groups.push({
      id: meta.id || kebab(title),
      area: meta.area || "unknown",
      root: meta.root || "",
      type: meta.type,
      title,
      purpose: firstParagraph(section(body, "Purpose")) || meta.purpose || "",
      usedBy: splitCsv(meta.usedBy),
      keywords: splitCsv(meta.keywords),
      primaryQuestions: parseBullets(section(body, "Primary Questions")),
      primaryFiles: parseFileRefs(section(body, "Primary Files")),
      supportingFiles: parseFileRefs(section(body, "Supporting Files")),
      relatedWikiPages: parseFileRefs(section(body, "Related Wiki Pages")).map((ref) => ref.path),
      updateTriggers: parseBullets(section(body, "Update Triggers")),
      notes: parseBullets(section(body, "Notes")),
    });
  }

  const project = path.basename(projectPath);
  return {
    project,
    indexVersion: INDEX_VERSION,
    generatedAt: new Date().toISOString(),
    sourceMapPath: path.relative(process.cwd(), sourceMapFile),
    sourceMapSha256: sha256(markdown),
    roots,
    groups,
  };
}

function indexDir(projectPath: string): string {
  return path.join(projectPath, ".index");
}

function writeJson(file: string, value: unknown): void {
  writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function build(projectPath: string): void {
  const index = parseSourceMap(projectPath);
  const dir = indexDir(projectPath);
  mkdirSync(dir, { recursive: true });

  const manifest: Manifest = {
    project: index.project,
    indexVersion: index.indexVersion,
    generatedAt: index.generatedAt,
    sourceMapPath: index.sourceMapPath,
    sourceMapSha256: index.sourceMapSha256,
    groupCount: index.groups.length,
  };

  writeJson(path.join(dir, "source-map.json"), index);
  writeJson(path.join(dir, "manifest.json"), manifest);
  console.log(`Built index for ${index.project}: ${index.groups.length} groups`);
}

function readIndex(projectPath: string): SourceMapIndex {
  const file = path.join(indexDir(projectPath), "source-map.json");
  if (!existsSync(file)) throw new Error(`Missing index: ${file}`);
  return JSON.parse(readFileSync(file, "utf8")) as SourceMapIndex;
}

function check(projectPath: string): number {
  const errors: string[] = [];
  const warnings: string[] = [];
  const sourceMapFile = path.join(projectPath, "source-map.md");
  const indexFile = path.join(indexDir(projectPath), "source-map.json");
  const manifestFile = path.join(indexDir(projectPath), "manifest.json");

  if (!existsSync(sourceMapFile)) errors.push(`Missing source-map.md: ${sourceMapFile}`);
  if (!existsSync(indexFile)) errors.push(`Missing generated index: ${indexFile}`);
  if (!existsSync(manifestFile)) warnings.push(`Missing manifest: ${manifestFile}`);
  if (errors.length > 0) return printCheck(errors, warnings);

  const index = readIndex(projectPath);
  const sourceHash = sha256(readFileSync(sourceMapFile, "utf8"));
  if (index.sourceMapSha256 !== sourceHash) {
    errors.push("Stale index: source-map.md hash does not match .index/source-map.json");
  }

  const ids = new Set<string>();
  for (const group of index.groups) {
    if (ids.has(group.id)) errors.push(`Duplicate source group id: ${group.id}`);
    ids.add(group.id);
    if (!group.root) errors.push(`Group ${group.id} is missing root`);
    if (!group.area) errors.push(`Group ${group.id} is missing area`);
    if (!group.purpose) warnings.push(`Group ${group.id} is missing purpose`);
    if (group.primaryFiles.length === 0 && group.supportingFiles.length === 0) {
      warnings.push(`Group ${group.id} has no file references`);
    }

    for (const ref of [...group.primaryFiles, ...group.supportingFiles]) {
      const resolved = path.resolve(process.cwd(), ref.path);
      if (!existsSync(resolved)) errors.push(`Missing source file for ${group.id}: ${ref.path}`);
    }

    for (const page of group.relatedWikiPages) {
      const resolved = path.resolve(projectPath, page);
      if (!existsSync(resolved)) errors.push(`Missing wiki page for ${group.id}: ${page}`);
    }
  }

  try {
    const sourceStat = statSync(sourceMapFile);
    const indexStat = statSync(indexFile);
    if (indexStat.mtimeMs < sourceStat.mtimeMs) warnings.push("Index file is older than source-map.md");
  } catch {
    warnings.push("Could not compare source-map.md and index mtimes");
  }

  return printCheck(errors, warnings);
}

function printCheck(errors: string[], warnings: string[]): number {
  for (const warning of warnings) console.log(`WARN ${warning}`);
  for (const error of errors) console.error(`ERROR ${error}`);
  if (errors.length === 0) {
    console.log("OK wiki index check passed");
    return 0;
  }
  return 1;
}

function scoreGroup(group: SourceGroup, queryTokens: string[]): number {
  const weighted = [
    [group.id, 8],
    [group.title, 6],
    [group.area, 5],
    [group.keywords.join(" "), 5],
    [group.purpose, 4],
    [group.primaryQuestions.join(" "), 3],
    [group.primaryFiles.map((file) => `${file.path} ${file.description}`).join(" "), 3],
    [group.supportingFiles.map((file) => `${file.path} ${file.description}`).join(" "), 2],
    [group.relatedWikiPages.join(" "), 2],
    [group.usedBy.join(" "), 2],
  ] as const;

  let score = 0;
  for (const [text, weight] of weighted) {
    const haystack = text.toLowerCase();
    for (const token of queryTokens) {
      if (haystack.includes(token)) score += weight;
    }
  }
  return score;
}

function search(projectPath: string, query: string): void {
  const index = readIndex(projectPath);
  const queryTokens = query
    .toLowerCase()
    .split(/[^a-z0-9а-яё_-]+/i)
    .map((token) => token.trim())
    .filter(Boolean);

  const matches = index.groups
    .map((group) => ({ group, score: scoreGroup(group, queryTokens) }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 8);

  if (matches.length === 0) {
    console.log(`No matches for: ${query}`);
    return;
  }

  console.log(`Top matches for: ${query}\n`);
  matches.forEach(({ group, score }, index) => {
    console.log(`${index + 1}. ${group.id} score=${score}`);
    console.log(`   ${group.title}`);
    if (group.purpose) console.log(`   Purpose: ${group.purpose}`);
    if (group.primaryFiles.length > 0) {
      console.log("   Files:");
      for (const file of group.primaryFiles.slice(0, 5)) console.log(`   - ${file.path}`);
    }
    if (group.relatedWikiPages.length > 0) {
      console.log("   Wiki:");
      for (const page of group.relatedWikiPages.slice(0, 5)) console.log(`   - ${page}`);
    }
    console.log("");
  });
}

const [, , command, subcommandOrProject, ...rest] = process.argv;

try {
  if (command === "index" && subcommandOrProject === "build") {
    const projectPath = rest[0];
    if (!projectPath) usage();
    build(path.resolve(projectPath));
  } else if (command === "index" && subcommandOrProject === "check") {
    const projectPath = rest[0];
    if (!projectPath) usage();
    process.exit(check(path.resolve(projectPath)));
  } else if (command === "search") {
    const projectPath = subcommandOrProject;
    const query = rest.join(" ");
    if (!projectPath || !query) usage();
    search(path.resolve(projectPath), query);
  } else {
    usage();
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
