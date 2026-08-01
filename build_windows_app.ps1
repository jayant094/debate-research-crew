$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

uv run --with pyinstaller pyinstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name DebateResearchCrew `
    --paths src `
    --collect-all crewai `
    --collect-all crewai_tools `
    src/debate_research_crew/desktop_app.py

Write-Host "Windows app created in dist\DebateResearchCrew"
