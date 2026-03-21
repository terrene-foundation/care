# TODO-1004: Prefix-Containment Queries

Status: pending
Priority: high
Dependencies: [1003]
Milestone: M1

## What

Extend `CompiledOrg` in `src/pact/governance/compilation.py` with efficient
prefix-containment queries. The core operation is `query_by_prefix(prefix)`:
given a positional address prefix, return all nodes in the org whose address
starts with that prefix. This enables "everything under CFO", "everyone in
the Trading Division", and "all agents in Compliance Team" queries.

`get_subtree(address)` is the companion: return the node at the given address
plus all its descendants. Both methods return results in depth-first order.

The index built during `compile_org` must make prefix queries O(n) in the size
of the result set, not O(total nodes). A trie or sorted-string prefix scan
on the address index achieves this.

## Where

- `src/pact/governance/compilation.py` — extend `CompiledOrg` (no new files)
- `tests/unit/governance/test_prefix_queries.py` — focused test suite (~80 LOC)

## Evidence

- `compiled.query_by_prefix("D1-R1-D3")` on the financial services org returns
  exactly: Head of Trading, Senior Trader (the two roles in Trading Division)
- `compiled.query_by_prefix("D1-R1-D1")` returns: Head of Compliance, AML Specialist
- `compiled.query_by_prefix("D1-R1")` returns all nodes at depth 2+ (every role
  under the CEO)
- `compiled.query_by_prefix("D1")` returns all nodes in the entire org
- `compiled.query_by_prefix("D1-R1-D99")` returns `[]` (no nodes match)
- `compiled.get_subtree("D1-R1-D3-R1")` returns Head of Trading and Senior Trader
- `compiled.get_subtree("D1-R1-D3-R1")` returns depth-first ordering:
  Head of Trading first, then its reports
- Results are `list[CompiledNode]`, always in depth-first order
- The prefix node itself is included in query results
- `pytest tests/unit/governance/test_prefix_queries.py` passes

## Details

### Why prefix queries matter

The access enforcement algorithm (TODO-2006) needs to answer questions like:

- "Does agent A (at address X) have read access to items owned by role B (at address Y)?"
- The answer depends on whether X is in Y's subtree, or vice versa, or neither

Prefix queries are the primitive that makes this efficient. Without them, the access
algorithm would have to traverse the entire org tree for every access check.

### Implementation approach

During `compile_org`, the `_index` dict maps `str(address) -> CompiledNode`.
For prefix queries, a sorted list of address strings enables binary-search-based
prefix scans. Alternatively, since address strings use a consistent separator (`-`),
a simple prefix check `address_str.startswith(prefix_str + "-")` on the index keys
works correctly without a trie.

The `query_by_prefix` implementation:

```python
def query_by_prefix(self, prefix: Address | str) -> list[CompiledNode]:
    prefix_str = str(prefix) if isinstance(prefix, Address) else prefix
    # Include the prefix node itself if it exists
    # Include all nodes whose address starts with prefix_str + "-"
    results = [
        node for addr_str, node in self._index.items()
        if addr_str == prefix_str or addr_str.startswith(prefix_str + "-")
    ]
    # Sort depth-first: by address string length, then lexicographically
    return sorted(results, key=lambda n: (len(n.address.tokens), str(n.address)))
```

The prefix separator `-` ensures `"D1-R1-D3"` does not accidentally match
`"D1-R1-D30-R1"` (which would happen with a naive `startswith("D1-R1-D3")`).

### get_subtree

`get_subtree(address)` is equivalent to `query_by_prefix(address)` but is a
semantically clearer name for the common case of "give me this node and all
its descendants". Both methods return identical results when called with the
same address.

Consider making `get_subtree` an alias for `query_by_prefix` or implementing it
in terms of `query_by_prefix` to avoid duplicated logic.

### Depth-first ordering

Results must be returned in depth-first order, not arbitrary dict iteration order.
The sort key `(len(tokens), str(address))` achieves this:

- Shorter addresses (higher in the hierarchy) come first
- Siblings at the same depth are ordered by their address string (lexicographic)

Note: lexicographic ordering of address strings produces correct depth-first order
because PACT address numbers are assigned in depth-first traversal order during
compilation. If the numbering scheme changes, the sort key may need adjustment.

### Edge cases

- `query_by_prefix(address)` where `address` is not in the org: returns `[]`
  (not an error — the prefix may not have any nodes)
- `query_by_prefix(root_address)`: returns all nodes (root + entire tree)
- Single-node org: `query_by_prefix(root_address)` returns `[root_node]`
- Team prefix vs dept prefix: `T1-R1` and `D1-R1` are different prefixes; a query
  for `D1-R1` does not match nodes in a `T1-...` subtree

### Test file structure

Use the financial services org from `test_compilation.py` as the shared fixture.
Define it once in `conftest.py` (in `tests/unit/governance/`) so both test files
can use it.

Tests to include:

1. Trading Division query: `query_by_prefix("D1-R1-D3")` → trading head + traders
2. Compliance Team query: `query_by_prefix("D1-R1-D1")` → compliance head + AML
3. CEO subtree query: `query_by_prefix("D1-R1")` → all nodes below CEO
4. Root query: `query_by_prefix("D1")` → all nodes in org
5. Non-existent prefix: `query_by_prefix("D1-R1-D99")` → `[]`
6. get_subtree consistency: `get_subtree(a) == query_by_prefix(a)` for several addrs
7. Depth-first ordering: assert first result is the prefix node, not a deep descendant
8. Single-node org: query on root returns `[root]`
