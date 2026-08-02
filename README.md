# Debate Research Crew

A CrewAI Flow project with three specialized agents that research, independently review, and clearly present evidence for a debate resolution.

## Agents

| Agent | Role |
|---|---|
| **Researcher** | Finds and analyzes evidence from trusted publications, primary data, and reputable organizations using Serper web search |
| **Reviewer** | Checks the research, evaluates reliability and substantiated bias/limitations, and identifies the side of the resolution the evidence supports |
| **Presenter** | Delivers direct links, summaries, statistics and percentages, bias/limitations, reliability, and resolution support in one readable brief |

## Workflow

```
Topic → Researcher → Reviewer → Presenter
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
uv run kickoff
```

You will be prompted for a debate resolution. To pass one directly:

```bash
uv run run_with_trigger '{"topic": "Resolved: ..."}'
```

See [HOW_TO_RUN.md](HOW_TO_RUN.md) for PowerShell examples and the desktop app.

## Desktop app (Windows)

After setup, double-click `run_desktop_app.bat`, or run:

```powershell
uv run debate-research-app
```

The desktop interface lets you enter a resolution, start the crew, read the completed briefing, save a copy, and open its output folder.

### Build a shareable Windows app

On a Windows machine with Python and `uv` installed, run:

```powershell
.\build_windows_app.ps1
```

The distributable app is created in `dist\DebateResearchCrew`. Place a `.env` file containing `OPENAI_API_KEY` and `SERPER_API_KEY` beside `DebateResearchCrew.exe` before running it. The app requires internet access to research sources and use the configured LLM.

## Outputs

| File | Description |
|---|---|
| `output/research_report.md` | Raw sourced research |
| `output/validated_research.md` | Fact-checked evidence bank with reliability, bias/limitations, and resolution-support assessments |
| `output/debate_research_brief.md` | Final source cards with links, summaries, statistics, impact, and supported side |

## Trigger payload (optional)

Or use the `run_with_trigger` script entry point with a JSON payload containing `"topic"`.
