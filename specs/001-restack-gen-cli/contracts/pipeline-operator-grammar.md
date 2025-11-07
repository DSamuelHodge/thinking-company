# Contract: Pipeline Operator Grammar

**Feature**: 001-restack-gen-cli  
**Date**: November 6, 2025  
**Status**: Draft  
**Related**: FR-004 (Operator grammar for pipelines), US3 (Complex pipelines), research.md (Declarative Pipeline Operators)

## Purpose

Defines the formal grammar and semantics for pipeline composition operators used in complex workflow generation.

## Operator Definitions

### Sequence Operator: `→`

**Syntax**: `ComponentA → ComponentB → ComponentC`

**Semantics**: Execute components sequentially, passing output of each as input to the next

**Example**:
```python
# Generated workflow code
async def pipeline():
    result_a = await ComponentA()
    result_b = await ComponentB(result_a)
    result_c = await ComponentC(result_b)
    return result_c
```

**Properties**:
- **Order**: Left-to-right execution
- **Data flow**: Output of left becomes input of right
- **Error handling**: Failure halts pipeline unless configured otherwise
- **Precedence**: Lowest (applied after parallel and optional)

---

### Parallel Operator: `⇄`

**Syntax**: `ComponentA ⇄ ComponentB ⇄ ComponentC`

**Semantics**: Execute components concurrently, collect all results

**Example**:
```python
# Generated workflow code
async def pipeline():
    results = await asyncio.gather(
        ComponentA(),
        ComponentB(),
        ComponentC()
    )
    return results  # [result_a, result_b, result_c]
```

**Properties**:
- **Order**: Concurrent execution (no guaranteed order)
- **Data flow**: Components share same input, outputs collected as list
- **Error handling**: All must succeed unless `return_exceptions=True`
- **Precedence**: Higher than sequence (evaluated first)

---

### Optional Operator: `→?`

**Syntax**: `ComponentA →? ComponentB`

**Semantics**: Execute ComponentB only if ComponentA produces non-null result

**Example**:
```python
# Generated workflow code
async def pipeline():
    result_a = await ComponentA()
    if result_a is not None:
        result_b = await ComponentB(result_a)
        return result_b
    return None
```

**Properties**:
- **Condition**: Right side executes only if left returns non-null
- **Data flow**: Conditional passing
- **Error handling**: Left-side errors skip right side
- **Precedence**: Same as sequence

---

### Grouping: `()`

**Syntax**: `ComponentA → (ComponentB ⇄ ComponentC) → ComponentD`

**Semantics**: Override precedence, evaluate grouped expression first

**Example**:
```python
# Generated workflow code
async def pipeline():
    result_a = await ComponentA()
    
    # Parallel group
    results_bc = await asyncio.gather(
        ComponentB(result_a),
        ComponentC(result_a)
    )
    
    result_d = await ComponentD(results_bc)
    return result_d
```

**Properties**:
- **Precedence**: Highest (evaluated before operators)
- **Nesting**: Groups can contain other groups
- **Data flow**: Group result passed as single value

---

## Operator Precedence (Highest to Lowest)

1. `()` - Grouping
2. `⇄` - Parallel
3. `→` - Sequence
4. `→?` - Optional sequence

**Example**: `A → B ⇄ C → D` is interpreted as `A → (B ⇄ C) → D`

---

## Grammar Specification (EBNF)

```ebnf
pipeline     ::= expression
expression   ::= sequence
sequence     ::= optional (("→" | "→?") optional)*
optional     ::= parallel
parallel     ::= primary ("⇄" primary)*
primary      ::= component | "(" expression ")"
component    ::= identifier
identifier   ::= [A-Z][a-zA-Z0-9]*
```

---

## Generated Code Structure

### Pipeline Class Template

```python
"""
Generated pipeline: {pipeline_name}
Operator expression: {operator_expression}
"""
from restack_ai import workflow
from typing import Any, List, Optional
import asyncio

@workflow.defn()
class {PipelineName}Workflow:
    @workflow.run
    async def run(self, input_data: Any) -> Any:
        """
        Execute pipeline with operator composition.
        Expression: {operator_expression}
        """
        # Generated based on parsed operators
        {generated_execution_logic}
        
        return result
```

### Error Handling Configuration

Generated pipelines support error strategies:

```python
class ErrorHandlingStrategy(Enum):
    HALT = "halt"          # Stop on first error
    CONTINUE = "continue"  # Skip failed components, continue
    RETRY = "retry"        # Retry failed components with backoff

@workflow.defn()
class PipelineWorkflow:
    def __init__(self, error_strategy: ErrorHandlingStrategy = ErrorHandlingStrategy.HALT):
        self.error_strategy = error_strategy
```

---

## Validation Rules

Generated pipelines MUST validate:

1. **Acyclic Graph**: No component depends on itself (directly or transitively)
   ```python
   # ❌ INVALID - Cyclic
   A → B → A
   
   # ✅ VALID - Acyclic
   A → B → C
   ```

2. **Component Existence**: All referenced components must exist in project
   ```python
   # ❌ INVALID - UnknownComponent not defined
   A → UnknownComponent → B
   
   # ✅ VALID - All components defined
   A → B → C  # Where A, B, C exist as agents/workflows/functions
   ```

3. **Type Compatibility**: Output type of left must match input type of right (in sequence)
   ```python
   # ❌ INVALID - Type mismatch
   ComponentA() -> int
   ComponentB(input: str)  # Can't pass int to str
   
   # ✅ VALID - Types compatible
   ComponentA() -> str
   ComponentB(input: str)
   ```

4. **Parallel Input Compatibility**: All parallel components must accept same input type
   ```python
   # ❌ INVALID - Different input types in parallel
   ComponentA(input: str) ⇄ ComponentB(input: int)
   
   # ✅ VALID - Same input type
   ComponentA(input: str) ⇄ ComponentB(input: str)
   ```

---

## CLI Usage

### Generate Pipeline with Operators

```bash
# Basic pipeline generation
restack g pipeline DataProcessor --operators "Extract → Transform → Load"

# Complex pipeline with parallel and grouping
restack g pipeline Analysis --operators "Fetch → (ParseJSON ⇄ Validate) → Store"

# Optional execution
restack g pipeline SafeProcess --operators "Validate →? Process → Save"

# With error strategy
restack g pipeline ResilientPipe --operators "A → B → C" --error-strategy continue
```

### Operator Expression Validation

CLI MUST validate expression before generation:

```bash
$ restack g pipeline Test --operators "A → B → A"
❌ Error: Cyclic dependency detected: A → B → A

$ restack g pipeline Test --operators "A → UnknownComp"
❌ Error: Component 'UnknownComp' not found in project

$ restack g pipeline Test --operators "A → (B ⇄ C"
❌ Error: Unmatched parenthesis in operator expression
```

---

## Generated Test Structure

```python
"""
Test for {pipeline_name} pipeline
"""
import pytest
from workflows.{pipeline_module} import {PipelineName}Workflow

@pytest.mark.asyncio
async def test_pipeline_execution():
    """Test pipeline executes all components in correct order"""
    workflow = {PipelineName}Workflow()
    result = await workflow.run(test_input)
    
    # Verify execution order and results
    assert result is not None
    assert isinstance(result, expected_type)

@pytest.mark.asyncio
async def test_pipeline_error_handling():
    """Test pipeline handles component failures correctly"""
    workflow = {PipelineName}Workflow(error_strategy="halt")
    
    with pytest.raises(ComponentError):
        await workflow.run(invalid_input)
```

---

## Limitations & Future Enhancements

### Current Scope (Phase 1)

- ✅ Three operators: `→`, `⇄`, `→?`
- ✅ Grouping with parentheses
- ✅ Basic validation (cycles, existence, types)
- ✅ Error strategy configuration

### Future Enhancements (Not in Scope)

- ❌ Loop operators (e.g., `⊙` for iteration)
- ❌ Conditional branches (if/else)
- ❌ Merge operators (e.g., `⊗` for combining results)
- ❌ Timeout operators
- ❌ Retry operators (handled by component config instead)

---

## Acceptance Criteria

- [ ] Grammar formally defined in EBNF notation
- [ ] Operator precedence clearly specified
- [ ] Parser validates expressions before generation
- [ ] Generated code correctly implements operator semantics
- [ ] Cycle detection prevents invalid pipelines
- [ ] Type checking validates component compatibility
- [ ] Error strategies (halt/continue/retry) implemented
- [ ] Generated tests verify execution order
- [ ] CLI provides clear error messages for invalid expressions

---

## Implementation Notes

**Declarative Parser**: Research.md describes a declarative operator parser as an innovation. The CLI MUST implement:

1. **Tokenizer**: Break expression into tokens (`→`, `⇄`, `→?`, `(`, `)`, identifiers)
2. **Parser**: Build AST from tokens following precedence rules
3. **Validator**: Check cycles, component existence, type compatibility
4. **Code Generator**: Transform AST into executable workflow code

**Example AST**:
```python
# Expression: A → (B ⇄ C) → D
{
    "type": "sequence",
    "left": {"type": "component", "name": "A"},
    "right": {
        "type": "sequence",
        "left": {
            "type": "parallel",
            "components": [
                {"type": "component", "name": "B"},
                {"type": "component", "name": "C"}
            ]
        },
        "right": {"type": "component", "name": "D"}
    }
}
```

The generated workflow code executes this AST structure.
