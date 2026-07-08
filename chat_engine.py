"""
Chat engine for Viably — context-aware response generation.
Pure functions, no Streamlit dependency. Testable in isolation.
"""
from typing import Any


def generate_response(user_msg: str, context: dict) -> str:
    """Generate a context-aware response from the assessment data.

    Template-based for demo reliability. Replace with an LLM call
    (OpenAI, DeepSeek, etc.) for richer responses.
    """
    if not context:
        return (
            "I don't have any assessment results to discuss yet. "
            "Run an assessment first, then ask me about the findings!"
        )

    msg_lower = user_msg.lower()
    rec = context["recommendation"]
    counts = context["counts"]

    # Pattern-match common question types
    if any(w in msg_lower for w in ["why", "reason", "explain"]):
        return (
            f"The recommendation is **{rec}** because: "
            f"we found {counts['papers']} papers, {counts['trials']} trials, "
            f"{counts['drugs']} drugs, {counts.get('regulatory', 0)} regulatory authorizations, "
            f"and {counts.get('patents', 0)} patents. "
            f"The literature signal is {context['studied_before'].lower()}, "
            f"practical testing is {context['tested_in_practice'].lower()}, "
            f"and competitive pressure is {context['competitive_pressure'].lower()}. "
            f"\n\n**{context['rationale']}**"
        )

    if any(w in msg_lower for w in ["next", "what now", "should i", "recommend"]):
        if rec == "Proceed":
            return (
                "This space looks underexplored — that's promising! Next steps:\n\n"
                "1. **Validate** the finding with a domain expert\n"
                "2. **Refine** your query — try different phrasings to make sure you haven't missed anything\n"
                "3. **Check** for preprints and conference abstracts not yet indexed\n"
                "4. **Consider** running a deeper search on the specific mechanism or target"
            )
        elif rec == "Review carefully":
            return (
                "There's meaningful prior activity here. Before committing:\n\n"
                "1. **Differentiate** — what specific angle, population, or mechanism is new?\n"
                "2. **Check the stopped trials** — learn from what didn't work\n"
                "3. **Map competitors** — who has the late-stage programs?\n"
                "4. **Narrow the query** — try a more specific hypothesis"
            )
        else:  # Reframe
            return (
                "This space is crowded with prior work and/or failure signals. Rather than abandoning it:\n\n"
                "1. **Change the hypothesis** — same disease, different mechanism?\n"
                "2. **Shift the population** — a subgroup not yet studied?\n"
                "3. **Combine differently** — can you pair with something that changes the dynamics?\n"
                "4. **Look at the stopped trials** — what did they learn, and can you avoid the same pitfalls?"
            )

    if any(w in msg_lower for w in ["stopped", "terminated", "failed", "withdrawn"]):
        stopped = counts.get("stopped", 0)
        if stopped > 0:
            return (
                f"We found {stopped} stopped, terminated, suspended, or withdrawn "
                f"trial{'s' if stopped != 1 else ''}. This is a caution signal — "
                f"something about the approach didn't work in practice. "
                f"Check the evidence table for details on which trials stopped and why."
            )
        return "No stopped or withdrawn trials were found in the results."

    if any(w in msg_lower for w in ["competitor", "competitive", "crowded", "landscape"]):
        return (
            f"Competitive pressure is **{context['competitive_pressure'].lower()}**. "
            f"We found {counts['drugs']} drugs/interventions and "
            f"{counts.get('patents', 0)} patents in this space. "
            f"{counts.get('late_stage', 0)} are late-stage or approved. "
            f"This suggests the space is "
            f"{'already well-populated' if context['competitive_pressure'] == 'High' else 'moderately active' if context['competitive_pressure'] == 'Moderate' else 'relatively open'}."
        )

    if any(w in msg_lower for w in ["regulatory", "fda", "ema", "approved", "authorization"]):
        reg_count = counts.get("regulatory", 0)
        if reg_count > 0:
            return (
                f"I found {reg_count} regulatory authorization{'s' if reg_count != 1 else ''} "
                f"(FDA and/or EMA). Check the evidence table — I've flagged active authorizations "
                f"with ✅. This tells you whether related products have already passed regulatory review."
            )
        return "No regulatory authorizations were found — this doesn't mean none exist, but none matched the search."

    if any(w in msg_lower for w in ["patent", "ip"]):
        pt_count = counts.get("patents", 0)
        if pt_count > 0:
            return (
                f"{pt_count} patent{'s' if pt_count != 1 else ''} found. "
                f"Key assignees are listed in the evidence table. "
                f"This gives you a sense of who is actively protecting IP in this space."
            )
        return "No patents were found for this query."

    if any(w in msg_lower for w in ["summary", "overview", "tldr"]):
        return (
            f"**{rec}** — {context['rationale']}\n\n"
            f"📄 Literature: {context['studied_before']} ({counts['papers']} papers)\n"
            f"🔬 Testing: {context['tested_in_practice']} ({counts['trials']} trials, {counts.get('stopped', 0)} stopped)\n"
            f"💊 Translation: {context['translation_signal']} ({counts.get('late_stage', 0)} late-stage)\n"
            f"🏭 Competition: {context['competitive_pressure']} ({counts['drugs']} drugs, {counts.get('patents', 0)} patents)"
        )

    return (
        f"Good question. Based on the assessment for *'{context['idea'][:80]}'*, "
        f"the overall recommendation is **{rec}**. "
        f"I can help you dig into specific aspects — try asking about:\n\n"
        f"- Why this recommendation?\n"
        f"- What should I do next?\n"
        f"- Tell me about the stopped/failed trials\n"
        f"- What's the competitive landscape?\n"
        f"- Any regulatory or patent activity?\n"
        f"- Give me a summary"
    )
