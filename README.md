# Debate Research Crew

A CrewAI Flow project with four specialized agents that research a debate topic and produce tournament-ready LD and PF briefs.

## Agents

| Agent | Role |
|---|---|
| **Researcher** | Researches topics using trusted publications and organizations (Serper web search) |
| **Reviewer** | Validates research and organizes a debate-ready evidence bank |
| **Debate_LD** | Builds Aff + Neg Lincoln-Douglas cases |
| **Debate_PF** | Builds Pro + Con Public Forum cases |

## Workflow

```
Topic → Researcher → Reviewer → (Debate_LD + Debate_PF in parallel)
```

## Setup

1. Install [Python 3.10–3.13](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/)
2. Install the CrewAI CLI: `uv tool install crewai`
3. Copy `.env` and add your API keys:
   - `OPENAI_API_KEY` — [OpenAI](https://platform.openai.com/)
   - `SERPER_API_KEY` — [Serper.dev](https://serper.dev/) (free tier available)
4. Install dependencies: `crewai install`

## Run

```bash
crewai run
```

When prompted, enter a debate topic/resolution. Default topic is a sample water-resources LD resolution.

## Outputs

| File | Description |
|---|---|
| `output/research_report.md` | Raw sourced research |
| `output/validated_research.md` | Fact-checked evidence bank |
| `output/ld_debate_brief.md` | LD Aff + Neg cases |
| `output/pf_debate_brief.md` | PF Pro + Con cases |

## Trigger payload (optional)

```bash
python -m debate_research_crew.main '{"topic": "Resolved: ..."}'
```

Or use the `run_with_trigger` script entry point with a JSON payload containing `"topic"`.
