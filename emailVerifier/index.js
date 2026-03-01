#!/usr/bin/env node
const fs = require("node:fs/promises");
const path = require("node:path");

const { normalizeEmail, validateSyntax, maskEmail } = require("./lib/validateSyntax");
const { dnsCheck } = require("./lib/dnsCheck");
const { smtpCheck } = require("./lib/smtpCheck");
const { classifyStatus } = require("./lib/scoring");

const roleNames = new Set(["info", "support", "admin", "sales", "contact", "billing"]);

function parseCsv(content) {
  const lines = content.split(/\r?\n/).filter((line) => line.trim().length > 0);
  if (lines.length === 0) return [];
  const headers = lines[0].split(",").map((h) => h.trim());
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    return headers.reduce((acc, header, idx) => {
      acc[header] = (values[idx] || "").trim();
      return acc;
    }, {});
  });
}

function toCsv(rows, columns) {
  const escape = (value) => {
    const str = String(value ?? "");
    if (str.includes(",") || str.includes("\n") || str.includes('"')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const header = columns.join(",");
  const body = rows.map((row) => columns.map((c) => escape(row[c])).join(",")).join("\n");
  return `${header}\n${body}\n`;
}

function loadDotEnv(content) {
  content.split(/\r?\n/).forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) return;
    const sep = trimmed.indexOf("=");
    if (sep === -1) return;
    const key = trimmed.slice(0, sep).trim();
    const value = trimmed.slice(sep + 1).trim();
    if (!(key in process.env)) {
      process.env[key] = value;
    }
  });
}

async function maybeLoadEnv() {
  const envPath = path.resolve(".env");
  try {
    const env = await fs.readFile(envPath, "utf8");
    loadDotEnv(env);
  } catch {
    // optional
  }
}

function parseArgs(argv) {
  const args = {
    in: "inputEmails.csv",
    out: "results.csv",
    concurrency: Number(process.env.CONCURRENCY || 3),
    smtp: (process.env.SMTP_ENABLED || "true").toLowerCase() !== "false",
  };

  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--in") args.in = value;
    if (key === "--out") args.out = value;
    if (key === "--concurrency") args.concurrency = Number(value);
    if (key === "--smtp") args.smtp = String(value).toLowerCase() === "true";
  }

  return args;
}

async function loadDisposableDomains(filePath) {
  const fullPath = path.resolve(filePath);
  const content = await fs.readFile(fullPath, "utf8");
  return new Set(
    content
      .split(/\r?\n/)
      .map((line) => line.trim().toLowerCase())
      .filter((line) => line && !line.startsWith("#")),
  );
}

async function runWithConcurrency(items, concurrency, worker) {
  const output = new Array(items.length);
  let index = 0;

  async function runner() {
    while (index < items.length) {
      const current = index;
      index += 1;
      output[current] = await worker(items[current]);
    }
  }

  const runnerCount = Math.min(Math.max(concurrency, 1), items.length || 1);
  await Promise.all(Array.from({ length: runnerCount }, () => runner()));
  return output;
}

async function main() {
  await maybeLoadEnv();
  const args = parseArgs(process.argv);
  const timeoutMs = Number(process.env.SMTP_TIMEOUT_MS || 6000);
  const hostname = process.env.SMTP_EHLO_HOST || "localhost";
  const mailFrom = process.env.SMTP_MAIL_FROM || "verify@example.com";
  const disposableDomains = await loadDisposableDomains(path.join(__dirname, "disposableDomains.txt"));

  const csvInput = await fs.readFile(path.resolve(args.in), "utf8");
  const rows = parseCsv(csvInput);

  const dedupedEmails = [...new Set(rows.map((row) => normalizeEmail(row.email)).filter(Boolean))];

  const results = await runWithConcurrency(dedupedEmails, args.concurrency, async (email) => {
    const syntax = validateSyntax(email);
    const masked = maskEmail(email);

    if (!syntax.syntaxValid) {
      console.log(`Processed ${masked}: invalid syntax`);
      return {
        emailMasked: masked,
        syntaxValid: false,
        domain: "",
        mxFound: false,
        smtpResultCode: "",
        disposable: false,
        roleBased: false,
        status: "invalid",
        notes: "Invalid syntax",
      };
    }

    const [, domain] = email.split("@");
    const localPart = email.split("@")[0] || "";
    const dns = await dnsCheck(domain);
    const disposable = disposableDomains.has(domain);
    const roleBased = roleNames.has(localPart);

    let smtp = { smtpResult: "not_attempted", smtpResultCode: "", notes: "SMTP disabled" };
    if (args.smtp && dns.mxFound) {
      smtp = await smtpCheck({
        email,
        mxRecords: dns.mxRecords,
        timeoutMs,
        mailFrom,
        hostname,
      });
    }

    const scored = classifyStatus({
      syntaxValid: syntax.syntaxValid,
      domainExists: dns.domainExists,
      mxFound: dns.mxFound,
      smtpResult: smtp.smtpResult,
      disposable,
      roleBased,
    });

    console.log(`Processed ${masked}: ${scored.status}`);

    return {
      emailMasked: masked,
      syntaxValid: syntax.syntaxValid,
      domain,
      mxFound: dns.mxFound,
      smtpResultCode: smtp.smtpResultCode,
      disposable,
      roleBased,
      status: scored.status,
      notes: [scored.notes, dns.notes, smtp.notes].filter(Boolean).join("; "),
    };
  });

  const csvOutput = toCsv(results, [
    "emailMasked",
    "syntaxValid",
    "domain",
    "mxFound",
    "smtpResultCode",
    "disposable",
    "roleBased",
    "status",
    "notes",
  ]);

  await fs.writeFile(path.resolve(args.out), csvOutput, "utf8");
  console.log(`Wrote ${results.length} records to ${args.out}`);
}

main().catch((err) => {
  console.error("Fatal error:", err.message);
  process.exitCode = 1;
});
