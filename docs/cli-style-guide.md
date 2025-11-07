# CLI Emoji and Color Style Guide

## Standard Emoji Usage

The Restack Gen CLI uses a consistent emoji palette for user feedback:

### Status Indicators
- ✅ **Success** - Operation completed successfully (green text)
- ❌ **Error** - Operation failed (red text, stderr)
- ⚠️ **Warning** - Operation completed with warnings (yellow text)
- ℹ️ **Info** - Informational message (default text)

### Action Indicators
- ✨ **Generated** - Component/file created successfully (green text)
- 📄 **File** - File path or file-related info
- 💡 **Suggestion** - Helpful tip or recommendation
- 🔄 **Processing** - Operation in progress
- 🚀 **Launch** - Server or service starting

### Component Icons
- 🤖 **Agent** - AI agent component
- 🔄 **Workflow** - Workflow component
- ⚙️ **Function** - Function component
- 🔌 **LLM** - LLM integration
- 📦 **Pipeline** - Data pipeline

## Color Usage

### Click Color Codes
- `fg="green"` - Success messages, completion
- `fg="red"` - Errors, failures
- `fg="yellow"` - Warnings, cautions
- `fg="blue"` - Info, neutral messages
- `fg="cyan"` - Highlighted text, paths

### Usage Guidelines
1. **Always use stderr for errors**: `err=True` with red text
2. **Success messages**: Green text for positive outcomes
3. **Warnings**: Yellow text for non-critical issues
4. **Info**: Default or blue text for neutral information

## Examples

### Success Message
```python
click.secho(f"✅ Generated agent: {name}", fg="green")
```

### Error with Suggestion
```python
click.secho("❌ Error: File already exists", fg="red", err=True)
click.echo("")
click.echo("💡 Try one of these options:")
click.echo("   • Use --force to overwrite")
```

### Info Message
```python
click.echo("ℹ️  No pending migrations")
```

### Warning
```python
click.secho("⚠️ SDK version below recommended minimum", fg="yellow")
```

## Consistency Checklist

- [ ] All success messages use ✅ with green text
- [ ] All errors use ❌ with red text and stderr
- [ ] All warnings use ⚠️ with yellow text
- [ ] Info messages use ℹ️
- [ ] Suggestions use 💡
- [ ] Generated output uses ✨ with green text
- [ ] File paths use 📄 prefix
