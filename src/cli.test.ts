import { execSync, ExecSyncOptionsWithStringEncoding } from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

const DATA_FILE = path.join(os.homedir(), ".todo-items.json");
const CLI = path.resolve(__dirname, "../dist/cli.js");

const execOpts: ExecSyncOptionsWithStringEncoding = {
  encoding: "utf-8",
  stdio: ["pipe", "pipe", "pipe"],
};

function run(args: string): string {
  return execSync(`node ${CLI} ${args}`, execOpts).trim();
}

function runRaw(args: string): { stdout: string; stderr: string; status: number } {
  try {
    const stdout = execSync(`node ${CLI} ${args}`, execOpts).trim();
    return { stdout, stderr: "", status: 0 };
  } catch (e: unknown) {
    const err = e as { stdout?: string; stderr?: string; status?: number };
    return {
      stdout: (err.stdout ?? "").trim(),
      stderr: (err.stderr ?? "").trim(),
      status: err.status ?? 1,
    };
  }
}

beforeEach(() => {
  // Reset data file before each test
  if (fs.existsSync(DATA_FILE)) {
    fs.unlinkSync(DATA_FILE);
  }
});

afterAll(() => {
  if (fs.existsSync(DATA_FILE)) {
    fs.unlinkSync(DATA_FILE);
  }
});

// ── Human-readable output (regression) ───────────────────────────────────────
describe("human-readable output (no --json)", () => {
  it("add: prints a confirmation message", () => {
    const out = run('add "Buy milk"');
    expect(out).toMatch(/Added:/);
    expect(out).toMatch(/Buy milk/);
  });

  it("list: prints items", () => {
    run('add "Task A"');
    run('add "Task B"');
    const out = run("list");
    expect(out).toMatch(/Task A/);
    expect(out).toMatch(/Task B/);
  });

  it("list: prints message when empty", () => {
    const out = run("list");
    expect(out).toMatch(/No todo items found/);
  });

  it("done: prints confirmation", () => {
    run('add "Finish report"');
    const out = run("done 1");
    expect(out).toMatch(/Done:/);
    expect(out).toMatch(/Finish report/);
  });
});

// ── JSON output ───────────────────────────────────────────────────────────────
describe("--json flag", () => {
  describe("add --json", () => {
    it("outputs valid JSON", () => {
      const raw = run('add "Buy milk" --json');
      expect(() => JSON.parse(raw)).not.toThrow();
    });

    it("returns success:true with the new item", () => {
      const raw = run('add "Buy milk" --json');
      const result = JSON.parse(raw);
      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data.text).toBe("Buy milk");
      expect(result.data.done).toBe(false);
      expect(typeof result.data.id).toBe("number");
      expect(typeof result.data.createdAt).toBe("string");
    });

    it("assigns incrementing IDs", () => {
      const r1 = JSON.parse(run('add "First" --json'));
      const r2 = JSON.parse(run('add "Second" --json'));
      expect(r2.data.id).toBeGreaterThan(r1.data.id);
    });
  });

  describe("list --json", () => {
    it("outputs valid JSON for empty list", () => {
      const raw = run("list --json");
      expect(() => JSON.parse(raw)).not.toThrow();
    });

    it("returns success:true with empty array when no items", () => {
      const result = JSON.parse(run("list --json"));
      expect(result.success).toBe(true);
      expect(Array.isArray(result.data)).toBe(true);
      expect(result.data).toHaveLength(0);
    });

    it("returns all items in data array", () => {
      run('add "Alpha"');
      run('add "Beta"');
      const result = JSON.parse(run("list --json"));
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(2);
      const texts = result.data.map((i: { text: string }) => i.text);
      expect(texts).toContain("Alpha");
      expect(texts).toContain("Beta");
    });

    it("each item has id, text, done, createdAt fields", () => {
      run('add "Check fields"');
      const result = JSON.parse(run("list --json"));
      const item = result.data[0];
      expect(item).toHaveProperty("id");
      expect(item).toHaveProperty("text");
      expect(item).toHaveProperty("done");
      expect(item).toHaveProperty("createdAt");
    });
  });

  describe("done --json", () => {
    it("outputs valid JSON on success", () => {
      run('add "Finish task"');
      const raw = run("done 1 --json");
      expect(() => JSON.parse(raw)).not.toThrow();
    });

    it("returns success:true with the updated item", () => {
      run('add "Finish task"');
      const result = JSON.parse(run("done 1 --json"));
      expect(result.success).toBe(true);
      expect(result.data.done).toBe(true);
      expect(result.data.id).toBe(1);
    });

    it("reflects the done:true in list --json after marking done", () => {
      run('add "Write tests"');
      run("done 1 --json");
      const list = JSON.parse(run("list --json"));
      const item = list.data.find((i: { id: number }) => i.id === 1);
      expect(item.done).toBe(true);
    });

    it("returns success:false with error on invalid ID (non-numeric)", () => {
      const { stdout, status } = runRaw("done abc --json");
      expect(status).not.toBe(0);
      const result = JSON.parse(stdout);
      expect(result.success).toBe(false);
      expect(typeof result.error).toBe("string");
    });

    it("returns success:false with error on missing ID", () => {
      const { stdout, status } = runRaw("done 999 --json");
      expect(status).not.toBe(0);
      const result = JSON.parse(stdout);
      expect(result.success).toBe(false);
      expect(typeof result.error).toBe("string");
    });
  });
});
