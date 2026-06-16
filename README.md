# NormalObjects - Strict Complaint Processor (LangGraph)

This project implements a structured complaint-processing workflow for Bloyce's Protocol using LangGraph. The workflow follows a strict sequence: intake, validate, investigate, resolve, and close. It also tracks the path taken through the graph so each complaint can be traced step by step.

## How to Run

1. Make sure your `.env` file includes a valid `OPENAI_API_KEY`.
2. Run the script:

    python3 normalobjects_langgraph.py

If your environment uses `python` instead of `python3`, you can use:

    python normalobjects_langgraph.py

## Files

- `normalobjects_langgraph.py`: Main LangGraph implementation, workflow nodes, graph wiring, and sample tests.
- `lab_summary.md`: Short lab recap and the Step 6 comparison between LangGraph and LangChain.
- `.env`: Environment variables, including the OpenAI API key.
- `.gitignore`: Files and folders excluded from version control.

## Notes

The script includes built-in test complaints that demonstrate both valid and invalid workflow paths. Running the file will print the full processing trace and final state for each complaint.