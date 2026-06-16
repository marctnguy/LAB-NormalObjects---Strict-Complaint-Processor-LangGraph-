from typing import TypedDict, Literal
import os
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0,
)


ComplaintCategory = Literal["portal", "monster", "psychic", "environmental", "other"]
WorkflowStatus = Literal[
    "intake",
    "validate",
    "investigate",
    "resolve",
    "close",
    "needs_clarification",
    "rejected",
    "escalated",
    "completed",
]


class ComplaintStateBase(TypedDict):
    complaint: str


class ComplaintState(ComplaintStateBase, total=False):
    category: ComplaintCategory
    status: WorkflowStatus
    workflow_path: list[str]

    needs_clarification: bool
    validation_passed: bool
    duplicate_of: str
    investigation_notes: list[str]

    resolution: str
    effectiveness: Literal["high", "medium", "low"]
    closed: bool
    outcome: str
    timestamp: str


from datetime import datetime
from langchain_core.messages import HumanMessage


def intake_node(state: ComplaintState) -> ComplaintState:
    """Step 1: Intake - Parse and categorize the complaint"""
    print("\n[INTAKE] Processing complaint...")

    complaint = state["complaint"]

    categorization_prompt = f"""Categorize this Downside Up complaint into one of these categories:
- portal: Issues with portal timing, location, or behavior
- monster: Issues with creature behavior (demogorgons, etc.)
- psychic: Issues with psychic abilities or limitations
- environmental: Issues with electricity, weather, or physical environment
- other: Anything else

Complaint: {complaint}

Respond with ONLY the category name (portal, monster, psychic, environmental, or other)."""

    response = llm.invoke([HumanMessage(content=categorization_prompt)])
    category = response.content.strip().lower()

    if category not in {"portal", "monster", "psychic", "environmental", "other"}:
        category = "other"

    new_state = {
        **state,
        "category": category,
        "workflow_path": state.get("workflow_path", []) + ["intake"],
        "status": "intake",
    }

    print(f"[INTAKE] Categorized as: {category}")
    return new_state


def validate_node(state: ComplaintState) -> ComplaintState:
    """Step 2: Validate - Check complaint against category rules"""
    print("\n[VALIDATE] Validating complaint...")

    complaint = state["complaint"].lower()
    category = state.get("category", "other")

    validation_passed = False
    needs_clarification = False
    status = "validate"

    if category == "portal":
        validation_passed = any(
            word in complaint for word in ["portal", "time", "timing", "location", "place", "shift", "delay"]
        )
        if not validation_passed:
            status = "rejected"

    elif category == "monster":
        validation_passed = any(
            word in complaint for word in ["demogorgon", "creature", "monster", "beast", "fight", "attack", "behavior"]
        )
        if not validation_passed:
            status = "rejected"

    elif category == "psychic":
        validation_passed = any(
            word in complaint for word in ["psychic", "power", "ability", "mind", "telekinesis", "lift", "cannot", "can't"]
        )
        if not validation_passed:
            status = "rejected"

    elif category == "environmental":
        validation_passed = any(
            word in complaint for word in ["electric", "weather", "storm", "rain", "temperature", "power line", "power"]
        )
        if not validation_passed:
            status = "rejected"

    else:
        # Other category is escalated for manual review if there is at least some complaint-like content
        if len(complaint.strip()) > 10:
            status = "escalated"
            validation_passed = True
        else:
            status = "needs_clarification"
            needs_clarification = True

    # If the complaint is very short or basically empty, ask for clarification
    if len(complaint.strip()) < 15:
        validation_passed = False
        needs_clarification = True
        status = "needs_clarification"

    if validation_passed and status == "validate":
        status = "validate"
        print("[VALIDATE] Complaint passed validation.")
    elif status == "escalated":
        print("[VALIDATE] Category is other: escalating for manual review.")
    elif status == "needs_clarification":
        print("[VALIDATE] Complaint is too vague: needs clarification.")
    else:
        print("[VALIDATE] Complaint failed validation: reject and request clarification.")

    new_state = {
        **state,
        "validation_passed": validation_passed,
        "needs_clarification": needs_clarification,
        "workflow_path": state.get("workflow_path", []) + ["validate"],
        "status": status,
    }

    return new_state


def investigate_node(state: ComplaintState) -> ComplaintState:
    """Step 3: Investigate - Gather documented evidence"""
    print("\n[INVESTIGATE] Gathering evidence...")

    category = state.get("category", "other")
    complaint = state["complaint"]

    evidence_map = {
        "portal": [
            "Checked temporal consistency across reported portal events.",
            "Reviewed location anomalies and shift patterns.",
            "Logged environmental interference around portal activation.",
        ],
        "monster": [
            "Collected behavioral observations for creature interactions.",
            "Checked for aggression patterns and repeat encounters.",
            "Recorded environmental triggers associated with sightings.",
        ],
        "psychic": [
            "Reviewed ability limitations and failure points.",
            "Compared reported power usage against contextual stress factors.",
            "Logged observed malfunctions and inconsistencies.",
        ],
        "environmental": [
            "Analyzed electrical activity and anomaly reports.",
            "Checked atmospheric conditions and physical disturbances.",
            "Recorded correlation between weather and complaint timing.",
        ],
    }

    investigation_notes = evidence_map.get(category, ["Manual investigation required."])

    new_state = {
        **state,
        "investigation_notes": investigation_notes,
        "workflow_path": state.get("workflow_path", []) + ["investigate"],
        "status": "investigate",
    }

    print(f"[INVESTIGATE] Evidence documented for category: {category}")
    return new_state


def resolve_node(state: ComplaintState) -> ComplaintState:
    """Step 4: Resolve - Apply category-specific resolution"""
    print("\n[RESOLVE] Applying resolution...")

    category = state.get("category", "other")
    complaint = state["complaint"].lower()
    investigation_notes = state.get("investigation_notes", [])

    resolution_map = {
        "portal": "Applied portal timing stabilization protocol.",
        "monster": "Escalated to creature containment team and applied behavioral tracking protocol.",
        "psychic": "Adjusted psychic support protocol and logged ability limitation review.",
        "environmental": "Activated environmental anomaly response procedure and notified maintenance team.",
        "other": "Escalated to manual review under Downside Up Protocol X-0.",
    }

    def score_portal() -> str:
        signals = [
            any(word in complaint for word in ["portal", "timing", "time", "location", "shift", "delay"]),
            any(word in complaint for word in ["where", "when", "place", "pattern"]),
            len(investigation_notes) >= 3,
        ]
        score = sum(signals)
        if score == 3:
            return "high"
        if score == 2:
            return "medium"
        return "low"

    def score_monster() -> str:
        signals = [
            any(word in complaint for word in ["monster", "demogorgon", "creature", "beast"]),
            any(word in complaint for word in ["attack", "behavior", "interact", "aggressive", "pattern"]),
            len(investigation_notes) >= 3,
        ]
        score = sum(signals)
        if score == 3:
            return "medium"
        if score == 2:
            return "medium"
        return "low"

    def score_psychic() -> str:
        signals = [
            any(word in complaint for word in ["psychic", "power", "ability", "mind", "telekinesis", "lift"]),
            any(word in complaint for word in ["limit", "cannot", "can't", "fail", "malfunction", "stress"]),
            len(investigation_notes) >= 3,
        ]
        score = sum(signals)
        if score == 3:
            return "high"
        if score == 2:
            return "medium"
        return "low"

    def score_environmental() -> str:
        signals = [
            any(word in complaint for word in ["electric", "weather", "storm", "rain", "temperature", "power"]),
            any(word in complaint for word in ["line", "field", "anomaly", "disturbance", "atmospheric"]),
            len(investigation_notes) >= 3,
        ]
        score = sum(signals)
        if score == 3:
            return "high"
        if score == 2:
            return "medium"
        return "low"

    if category == "portal":
        effectiveness = score_portal()
    elif category == "monster":
        effectiveness = score_monster()
    elif category == "psychic":
        effectiveness = score_psychic()
    elif category == "environmental":
        effectiveness = score_environmental()
    else:
        effectiveness = "low"

    resolution = resolution_map.get(category, "Manual review required.")

    new_state = {
        **state,
        "resolution": resolution,
        "effectiveness": effectiveness,
        "workflow_path": state.get("workflow_path", []) + ["resolve"],
        "status": "resolve",
    }

    print(f"[RESOLVE] Resolution set: {resolution}")
    print(f"[RESOLVE] Effectiveness rating: {effectiveness}")
    return new_state


def close_node(state: ComplaintState) -> ComplaintState:
    """Step 5: Close - Confirm completion and log outcome"""
    print("\n[CLOSE] Finalizing complaint...")

    timestamp = datetime.now(timezone.utc).isoformat()

    outcome = (
        "Closed after resolution was applied and satisfaction verification was attempted."
    )

    if state.get("effectiveness") == "low":
        outcome += " Follow-up checkpoint required in 30 days."

    new_state = {
        **state,
        "closed": True,
        "outcome": outcome,
        "timestamp": timestamp,
        "workflow_path": state.get("workflow_path", []) + ["close"],
        "status": "completed",
    }

    print(f"[CLOSE] Complaint closed at {timestamp}")
    return new_state


from langgraph.graph import StateGraph, END


def route_after_validate(state: ComplaintState) -> str:
    """Route based on validation outcome."""
    if state.get("needs_clarification"):
        return "end"
    if state.get("status") in {"rejected", "escalated"}:
        return "end"
    if state.get("validation_passed"):
        return "investigate"
    return "end"


workflow = StateGraph(ComplaintState)

# Add nodes
workflow.add_node("intake", intake_node)
workflow.add_node("validate", validate_node)
workflow.add_node("investigate", investigate_node)
workflow.add_node("resolve", resolve_node)
workflow.add_node("close", close_node)

# Entry point
workflow.set_entry_point("intake")

# Linear flow up to validation
workflow.add_edge("intake", "validate")

# Conditional routing after validation
workflow.add_conditional_edges(
    "validate",
    route_after_validate,
    {
        "investigate": "investigate",
        "end": END,
    },
)

# Linear flow for successful complaints
workflow.add_edge("investigate", "resolve")
workflow.add_edge("resolve", "close")
workflow.add_edge("close", END)

# Compile the graph
app = workflow.compile()

def visualize_workflow_path(final_state: ComplaintState) -> None:
    """Print the path taken through the workflow with final status."""
    path = final_state.get("workflow_path", [])
    status = final_state.get("status", "unknown")

    print("\nWorkflow visualization:")
    print(" -> ".join(path) if path else "[no workflow path recorded]")
    print(f"Final status: {status}")


test_complaints = [
    "The Downside Up portal opens at different times each day. How do I predict when?",
    "Demogorgons sometimes work together and sometimes fight. What's their deal?",
    "El can move things with her mind but can't lift heavy rocks. Why?",
    "Why do creatures and power lines react so strangely together?",
    "This is not a valid complaint about something random",
]

print("\nTesting workflow with sample complaints...\n")

for i, complaint in enumerate(test_complaints, 1):
    print(f"\n{'=' * 60}")
    print(f"TEST {i}")
    print(f"Complaint: {complaint}")

    initial_state: ComplaintState = {
        "complaint": complaint,
        "workflow_path": [],
        "status": "start",
    }

    final_state = app.invoke(initial_state)
    visualize_workflow_path(final_state)

    print("\nFinal state:")
    print(f"Category: {final_state.get('category')}")
    print(f"Status: {final_state.get('status')}")
    print(f"Workflow path: {final_state.get('workflow_path')}")
    print(f"Validation passed: {final_state.get('validation_passed')}")
    print(f"Needs clarification: {final_state.get('needs_clarification')}")
    print(f"Resolution: {final_state.get('resolution')}")
    print(f"Effectiveness: {final_state.get('effectiveness')}")
    print(f"Outcome: {final_state.get('outcome')}")
