---
name: create-subagent
description: Create custom Claude Code subagents. Use when the user wants to create a subagent, make an agent, add a custom agent, or set up agent files.
---

# Creating Claude Code Subagents

## What is a Subagent?

A subagent is a specialized AI assistant that Claude Code can delegate tasks to. Each subagent has its own context, tools, and instructions, enabling focused task handling and better context management.

## File Locations

| Location | Scope | Priority |
|----------|-------|----------|
| `--agents` CLI flag | Current session | 1 (highest) |
| `.claude/agents/` | Current project | 2 |
| `~/.claude/agents/` | All projects | 3 |
| Plugin's `agents/` directory | Where plugin enabled | 4 (lowest) |

When multiple subagents share the same name, the higher-priority location wins.

## Instructions

1. Create the agents directory if it doesn't exist:
   ```bash
   mkdir -p .claude/agents
   ```

2. Create a markdown file for your subagent (e.g., `code-reviewer.md`)

3. Add YAML frontmatter at the very top (no blank lines before `---`)

4. Add the subagent's system prompt in markdown below the frontmatter

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | **Yes** | Unique identifier using lowercase letters and hyphens |
| `description` | **Yes** | When Claude should delegate to this subagent. Include "use proactively" for automatic invocation. |
| `tools` | No | Comma-separated list of allowed tools. Inherits all if omitted. |
| `disallowedTools` | No | Tools to deny, removed from inherited list |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit`. Defaults to `sonnet`. |
| `permissionMode` | No | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, or `plan` |
| `skills` | No | Skills to load into subagent context at startup |
| `hooks` | No | Lifecycle hooks scoped to this subagent |

### Available Tools

Subagents can use: `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, and MCP tools (MCP not available in background subagents).

### Permission Modes

| Mode | Behavior |
|------|----------|
| `default` | Standard permission checking with prompts |
| `acceptEdits` | Auto-accept file edits |
| `dontAsk` | Auto-deny permission prompts (allowed tools still work) |
| `bypassPermissions` | Skip all permission checks (use with caution) |
| `plan` | Plan mode (read-only exploration) |

---

## Example Subagents

### Read-Only Code Reviewer

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### Debugger (Can Fix Issues)

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### Database Query Validator (With Hooks)

```markdown
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.

When asked to analyze data:
1. Identify which tables contain the relevant data
2. Write efficient SELECT queries with appropriate filters
3. Present results clearly with context

You cannot modify data. If asked to INSERT, UPDATE, DELETE, or modify schema, explain that you only have read access.
```

---

## Invoking Subagents

### Automatic Delegation
Claude automatically delegates tasks based on the subagent's `description` field and current context. Include "use proactively" in the description for automatic invocation.

### Explicit Request
```
Use the code-reviewer agent to suggest improvements in this project
Have the debugger subagent look at my recent changes
```

### Foreground vs Background
- **Foreground**: Blocks main conversation until complete
- **Background**: Runs concurrently (auto-denies unavailable permissions)
- Press **Ctrl+B** to background a task
- Request with: "run this in the background"

### Resume Subagents
```
Continue that {subagent} analysis
```

---

## Key Limitations

1. **Subagents cannot spawn other subagents** - Chain them from the main conversation instead
2. **Subagents don't inherit skills** from parent conversation (use `skills` field explicitly)
3. **Background subagents** auto-deny unavailable permissions and can't ask clarifying questions
4. **MCP tools** unavailable in background subagents

---

## Disabling Specific Subagents

Add to your settings:
```json
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(my-custom-agent)"]
  }
}
```

---

## Management

- Use `/agents` slash command for interactive management
- Pass `--agents` CLI flag for session-specific subagents (JSON format)
- Check project-level subagents into version control for team collaboration

---

## Quick Reference

| Task | Action |
|------|--------|
| Create project subagent | Add `.md` file to `.claude/agents/` |
| Create global subagent | Add `.md` file to `~/.claude/agents/` |
| Read-only subagent | Set `tools: Read, Grep, Glob` |
| Deny specific tools | Use `disallowedTools` field |
| Use faster model | Set `model: haiku` |
| Load skills | Use `skills` field with skill names |
| Manage subagents | Run `/agents` command |
