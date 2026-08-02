# How to Run Debate Research (PF)

Public Forum only by default. Pipeline: **Researcher → Reviewer → PF Strategist** (TOC Round-of-8 depth).

There is **no hardcoded topic**. You must provide a resolution, or the CLI will ask for one.

## Prerequisites

- Python 3.10–3.13
- Dependencies installed: `uv sync`
- `.env` in the project root with:
  - `OPENAI_API_KEY`
  - `SERPER_API_KEY`

## Interactive topic (recommended)

```bash
uv run kickoff
```

You will be prompted:

```text
Enter the debate resolution / topic:
>
```

Paste or type your resolution, then press Enter.

## Topic via CLI argument

Pass a JSON payload with a `topic` field. If `topic` is missing or empty, you will still be prompted.

### PowerShell

```powershell
uv run run_with_trigger '{\"topic\": \"Resolved: Your resolution here.\"}'
```

### Bash / macOS / Linux

```bash
uv run run_with_trigger '{"topic": "Resolved: Your resolution here."}'
```

### Equivalent module form

```powershell
uv run python -m debate_research_crew.main '{\"topic\": \"Resolved: Your resolution here.\"}'
```

## Desktop app

```bash
uv run debate-research-app
```

1. Enter your resolution in the text box (required).
2. Click **Research this resolution**.
3. When finished, the PF brief appears in the window and is saved under `output/`.

## Outputs

After a successful run:

| File | Contents |
|------|----------|
| `output/research_report.md` | Raw evidence file from the researcher |
| `output/validated_research.md` | Citation-audited evidence from the reviewer |
| `output/pf_debate_brief.md` | TOC Round-of-8 Public Forum brief |

## Notes

- Runs can take a long time at max depth (many searches, document reads, and a long PF brief).
- On lower OpenAI TPM tiers you may hit rate limits; wait a minute and retry, or reduce batching in the research crew if needed.
- LD format is not run by default; only PF is produced.
