[DEFAULT_SESSIONS_FOLDER]: [WORKSPACE_FOLDER]\Sessions
[SESSION_ARCHIVE_FOLDER]: [SESSION_FOLDER]\..\Archive

## .tools Folder Location

[TOOLS_FOLDER] = `[WORKSPACE_FOLDER]\..\.tools\`

**API keys file**: `[WORKSPACE_FOLDER]\..\.tools\.api-keys.txt` (in shared .tools folder)
Usage: `--keys-file [WORKSPACE_FOLDER]\..\.tools\.api-keys.txt`

## Prevention Rules (from session fails)

- **Model Accuracy**: Read model requests literally. Version numbers matter (e.g., Sonnet 4 != Sonnet 4.5).
- **Safety First**: UI automation scripts MUST have a `-DryRun` mode. Preview changes before sending irreversible keyboard events.
