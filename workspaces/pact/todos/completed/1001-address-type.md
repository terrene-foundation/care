# TODO-1001: Address Type and Grammar Validator

Status: pending
Priority: critical
Dependencies: [0003]
Milestone: M1

## What

Implement the `Address` value type in `src/pact/governance/addressing.py`. This is the
core data type for the entire PACT framework — every role, team, and department in a
compiled org has a unique `Address` that encodes both containment and accountability.

The Address type implements the D/T/R grammar from PACT-REQ-001. An address is a
sequence of tokens where each D (Department) or T (Team) unit is immediately followed
by exactly one R (Role). The grammar enforces this constraint; any sequence that
violates it must be rejected at parse time.

## Where

- `src/pact/governance/addressing.py` — full implementation
- `tests/unit/governance/test_addressing.py` — comprehensive test suite

## Evidence

- `Address.parse("D1-R1")` returns an Address object
- `Address.parse("D1-R1-D2-R2")` returns a nested Address
- `Address.parse("D1-R1-T1-R1")` returns a mixed depth Address
- `str(Address.parse(s)) == s` for all valid address strings (round-trip)
- `Address.parse("D1-D2-R1")` raises `AddressError` (D followed by D, not R)
- `Address.parse("D1-T1-R1")` raises `AddressError` (D followed by T, not R)
- `Address.parse("T1-T1-R1")` raises `AddressError` (T followed by T, not R)
- `Address.parse("T1-D1-R1")` raises `AddressError` (T followed by D, not R)
- `Address.parse("R1")` raises `AddressError` (R without preceding D or T)
- `Address.parse("")` raises `AddressError` (empty)
- `Address.parse("D1-R1").depth` returns 1
- `Address.parse("D1-R1-D2-R2").depth` returns 2
- `Address.parse("D1-R1").containment_unit` returns `"D1"` (the enclosing D/T unit)
- `Address.parse("D1-R1").accountability_chain` returns `["D1-R1"]`
- `Address.parse("D1-R1-D2-R2").accountability_chain` returns `["D1-R1", "D1-R1-D2-R2"]`
- `Address.parse("D1-R1").parent` returns `None` (root level has no parent)
- `Address.parse("D1-R1-D2-R2").parent` returns `Address.parse("D1-R1")`
- `Address.parse("D1-R1").is_prefix_of(Address.parse("D1-R1-D2-R2"))` returns `True`
- `Address.parse("D1-R1-D2-R2").is_prefix_of(Address.parse("D1-R1"))` returns `False`
- BOD root address `Address.parse("D1-R1")` where D1 is the top-level Board is valid
- `pytest tests/unit/governance/test_addressing.py` passes (all tests)

## Details

### Token grammar

An address token is one of:

- `D{n}` where n is a positive integer: Department unit
- `T{n}` where n is a positive integer: Team unit
- `R{n}` where n is a positive integer: Role within the immediately preceding D or T

The grammar state machine:

```
States: START, AFTER_D, AFTER_T, AFTER_R
Transitions:
  START  + D -> AFTER_D    (valid: first token is a D)
  START  + T -> AFTER_T    (valid: first token is a T — team at root level allowed)
  START  + R -> ERROR      (R cannot be first token)
  AFTER_D + R -> AFTER_R   (valid: D followed by R)
  AFTER_D + D -> ERROR     (D-D: grammar violation)
  AFTER_D + T -> ERROR     (D-T: grammar violation)
  AFTER_T + R -> AFTER_R   (valid: T followed by R)
  AFTER_T + T -> ERROR     (T-T: grammar violation)
  AFTER_T + D -> ERROR     (T-D: grammar violation)
  AFTER_R + D -> AFTER_D   (valid: Role followed by nested Department)
  AFTER_R + T -> AFTER_T   (valid: Role followed by nested Team)
  AFTER_R + R -> ERROR     (R-R: grammar violation)
Final state: AFTER_R (address must end after an R)
```

An empty token sequence is an error. An address that terminates in AFTER_D or AFTER_T
(a D or T without its R) is an error.

### Address class interface

```python
@dataclass(frozen=True)
class Address:
    tokens: tuple[str, ...]   # e.g. ("D1", "R1", "D2", "R2")

    @classmethod
    def parse(cls, s: str) -> "Address": ...

    def __str__(self) -> str: ...          # "D1-R1-D2-R2"

    @property
    def depth(self) -> int: ...            # number of D/T levels (not total tokens)

    @property
    def containment_unit(self) -> str: ... # the innermost D/T token, e.g. "D2"

    @property
    def accountability_chain(self) -> list["Address"]: ...
    # all ancestors including self, from root to self

    @property
    def parent(self) -> "Address | None": ...
    # address of the enclosing role (strip last D/T + R pair), or None if root

    def is_prefix_of(self, other: "Address") -> bool: ...
    # True if self.tokens == other.tokens[:len(self.tokens)]

    def format(self, sep: str = "-") -> str: ...
    # format with custom separator (useful for display)
```

### AddressError

```python
class AddressError(ValueError):
    """Raised when an address string violates the D/T/R grammar."""
    def __init__(self, message: str, token: str | None = None, position: int | None = None):
        super().__init__(message)
        self.token = token
        self.position = position
```

The error message must identify the specific violation:

- `"Expected R after D1 at position 1, got D2"` for D-D violation
- `"Address cannot start with R token"` for bare R
- `"Address must end with an R token, got D3"` for incomplete sequence

### BOD root handling

The Board of Directors (BOD) is the trust root of a PACT organization. By convention,
the top-level address is `D{n}-R{n}` where D{n} is the top-level governing body.
The Address type does not hardcode any specific numbering — it accepts any valid D-R
pair as a root-level address. The caller (OrgDefinition builder) assigns the actual
numbers. The root address `D1-R1` means "Department 1, Role 1" which is the standard
starting point, but `D2-R1` or `D3-R5` are equally valid as root addresses.

### Token parsing

Token format: letter(s) followed by positive integer, e.g. `D1`, `T12`, `R3`.
Use a regex `^([DT]|R)(\d+)$` to parse each token. The integer component must be
a positive integer (no zero, no leading zeros beyond a single digit).

Reject tokens that don't match: `Address.parse("D0-R1")` raises `AddressError`
because D0 is not a valid department number (must be >= 1).

### Implementation notes

Use `@dataclass(frozen=True)` so Address instances are hashable and usable as dict
keys (important for the CompiledOrg node lookup in TODO-1003).

The `parse` class method is the only entry point for creating an Address from a
string. Direct construction via `Address(tokens=(...))` bypasses grammar validation
and must not be used in production code (though it may appear in tests that build
pre-validated addresses for performance reasons, always with a comment explaining why).

Prefer raising `AddressError` over returning `None` on invalid input. The PACT grammar
is strict — any input that violates it is a programming error, not a runtime condition
to be silently handled.

### Test structure

Organize `test_addressing.py` into clear sections:

1. Valid parse cases — a representative sample of legal address strings
2. Round-trip invariants — `str(Address.parse(s)) == s` for all valid cases
3. Grammar violation cases — one test per illegal transition type
4. Property tests — depth, containment_unit, accountability_chain, parent
5. Prefix query tests — is_prefix_of
6. Edge cases — single-token D-R pairs, deeply nested addresses (5+ levels),
   addresses with large unit numbers (D999-R999)
