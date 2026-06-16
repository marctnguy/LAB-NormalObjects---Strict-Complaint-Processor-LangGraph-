# NormalObjects - Strict Complaint Processor (LangGraph)

This lab focused on building a structured complaint-processing workflow for Bloyce's Protocol using LangGraph. The goal was to move from a freeform agent approach to a rule-based state machine that follows a strict sequence: intake, validate, investigate, resolve, and close. I implemented a typed state object, workflow nodes, conditional routing, and a workflow path tracker so each complaint can be traced step by step. I also tested the graph with valid and invalid complaints to confirm that the workflow behaves consistently and records the final outcome.

## Step 6: LangGraph vs LangChain

LangGraph is a better fit for this complaint processor because the workflow must follow a strict sequence of steps, keep state, and produce traceable outputs for auditing. LangChain is better when the task is more open-ended and benefits from flexible reasoning or creative responses, such as brainstorming or freeform assistance. The trade-off is that LangGraph gives more control, predictability, and visibility into each step, while LangChain is faster to prototype and more adaptable but less structured.