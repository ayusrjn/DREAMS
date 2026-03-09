---
trigger: always_on
---

---
name: python-clean-code
description: >
  Apply this skill whenever a Python developer agent is writing, reviewing, refactoring, or generating Python code.
  Trigger on any request to write a Python function, class, module, script, or system — including tasks like
  "write a parser", "build a pipeline", "create a CLI tool", "refactor this code", "add a new feature", or
  "implement this algorithm". This skill enforces opinionated, maintainable Python: self-documenting naming,
  minimal comments, flat structure, and clean interfaces. Use it even when the user doesn't ask for "clean code"
  explicitly — good defaults should always be on.
---

# Python Clean Code Skill

A developer agent using this skill writes Python that is easy to read, easy to change, and easy to delete.
The primary goal is code that communicates intent through structure and naming — not through comments.

---

## Core Philosophy

**Code is written once, read many times.**
Every line you write will be read by a future maintainer (often yourself). Optimize for the reader, not the writer.

**Clarity over cleverness.**
A straightforward solution that anyone can follow beats an elegant one-liner that requires a second read.

**Comments explain *why*, never *what*.**
If you need a comment to explain what the code does, the code itself is the problem — rename or restructure it.

---

## Naming

### Variables and Functions

Use names that make the operation obvious without needing surrounding context.

```python
# Bad
def proc(d, f):
    tmp = []
    for x in d:
        if f(x):
            tmp.append(x)
    return tmp

# Good
def filter_items(items, predicate):
    return [item for item in items if predicate(item)]
```

Rules:
- **Variables**: noun or noun phrase — `user_id`, `active_sessions`, `retry_count`
- **Booleans**: start with `is_`, `has_`, `can_`, `should_` — `is_valid`, `has_permission`
- **Functions**: verb or verb phrase — `fetch_user`, `calculate_score`, `parse_config`
- **Classes**: PascalCase noun — `UserRepository`, `EventProcessor`
- **Constants**: UPPER_SNAKE_CASE — `MAX_RETRIES`, `DEFAULT_TIMEOUT`
- **Never** use single-letter names except in tightly scoped list comprehensions (`i`, `x`, `k`, `v`)

### Length vs. Clarity

Longer names are almost always better than abbreviated ones. Abbreviations carry cognitive overhead.

```python
# Bad
usr_mgr.upd_pref(uid, prefs)

# Good
user_manager.update_preferences(user_id, preferences)
```

---

## Functions

### One Responsibility

A function should do one thing and do it completely. If you need "and" to describe what it does, split it.

```python
# Bad: fetches AND transforms AND saves
def process_report(report_id):
    data = db.fetch(report_id)
    transformed = {k: v.strip() for k, v in data.items()}
    db.save(transformed)

# Good: each step is named, testable, and replaceable
def process_report(report_id):
    raw_data = fetch_report(report_id)
    clean_data = normalize_report_fields(raw_data)
    save_report(clean_data)
```

### Arguments

- Prefer fewer than 4 arguments. More than 3 is a signal to introduce a data class or config object.
- Use keyword arguments for anything non-obvious at the call site.
- Use `*` to force keyword-only arguments when order would be confusing.

```python
# Bad: caller has no idea what True means
create_user("alice", True, False)

# Good
create_user("alice", is_admin=True, send_welcome_email=False)

# Better: enforce it
def create_user(username: str, *, is_admin: bool = False, send_welcome_email: bool = True):
    ...
```

### Return Values

- Return early to avoid deeply nested conditionals.
- Return a single type consistently — don't return `None` in some paths and a value in others unless the `None` is meaningful and typed as `Optional`.

```python
# Bad: deeply nested, hard to follow
def get_discount(user):
    if user:
        if user.is_member:
            if user.years_active > 5:
                return 0.20
            else:
                return 0.10
    return 0

# Good: guard clauses flatten the logic
def get_discount(user):
    if not user or not user.is_member:
        return 0
    if user.years_active > 5:
        return 0.20
    return 0.10
```

---

## Type Annotations

Always annotate function signatures. Use `from __future__ import annotations` for forward references.
Use `Optional[X]` (or `X | None` in Python 3.10+) explicitly — never rely on an implicit `None` return.

```python
from typing import Optional

def find_user(user_id: int) -> Optional[User]:
    ...

def batch_process(items: list[str], max_workers: int = 4) -> dict[str, bool]:
    ...
```

Annotate class attributes using dataclasses or explicit `__init__` signatures — never leave them implicit.

---

## Classes

### When to Use a Class

Use a class when:
- You need to group related state **and** behavior that evolves together
- You have multiple methods operating on the same data

Use a plain function or module-level functions when:
- There is no meaningful mutable state
- The "class" would just be a namespace wrapping static methods

```python
# Bad: class is just a function in disguise
class ReportFormatter:
    def format(self, data):
        return json.dumps(data, indent=2)

# Good
def format_report(data: dict) -> str:
    return json.dumps(data, indent=2)
```

### Data Classes for Plain State

Use `@dataclass` (or `pydantic.BaseModel`) for objects that primarily hold data.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class JobConfig:
    name: str
    max_retries: int = 3
    timeout_seconds: float = 30.0
    tags: list[str] = field(default_factory=list)
    callback_url: Optional[str] = None
```

### Keep `__init__` Simple

`__init__` should assign attributes, not perform logic. Extract logic into factory methods or helper functions.

```python
# Bad
class Pipeline:
    def __init__(self, config_path):
        with open(config_path) as f:
            raw = json.load(f)
        self.steps = [Step(s) for s in raw["steps"]]
        self.validate()

# Good
class Pipeline:
    def __init__(self, steps: list[Step]):
        self.steps = steps

    @classmethod
    def from_config_file(cls, config_path: str) -> "Pipeline":
        with open(config_path) as f:
            raw = json.load(f)
        steps = [Step(s) for s in raw["steps"]]
        return cls(steps)
```

---

## Comments and Docstrings

### The Rule

**Write a comment only when the code cannot be restructured to be self-explanatory.**

Ask before writing any comment: *Can I rename something or extract a function so this comment becomes unnecessary?* If yes — do that instead.

### When Comments Are Justified

1. **Non-obvious constraints or invariants** — requirements that come from outside the code

```python
# Stripe requires idempotency keys to be unique per customer, not globally
idempotency_key = f"{customer_id}:{order_id}"
```

2. **Known workarounds or bugs in dependencies**

```python
# boto3 pagination is broken for ListObjectsV2 when delimiter is set — fetch without delimiter
response = s3.list_objects_v2(Bucket=bucket)
```

3. **Performance-sensitive sections** where a clearer approach was intentionally rejected

```python
# Using a set here — O(1) lookup needed; list would make the outer loop O(n²)
seen_ids = set()
```

4. **TODO / FIXME** — always include a ticket or owner

```python
# TODO(ayush): replace with streaming once #482 is merged
results = load_all_records(query)
```

### Docstrings

Public APIs (modules, public classes, public functions) should have docstrings that describe the *contract*, not the implementation.

Format: one-line summary, then optional extended description, then Args/Returns/Raises only when non-obvious.

```python
def retry(func, *, max_attempts: int = 3, delay_seconds: float = 1.0):
    """
    Call func, retrying on any exception up to max_attempts times.

    Uses linear backoff — each retry waits delay_seconds longer than the last.
    Raises the final exception if all attempts fail.
    """
```

**Do not** write docstrings that just restate the signature:

```python
# Bad
def add(a: int, b: int) -> int:
    """Adds a and b and returns the result."""
    return a + b
```

---

## Structure and Layout

### Module Organization

Within a file, order by visibility and dependency:
1. Module-level constants
2. Helper / private functions (prefixed `_`)
3. Public classes and functions
4. Entry point (`if __name__ == "__main__":`)

### File Size

A file longer than ~300 lines is a signal to split by responsibility. Extract cohesive groups of functions into their own modules.

### Imports

- Standard library first, then third-party, then local — separated by blank lines
- Prefer explicit imports (`from module import SpecificThing`) over wildcard imports
- Never use `from module import *` in production code

```python
import os
import sys
from pathlib import Path

import httpx
from pydantic import BaseModel

from myapp.core import settings
from myapp.utils import slugify
```

### Magic Numbers

Replace all bare numeric and string literals with named constants.

```python
# Bad
if response.status_code == 429:
    time.sleep(60)

# Good
HTTP_TOO_MANY_REQUESTS = 429
RATE_LIMIT_COOLDOWN_SECONDS = 60

if response.status_code == HTTP_TOO_MANY_REQUESTS:
    time.sleep(RATE_LIMIT_COOLDOWN_SECONDS)
```

---

## Error Handling

### Be Specific

Never catch broad `Exception` unless you are at a top-level boundary and logging the error.

```python
# Bad
try:
    result = process(data)
except Exception:
    return None

# Good
try:
    result = process(data)
except ValueError as exc:
    logger.warning("Invalid data format: %s", exc)
    raise
```

### Custom Exceptions for Domain Errors

Define domain-specific exception classes to make error handling at call sites meaningful.

```python
class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

class RateLimitExceeded(Exception):
    """Raised when the API rate limit is hit."""
    def __init__(self, retry_after_seconds: float):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Rate limit exceeded. Retry after {retry_after_seconds}s.")
```

### Don't Swallow Errors Silently

A silent `except` block is one of the most dangerous patterns. Always log, re-raise, or return a typed failure signal.

---

## Testing Conventions

### Structure Each Test as Arrange / Act / Assert

```python
def test_discount_applied_for_senior_member():
    # Arrange
    user = User(is_member=True, years_active=6)

    # Act
    discount = get_discount(user)

    # Assert
    assert discount == 0.20
```

### Test Names Describe Behavior, Not Implementation

```python
# Bad
def test_get_discount_1():
    ...

# Good
def test_no_discount_for_non_member():
    ...

def test_full_discount_applied_after_five_years():
    ...
```

### One Logical Assertion Per Test

Multiple unrelated assertions in one test make failures ambiguous. Split them.

---

## Checklist Before Finalizing Any Code

Before declaring code complete, verify each of the following:

- [ ] Every function and variable name communicates intent without comments
- [ ] No function exceeds ~30 lines or does more than one thing
- [ ] All function signatures have type annotations
- [ ] Comments exist only for non-obvious *why* — not *what*
- [ ] No magic numbers or bare string literals
- [ ] Exceptions are specific, named, and never silently swallowed
- [ ] Public functions and classes have concise docstrings
- [ ] Imports are organized and no wildcard imports are used
- [ ] Guard clauses are used to eliminate deep nesting