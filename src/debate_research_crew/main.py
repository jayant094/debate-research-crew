#!/usr/bin/env python
import json
import sys

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from debate_research_crew.crews.pf_crew.pf_crew import kickoff_pf_crew
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
    pf_brief: str = ""


class DebateResearchFlow(Flow[DebateFlowState]):
    @start()
    def set_topic(self, crewai_trigger_payload: dict | None = None):
        if crewai_trigger_payload:
            self.state.topic = crewai_trigger_payload.get("topic", DEFAULT_TOPIC)
        else:
            self.state.topic = DEFAULT_TOPIC
        print(f"Debate topic: {self.state.topic}")
        print("Format: Public Forum (PF) only — TOC Round-of-8 max depth")

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
    def run_pf(self):
        print("Running PF Debate agent...")
        result = kickoff_pf_crew(
            inputs={
                "topic": self.state.topic,
                "validated_research": self.state.validated_research,
            }
        )
        self.state.pf_brief = result.raw
        print("PF brief complete: output/pf_debate_brief.md")

    @listen(run_pf)
    def finalize(self):
        print("\nAll PF debate research outputs saved:")
        print("  - output/research_report.md")
        print("  - output/validated_research.md")
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
    if len(sys.argv) > 1:
        run_with_trigger()
    else:
        kickoff()
