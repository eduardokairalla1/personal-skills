# Personal standards baseline

Distilled from the guidelines of my own projects (code-royale,
lectern, EcoaNetwork). It applies to every repo of mine, in every language,
unless the repo's own documented standard says otherwise: **the repo
overrides this file.** Skip anything the repo's tooling already enforces
(ruff, eslint, prettier, mypy, tsc): a finding the linter would print is
noise in a review.

Each rule has an id (`G1`, `L2`...) so a finding can cite it.

## General (G)

- **G1 English only.** Names, comments, docstrings, log and error messages,
  commit messages. A word in another language is a finding.
- **G2 80 columns.** Break long imports, signatures and chained calls.
- **G3 Single quotes** for strings and imports. Double quotes only as text
  inside a string.
- **G4 Names say the purpose, not the library.** `formatValidationErrors`,
  not `formatZodIssues`. The library shows up in the type and the import.
- **G5 No speculative code.** No option, parameter, layer, hook or folder
  that nothing in the change needs. No empty folder "for later".

## File layout (L)

- **L1 Header.** Every file starts with a one-line docstring or comment
  summarising the module. A short paragraph only when the *design* needs
  explaining so nobody "fixes" it wrongly later.
- **L2 Section markers**, in this order, empty ones left out, one blank line
  between them:
  - `IMPORTS`: one import per line, sorted by module, no blank lines between
    groups. Python: `from` imports before plain `import`, first-party is
    `src`. TypeScript: `import` and `import type` share the same order.
  - `GLOBALS`: constants, schemas, module state, `logger`.
  - `CODE`: types, interfaces, classes and functions.
  - `EXPORTS` (TypeScript only, special cases): re-exports and aliases.
    Everything else is exported inline on the declaration.
  - A more specific marker (`PAYLOADS`, `RESPONSES`, `INPUT`/`PIPELINE`/
    `OUTPUT`) is fine when it genuinely helps; the default is `CODE`.
- **L3 Spacing.** Python: two blank lines between every function, methods
  inside a class included (stricter than PEP 8; ruff cannot check it).
  TypeScript: one blank line right after the `{` that opens a function,
  except one-liners (getters, a plain `return`).

## Docstrings (D)

- **D1 Every function has one**, constructors, getters, interface methods
  and private helpers included. One sentence, on its own line, saying what
  it does. Types, interfaces and classes get the sentence, no tags.
- **D2 Parameters documented.** Python: `:param name: Description.` for each
  argument and `:return: Description.`, a blank line before the first
  `:param:` and before `:return:`. TypeScript: `@param {Type} name
  Description.`, `@returns {Type} Description.` (`{void}` /
  `{Promise<void>}` when nothing is returned), `@throws {ErrorClass} When
  ...` for application errors, continuation lines aligned with the start of
  the description.
- **D3 Accepted exceptions** (arguments are not the reader's question):
  framework validators whose argument is the field itself, nested closures,
  and test functions (fixtures are injected, never passed by hand, so they
  carry no `:param:`).

## Comments (C)

- **C1 Lowercase, above the block**, saying what happens and why.
  Capitalise only a proper noun or acronym (`# Redis is unavailable: ...`).
- **C2 One line is the target, two the ceiling.** Longer belongs in a
  docstring, the README, or means the code below wants splitting.
- **C3 `NOTE:` is the one exception** to the ceiling: a constraint, a trap,
  or why the obvious simplification is wrong may take a paragraph.
- **C4 A comment that repeats the code earns nothing.** One that records a
  decision, a constraint or a non-obvious consequence earns its place.
- **C5 The comment of a `catch`/`except` goes on the line before it**, not
  inside the block.

## Simplicity (S)

- **S1 A human reviews and maintains this.** Code only its author or an AI
  assistant can follow is a defect, however correct. If a change cannot be
  explained in a sentence, simplify it before proposing it.
- **S2 Prefer a data structure to an `if`/`elif` chain.** A dict keyed by
  what you branch on, read with `.get()`; an ordered tuple resolved by one
  `next(...)` when order matters, with the ordering rule in a comment beside
  the data.
- **S3 Watch the branch count.** Many nested conditions means several
  functions or one function plus a table. Guard clauses that return early
  beat nested `if`s; a flat sequence of steps beats a tree.
- **S4 Generated code is suspect by default.** AI assistants produce dense,
  heavily branched code with extra layers, options nobody asked for and
  checks for cases that cannot happen. Cut it down to what the change needs.

## Architecture (A)

- **A1 Organised by domain**, not by file type (a modular monolith):
  `modules/<domain>/<domain>.{types,errors,service,utils,routes,socket}.ts`
  or the Python equivalent. Business rules live in the service; routes and
  handlers only validate input and call it.
- **A2 Interfaces only where the implementation will change** (a store, an
  executor). Not as a reflex.
- **A3 Every external input is validated** at the edge (body, params,
  socket events, env vars) with the project's schema library (Zod,
  Pydantic), through the project's one helper, never a bare `.parse()`
  scattered around.
- **A4 Config lives in one validated schema** (`config.ts` / `config.py`),
  with type and default per variable; an invalid env stops the boot. New
  variables also go into `.env.example`. Values shared across modules that
  are not deployment-tunable get a neutral home (a `ClassVar`, a constant),
  not an env var.
- **A5 Backend and frontend are independent projects**, no shared code.

## Errors (E)

- **E1 One class per failure mode**, extending the app's base error
  (`AppError` / `BackendError`), declaring `MESSAGE`, `STATUS_CODE` and how
  it is logged. The response slug derives from the class name
  (`RoomNotFoundError` → `room_not_found_error`); one handler covers every
  subclass. Never build an error response by hand.
- **E2 Details go to the logs only**, never to the client, unless the class
  overrides the response on purpose (a validation error listing fields).
- **E3 Do not re-type an error you cannot classify.** Wrapping a provider
  error into a generic one costs the layers above the type they classify
  on. Log with `exc_info=True` and re-raise.
- **E4 `try` wraps what can legitimately fail**, not a whole function. A
  `try` around a step's entire body turns a bug in your own code into the
  same warning as a timeout.

## Types (T)

- **T1 Closed vocabularies are types**, not conventions: `Literal[...]` in
  Python, a union of string literals in TypeScript. A bare `str` for a tag
  the database `CHECK` rejects is a bug waiting.
- **T2 Fully typed.** Every function signature typed (`disallow_untyped_defs`
  in Python, no implicit `any` in TypeScript). Modern syntax: `X | None`,
  PEP 695 generics, not `Optional[X]`.
- **T3 Naming by role.** Route input schemas end in `Payload`, route output
  in `Response`, one module per route. Objects that outlive a request are
  application state, not schemas. Shapes more than one layer speaks live in
  a shared `types` home; a pipeline's own vocabulary lives beside it.

## Migrations (M)

- **M1 A migration is a snapshot.** It never imports a value that can
  change. A constant mirrored in a migration is a deliberate, commented
  duplication; changing the constant means a new revision.

## Tests (Te)

- **Te1 The name is the documentation.** A sentence:
  `test_response_invalid_session_id_returns_400`. A docstring only when the
  reason is not in the name; one that restates the name earns nothing.
- **Te2 Tests target contracts**: status codes, response shape, events
  emitted, persistence scheduled. Files mirror the surface under test
  (`tests/unit/t_*.py`), not the module tree.
- **Te3 New behaviour comes with tests.** A fix that depends on a seam gets
  the test that fails without it, and that failure is verified: a test that
  passes for the wrong reason is worse than none.
- **Te4 The checks run before the commit.** `scripts/test`, `npm run
  typecheck && npm test`, `go vet ./... && go test ./...`: whatever the repo
  documents.

## Commits (K)

- **K1 Atomic.** One change per commit, every commit leaves the code
  working.
- **K2 Message** in English, imperative, at most 50 characters, no prefix,
  no period: `Add a timer to the lobby`, not `feat: added timer.`
- **K3 Say what changes for the product**, not which function changed. A
  body only when the why is not obvious from the code.
- **K4 Dependencies and settings get their own commit**, placed right before
  the first commit that uses them. Version bumps are their own commit, at
  the end.
- **K5 No AI attribution** in messages or PR bodies.
