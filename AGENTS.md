<!-- BILL-CUT MUSTS (non-negotiable, every session) -->
0. ADDRESS USER AS "SIR": call the user Sir in every reply. One "sir", natural, not groveling.
1. RTK MUST: prefix every bash command with `rtk` (installed: brew, /opt/homebrew/bin/rtk). Passthrough-safe.
2. HEADROOM MUST: proxy on 127.0.0.1:8787 (launchd: com.headroom.default). Use headroom_compress for large outputs; retrieve by hash only when needed.
3. PONYTAIL MUST: laziest working solution. YAGNI ladder first (/tmp/ponytail/AGENTS.md). No unrequested abstractions/files. Deletion over addition.
4. HUMANIZER MUST: human rewrite, keep meaning (/tmp/humanizer/SKILL.md). No AI tells.
6. ADHD MUST (always-on): lead with answer/action, number steps, one next action, cap lists at 5, no preamble/recap/closers. Full rules: `~/.config/opencode/skills/i-have-adhd/SKILL.md`.
7. CONTEXT-MODE MUST: sandbox via ctx_* tools, never raw dumps (see below).
8. PROGRESS MUST: silent run, short numbered updates only ([→] doing / [✓] done), one line each. No commands, code, diffs, logs, file contents, thoughts, or tool output. Hide all internals.
<!-- /BILL-CUT MUSTS -->

<!-- no-ai-slop:start -->
# NO-AI-SLOP MUST (non-negotiable, every session, all writing output)

Any prose you output for the user (replies, summaries, drafts, release notes, comments, docs) must read human, not generated. Full skill at `~/.config/opencode/skills/no-ai-slop/SKILL.md` — load it when asked to edit/audit a draft. Mandatory baseline, always:

**Banned outright:** delve, foster, leverage, utilize, facilitate, empower, streamline, robust, cutting-edge, paradigm shift, game changer, this is huge/this changes everything, tapestry, realm, beacon, multifaceted, meticulous, intricate, paramount, transformative, elevate, embark, supercharge, harness, ever-evolving, "let's dive in", "at the end of the day".

**Cut when empty:** just, literally, actually, truly, simply, fundamentally, it's worth noting, importantly, crucially, due to the fact that, when it comes to, in terms of, going forward.

**Patterns:** no binary "It's not X, it's Y" teases, no throat-clearing ("Here's the thing", "Let me be clear"), no faux-insight ("what most people get wrong"), no colon reveals, no trailing "-ing" pseudo-explanation, no importance puffery ("marks a pivotal moment"), no recap endings ("In conclusion"), no em-dash clusters, no emoji decoration, no robotic parallel rhythm. State the point directly and let facts carry it.

**Tone (respectable = human, not corporate):** plain words over jargon, active voice, one point per sentence. No superlatives or hype verbs (unlock, supercharge, skyrocket, next-level, seamless, game-changing). No "I hope this helps", "Let me know if you have questions", or any sign-off fluff. No hedging piles ("I might be able to possibly help"). Give the answer, then at most one line on what's skipped or risky.

**Voice:** keep the user's cadence, bluntness, humor, and edge. Minimum effective edit. Concrete over abstract ("cut review time from 30 min to 8", not "improved efficiency").
<!-- no-ai-slop:end -->
- To regenerate the legacy JavaScript SDK, run `./packages/sdk/js/script/build.ts`.
- After changing the public Protocol or Server `HttpApi`, run `bun run generate` from `packages/client`. Do not edit `src/generated` or `src/generated-effect` directly.
- Keep runtime dependencies directed from Schema to Core and Protocol, then from Core and Protocol to Server. Client runtime code may depend on Schema and Protocol but never Core or Server; `sdk-next` composes Client, Core, and Server.
- The default branch in this repo is `dev`.
- Local `main` ref may not exist; use `dev` or `origin/dev` for diffs.

## Branch Names

Use a short branch name of at most three words, separated by hyphens. Do not use slashes or type prefixes such as `feat/` or `fix/`.

Examples: `session-recovery`, `fix-scroll-state`, `regenerate-sdk`.

## Commits and PR Titles

Use conventional commit-style messages and PR titles: `type(scope): summary`.

Valid types are `feat`, `fix`, `docs`, `chore`, `refactor`, and `test`. Scopes are optional; use the affected package or area when helpful, e.g. `core`, `opencode`, `tui`, `app`, `desktop`, `sdk`, or `plugin`.

Examples: `fix(tui): simplify thinking toggle styling`, `docs: update contributing guide`, `chore(sdk): regenerate types`.

## Style Guide

### General Principles

- Keep things in one function unless composable or reusable
- Do not extract single-use helpers preemptively. Inline the logic at the call site unless the helper is reused, hides a genuinely complex boundary, or has a clear independent name that improves the caller.
- Avoid `try`/`catch` where possible
- Avoid using the `any` type
- Use Bun APIs when possible, like `Bun.file()`
- Rely on type inference when possible; avoid explicit type annotations or interfaces unless necessary for exports or clarity
- Prefer functional array methods (flatMap, filter, map) over for loops; use type guards on filter to maintain type inference downstream
- In `src/config`, follow the existing self-export pattern at the top of the file (for example `export * as ConfigAgent from "./agent"`) when adding a new config module.
- In Effect generators, bind services to named variables before calling methods. Do not use nested service yields such as `yield* (yield* Foo.Service).bar()`.

Reduce total variable count by inlining when a value is only used once.

```ts
// Good
const journal = await Bun.file(path.join(dir, "journal.json")).json()

// Bad
const journalPath = path.join(dir, "journal.json")
const journal = await Bun.file(journalPath).json()
```

### Destructuring

Avoid unnecessary destructuring. Use dot notation to preserve context.

```ts
// Good
obj.a
obj.b

// Bad
const { a, b } = obj
```

### Imports

- Never alias imports. Do not use `import { foo as bar } from "..."` or renamed imports like `resolve as pathResolve`.
- Never use star imports. Do not use `import * as Foo from "..."` or `import type * as Foo from "..."`.
- If a namespace-style value is needed, import the module's own exported namespace by name, for example `import { Project } from "@opencode-ai/core/project"`, then reference `Project.ID`.
- Prefer dynamic imports for heavy modules that are only needed in selected code paths, especially in startup-sensitive entrypoints. Destructure dynamic import bindings near the top of the narrowest scope that needs them so they read like normal imports. Avoid inline chains such as `await import("./module").then((mod) => mod.value())` or `(await import("./module")).value()`. Keep branch-specific imports inside the branch that needs them to preserve lazy loading.

### Variables

Prefer `const` over `let`. Use ternaries or early returns instead of reassignment.

```ts
// Good
const foo = condition ? 1 : 2

// Bad
let foo
if (condition) foo = 1
else foo = 2
```

### Control Flow

Avoid `else` statements. Prefer early returns.

```ts
// Good
function foo() {
  if (condition) return 1
  return 2
}

// Bad
function foo() {
  if (condition) return 1
  else return 2
}
```

### Complex Logic

When a function has several validation branches or supporting details, make the main function read as the happy path and move supporting details into small helpers below it.

```ts
// Good
export function loadThing(input: unknown) {
  const config = requireConfig(input)
  const metadata = readMetadata(input)
  return createThing({ config, metadata })
}

function requireConfig(input: unknown) {
  ...
}
```

- Keep helpers close to the code they support, below the main export when that improves readability.
- Do not over-abstract simple expressions into many single-use helpers; extract only when it names a real concept like `requireConfig` or `readMetadata`.
- Do not return `Effect` from helpers unless they actually perform effectful work. Synchronous parsing, validation, and option building should stay synchronous.
- Prefer Effect schema helpers such as `Schema.UnknownFromJsonString` and `Schema.decodeUnknownOption` over manual `JSON.parse` wrapped in `Effect.try` when parsing untrusted JSON strings.
- Add comments for non-obvious constraints and surprising behavior, not for obvious assignments or control flow.

### Schema Definitions (Drizzle)

Use snake_case for field names so column names don't need to be redefined as strings.

```ts
// Good
const table = sqliteTable("session", {
  id: text().primaryKey(),
  project_id: text().notNull(),
  created_at: integer().notNull(),
})

// Bad
const table = sqliteTable("session", {
  id: text("id").primaryKey(),
  projectID: text("project_id").notNull(),
  createdAt: integer("created_at").notNull(),
})
```

## Testing

- Avoid mocks as much as possible, you shouldn't be using globalThis.\* at all unless it's the only option.
- Test actual implementation, do not duplicate logic into tests
- Tests cannot run from repo root (guard: `do-not-run-tests-from-root`); run from package dirs like `packages/opencode`.

## Type Checking

- Always run `bun typecheck` from package directories (e.g., `packages/opencode`), never `tsc` directly.

## V2 Session Core

- Keep durable prompt admission separate from model execution. `SessionV2.prompt(...)` admits one durable `session_input` row before scheduling advisory `SessionExecution.wake(sessionID)` unless `resume: false` requests admit-only behavior. The serialized runner promotes admitted inputs into visible user messages at safe boundaries.
- Reusing a Session ID adopts the existing Session. Reusing a prompt message ID reconciles an exact retry only when Session, prompt, and delivery mode match; conflicting reuse fails. Historical projected prompts lazily synthesize promoted inbox records during exact retry.
- Keep `SessionExecution` process-global and Session-ID based. Its local implementation owns the process-local Session coordinator and discovers placement through `SessionStore` plus `LocationServiceMap.get(session.location)` only when a drain starts; no layer should take a Session ID. V2 interruption targets the active process-local ownership chain for that Session; idle or missing interruption is a no-op.
- Keep `SessionRunner`, model resolution, tool registry, permissions, and filesystem Location-scoped. Omitted `Location.workspaceID` means implicit-local placement; explicit workspace identity remains reserved for future placement semantics.
- Preserve one explicit `llm.stream(request)` call per provider turn and reload projected history before durable continuation. Do not bridge through legacy `SessionPrompt.loop(...)` or delegate orchestration to an in-memory tool loop.
- Keep local Session drains process-local until clustering is implemented. `SessionRunCoordinator` joins explicit same-Session resumes, coalesces prompt wakeups, and allows different Sessions to run concurrently. Advisory wakes drain eligible durable inbox rows only; post-crash continuation recovery requires a separate explicit design before it may retry provider work. A drain has no durable identity or transcript boundary.
- Keep delivery vocabulary explicit. Prompts steer by default and promote at the next safe provider-turn boundary while the current drain requires continuation. An explicit `queue` input remains pending until the Session would otherwise become idle; promote one queued input at that boundary, then reevaluate continuation before promoting another. Promoting any new user input resets the selected agent's provider-turn allowance; a batch of steers resets it once.
- Keep EventV2 replay owner claims separate from clustered Session execution ownership.
- Keep the System Context algebra, registry, and built-ins in `src/system-context`; keep Context Source producers with their observed domains, and keep Session History selection plus Context Epoch persistence Session-owned.

<!-- OUTPUT OVERRIDE (wins over all above): one point per sentence, max 5 numbered single-line bullets, lead with answer, one Sir, one next action. No preamble, no file dumps, no tool theater. -->
