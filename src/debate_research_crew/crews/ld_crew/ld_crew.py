from pathlib import Path

from crewai.project import load_crew


def _load():
    return load_crew(Path(__file__).with_name("crew.jsonc"))


def kickoff_ld_crew(inputs: dict):
    crew, default_inputs = _load()
    return crew.kickoff(inputs={**default_inputs, **inputs})


async def kickoff_ld_crew_async(inputs: dict):
    crew, default_inputs = _load()
    return await crew.kickoff_async(inputs={**default_inputs, **inputs})
