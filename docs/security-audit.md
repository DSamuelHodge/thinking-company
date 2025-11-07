# Security Audit Notes (Placeholder)

Scope: File operations, template rendering, CLI inputs.

Checklist:
- [ ] Validate all user inputs (names, paths) with strict regex/keyword checks
- [ ] Avoid code execution during template rendering
- [ ] Handle file permissions and symlinks safely
- [ ] Do not log secrets; redact sensitive values in structured logs
- [ ] Pin critical dependencies; review for known vulnerabilities
