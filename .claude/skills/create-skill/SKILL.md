---
name: create-skill
description: Create a new Claude Code skill. Use when the user wants to create a skill, make a skill, add a custom skill, or set up skill files.
---

# Creating Claude Code Skills

## What is a Skill?

A skill is a markdown file that gives Claude specialized instructions for specific tasks. Skills are loaded automatically based on context.

## File Locations

| Location | Scope |
|----------|-------|
| `.claude/skills/` | Project-specific (shared via git) |
| `~/.claude/skills/` | Personal (all projects) |

## Instructions

1. Create a skill directory:
   ```bash
   mkdir -p .claude/skills/your-skill-name
   ```

2. Create a `SKILL.md` file inside the directory (filename is case-sensitive)

3. Add YAML frontmatter at the very top (no blank lines before `---`):
   ```yaml
   ---
   name: your-skill-name
   description: Brief description of what this skill does and when to use it.
   ---
   ```

4. Add the skill body in markdown below the frontmatter

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Identifier used to invoke the skill |
| `description` | Yes | Tells Claude when to use this skill |
| `allowed-tools` | No | Restricts which tools Claude can use |
| `globs` | No | File patterns the skill applies to |

## Skill Body Structure

```markdown
# Skill Title

## Instructions
Step-by-step guidance for Claude.

## Examples
Concrete input-output examples.

## Guidelines
Rules and constraints.
```

## Example Skill

```markdown
---
name: commit-message
description: Generate commit messages from staged changes. Use when writing commits.
---

# Commit Message Generator

## Instructions
1. Run `git diff --staged` to see changes
2. Write a commit message with:
   - Summary under 50 characters
   - Detailed description if needed
   - List affected components

## Guidelines
- Use imperative mood ("Add feature" not "Added feature")
- Focus on why, not what
```

## Restricting Tools

To create a read-only skill:
```yaml
---
name: code-explorer
description: Explore code without modifications.
allowed-tools: Read, Grep, Glob
---
```

## Tips

- Write clear, scannable instructions
- Put trigger conditions in the `description` field
- Use spaces (not tabs) in frontmatter
- Avoid multiline descriptions
- Changes take effect immediately (no restart needed)
- Use `claude --debug` to troubleshoot loading issues

## Directory Structure

A skill can include multiple files:
```
skills/
└── my-skill/
    ├── SKILL.md           # Required
    ├── scripts/           # Optional executables
    ├── references/        # Optional docs
    └── examples/          # Optional templates
```
