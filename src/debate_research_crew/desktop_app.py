"""Windows desktop interface for the Debate Research Crew."""

from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from debate_research_crew.main import DebateResearchFlow


def application_root() -> Path:
    """Use the project directory in development or the app directory when packaged."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


class DebateResearchApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.project_root = application_root()
        self.output_path = self.project_root / "output" / "pf_debate_brief.md"

        self.title("Debate Research Crew")
        self.minsize(860, 660)
        self.geometry("1000x760")

        self.status = tk.StringVar(
            value="Ready. Enter a resolution and select Research."
        )
        self._build_interface()

    def _build_interface(self) -> None:
        container = ttk.Frame(self, padding=18)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Debate Research Crew",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor=tk.W)
        ttk.Label(
            container,
            text=(
                "PF-only TOC Round-of-8 pipeline: research trusted sources, review "
                "citations, then produce a full Public Forum brief."
            ),
            wraplength=900,
        ).pack(anchor=tk.W, pady=(2, 16))

        ttk.Label(container, text="Resolution or topic").pack(anchor=tk.W)
        self.topic_input = scrolledtext.ScrolledText(
            container, height=4, wrap=tk.WORD, font=("Segoe UI", 11)
        )
        self.topic_input.pack(fill=tk.X, pady=(5, 12))
        self.topic_input.insert(
            "1.0", "Resolved: Enter your debate resolution here."
        )
        self.topic_input.bind("<FocusIn>", self._clear_topic_placeholder, add="+")

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(0, 12))
        self.run_button = ttk.Button(
            actions, text="Research this resolution", command=self.start_research
        )
        self.run_button.pack(side=tk.LEFT)
        ttk.Button(actions, text="Save report as…", command=self.save_report).pack(
            side=tk.LEFT, padx=8
        )
        ttk.Button(
            actions, text="Open output folder", command=self.open_output_folder
        ).pack(side=tk.LEFT)

        ttk.Label(
            container, textvariable=self.status, foreground="#1f5f8b", wraplength=900
        ).pack(anchor=tk.W, pady=(0, 8))

        self.report = scrolledtext.ScrolledText(
            container, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10)
        )
        self.report.pack(fill=tk.BOTH, expand=True)
        self._set_report(
            "Your completed evidence briefing will appear here.\n\n"
            "Required configuration:\n"
            "• OPENAI_API_KEY\n"
            "• SERPER_API_KEY\n\n"
            "Put both values in a .env file beside this app before starting research."
        )

    def _clear_topic_placeholder(self, _event=None) -> None:
        current = self.topic_input.get("1.0", tk.END).strip()
        if current == "Resolved: Enter your debate resolution here.":
            self.topic_input.delete("1.0", tk.END)

    def start_research(self) -> None:
        topic = self.topic_input.get("1.0", tk.END).strip()
        if (
            not topic
            or topic == "Resolved: Enter your debate resolution here."
        ):
            messagebox.showerror(
                "Resolution required", "Enter a debate resolution first."
            )
            self.topic_input.focus_set()
            return

        self.run_button.configure(state=tk.DISABLED)
        self.status.set(
            "Research in progress. This can take several minutes while sources are "
            "searched, reviewed, and presented."
        )
        self._set_report("Working…\n\nResearcher → Reviewer → PF Strategist")
        threading.Thread(target=self._run_flow, args=(topic,), daemon=True).start()

    def _run_flow(self, topic: str) -> None:
        try:
            os.chdir(self.project_root)
            DebateResearchFlow().kickoff(
                {"crewai_trigger_payload": {"topic": topic}}
            )
            report = self.output_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.after(0, self._show_failure, str(exc))
            return

        self.after(0, self._show_success, report)

    def _show_success(self, report: str) -> None:
        self._set_report(report)
        self.status.set(f"Complete. Saved to {self.output_path}")
        self.run_button.configure(state=tk.NORMAL)

    def _show_failure(self, error: str) -> None:
        self._set_report(
            "Research could not be completed.\n\n"
            f"{error}\n\n"
            "Confirm OPENAI_API_KEY and SERPER_API_KEY are set in .env, then try again."
        )
        self.status.set("Research failed. Review the message above and try again.")
        self.run_button.configure(state=tk.NORMAL)

    def _set_report(self, content: str) -> None:
        self.report.configure(state=tk.NORMAL)
        self.report.delete("1.0", tk.END)
        self.report.insert("1.0", content)
        self.report.configure(state=tk.DISABLED)

    def save_report(self) -> None:
        content = self.report.get("1.0", tk.END).strip()
        if not content or content.startswith("Your completed evidence briefing"):
            messagebox.showinfo("No report yet", "Run research before saving a report.")
            return

        destination = filedialog.asksaveasfilename(
            title="Save debate research briefing",
            defaultextension=".md",
            initialfile="pf_debate_brief.md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All files", "*.*")],
        )
        if destination:
            Path(destination).write_text(content + "\n", encoding="utf-8")
            self.status.set(f"Report saved to {destination}")

    def open_output_folder(self) -> None:
        output_folder = self.output_path.parent
        output_folder.mkdir(parents=True, exist_ok=True)
        if hasattr(os, "startfile"):
            os.startfile(output_folder)  # type: ignore[attr-defined]
        else:
            messagebox.showinfo("Output folder", str(output_folder))


def main() -> None:
    app = DebateResearchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
