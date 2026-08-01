from pathlib import Path

from crewai.project import load_crew
from crewai_tools import SerperDevTool

from debate_research_crew.tools.source_reader import SourceReaderTool


def _load():
    return load_crew(Path(__file__).with_name("crew.jsonc"))


def _max_research_tools(crew) -> None:
    """Use full Serper result depth for TOC-caliber source discovery."""
    tools = [SerperDevTool(n_results=10), SourceReaderTool()]
    for agent in crew.agents:
        agent.tools = tools


def kickoff_research_crew(inputs: dict):
    crew, default_inputs = _load()
    _max_research_tools(crew)
    return crew.kickoff(inputs={**default_inputs, **inputs})


async def kickoff_research_crew_async(inputs: dict):
    crew, default_inputs = _load()
    _max_research_tools(crew)
    return await crew.kickoff_async(inputs={**default_inputs, **inputs})
