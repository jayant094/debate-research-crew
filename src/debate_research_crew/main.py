#!/usr/bin/env python
import asyncio
import json
import sys

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from debate_research_crew.crews.ld_crew.ld_crew import kickoff_ld_crew_async
from debate_research_crew.crews.pf_crew.pf_crew import kickoff_pf_crew_async
from debate_research_crew.crews.research_crew.research_crew import kickoff_research_crew
from debate_research_crew.crews.review_crew.review_crew import kickoff_review_crew

DEFAULT_TOPIC = (
    "Resolved: The United States federal government should substantially increase "
    "its protection of water resources in the United States."
)


class DebateFlowState(BaseModel):
    topic: str = ""
    research_report: str = ""
    validated_research: str = ""
    ld_brief: str = ""
    pf_brief: str = ""


class DebateResearchFlow(Flow[DebateFlowState]):
    @start()
    def set_topic(self, crewai_trigger_payload: dict | None = None):
        if crewai_trigger_payload:
            self.state.topic = crewai_trigger_payload.get("topic", DEFAULT_TOPIC)
        else:
            self.state.topic = DEFAULT_TOPIC
        print(f"Debate topic: {self.state.topic}")

    @listen(set_topic)
    def run_research(self):
        print("Running Researcher agent...")
        result = kickoff_research_crew(inputs={"topic": self.state.topic})
        self.state.research_report = result.raw
        print("Research complete: output/research_report.md")

    @listen(run_research)
    def run_review(self):
        print("Running Reviewer agent...")
        result = kickoff_review_crew(
            inputs={
                "topic": self.state.topic,
                "research": self.state.research_report,
            }
        )
        self.state.validated_research = result.raw
        print("Review complete: output/validated_research.md")

    @listen(run_review)
    def run_debate_briefs(self):
        print("Running Debate_LD and Debate_PF agents in parallel...")

        async def _run_parallel():
            return await asyncio.gather(
                kickoff_ld_crew_async(
                    inputs={
                        "topic": self.state.topic,
                        "validated_research": self.state.validated_research,
                    }
                ),
                kickoff_pf_crew_async(
                    inputs={
                        "topic": self.state.topic,
                        "validated_research": self.state.validated_research,
                    }
                ),
            )

        ld_result, pf_result = asyncio.run(_run_parallel())
        self.state.ld_brief = ld_result.raw
        self.state.pf_brief = pf_result.raw
        print("LD brief complete: output/ld_debate_brief.md")
        print("PF brief complete: output/pf_debate_brief.md")

    @listen(run_debate_briefs)
    def finalize(self):
        print("\nAll debate research outputs saved:")
        print("  - output/research_report.md")
        print("  - output/validated_research.md")
        print("  - output/ld_debate_brief.md")
        print("  - output/pf_debate_brief.md")


def kickoff():
    DebateResearchFlow().kickoff()


def plot():
    DebateResearchFlow().plot()


def run_with_trigger():
    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise Exception("Invalid JSON payload provided as argument") from exc

    try:
        return DebateResearchFlow().kickoff(
            {"crewai_trigger_payload": trigger_payload}
        )
    except Exception as exc:
        raise Exception(
            f"An error occurred while running the flow with trigger: {exc}"
        ) from exc


if __name__ == "__main__":
    kickoff()
