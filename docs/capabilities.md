# Capabilities and linting

SSMD exposes capability profiles so downstream tools can validate input against what a
target engine supports.

## Profiles

- `ssmd-core`: portable SSMD subset.
- `kokoro`: same as core, but excludes extensions.
- `google-ssml`: core SSMD with Google SSML mapping.

Use `list_profiles()` to enumerate and `get_profile()` for details.

## Linting

Use `lint(text, profile="ssmd-core")` to get structured warnings/errors:

```python
import ssmd

issues = ssmd.lint("[Hello]{ext='whisper'}", profile="kokoro")
for issue in issues:
    print(issue.severity, issue.message)
```
