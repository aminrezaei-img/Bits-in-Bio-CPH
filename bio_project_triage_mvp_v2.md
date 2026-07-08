# Bio Project Triage — Hackathon MVP v2

## 1. Product decision

The product should not be framed as a graph, prototype, API demo, or technical visualization. It should be framed as a decision-support product.

**Recommended name:** Bio Project Triage  
**Tagline:** Decide whether a bio idea is worth pursuing before spending weeks on it.  
**Core question:** Is this idea promising, crowded, already tested, or in need of reframing?

The evidence map can remain inside the product, but it should be a supporting view, not the product identity.

## 2. User-facing promise

Bio Project Triage gives a fast first-pass read on a biological project idea. The user enters an idea, and the system checks structured evidence sources to answer:

1. Has this been studied before?
2. Has it been tested in practice?
3. Are there signs of translation or approval?
4. Is there commercial or competitive pressure?
5. Should the user proceed, review carefully, or reframe?

The output should feel like a serious decision brief, not a prototype experiment.

## 3. Recommended verdict language

Avoid harsh or overconfident language like “NO-GO” as the main product label. Use user-aware decision language:

| Internal meaning | User-facing label | Explanation |
|---|---|---|
| Low crowding / weak prior evidence | **Proceed** | Worth exploring, but still requires expert review. |
| Mixed or crowded evidence | **Review carefully** | Prior work exists; user needs a clearer angle. |
| Strong crowding, prior testing, or failure signal | **Reframe** | Do not treat this as fresh; change the hypothesis, population, mechanism, or positioning. |

This is more constructive than “kill the idea” while preserving the triage value.

## 4. MVP scope

The MVP should be deliberately small and demo-safe.

### Must-have

1. Streamlit app.
2. One input box.
3. One “Assess project” button.
4. Three Amass source groups only:
   - Literature/papers
   - Trials/studies
   - Drugs/interventions
5. Simple evidence counts.
6. Simple transparent scoring.
7. One big recommendation card.
8. One evidence table showing top records.
9. Cached golden demo query.

### Nice-to-have

10. Regulatory records.
11. Patent/commercial records.
12. Simple evidence map.

### Skip unless everything else is done

13. DSPy query planning.
14. Advanced graph expansion.
15. Gene/target core.
16. Multi-hop traversal.
17. Complex graph visualization.
18. Multi-module agent architecture.

## 5. MVP user flow

```text
User enters idea
↓
System searches 3 source groups
↓
System counts evidence signals
↓
System assigns recommendation:
    Proceed / Review carefully / Reframe
↓
System shows:
    Recommendation card
    Four evidence cards
    Top evidence table
    Optional evidence map
```

## 6. Main UI

### Header

**Bio Project Triage**  
Decide whether a bio idea is worth pursuing before spending weeks on it.

### Input

“Describe the project idea, target, intervention, disease area, or hypothesis you want to assess.”

### Button

**Assess project**

### Output sections

1. **Recommendation**
   - Proceed / Review carefully / Reframe
   - One-sentence explanation

2. **What we found**
   - Studied before
   - Tested in practice
   - Translation signal
   - Competitive pressure

3. **Why this matters**
   - Three short bullets explaining the result.

4. **Supporting evidence**
   - Table of retrieved records.

5. **Evidence map** *(optional)*
   - A simple visual showing the idea connected to retrieved papers, studies, interventions, approvals, or patents.

## 7. Evidence cards

Use simple cards that a non-technical judge can understand in three seconds.

### Card 1 — Studied before

Source: literature/paper results.

Examples:
- “Low literature signal”
- “Moderate literature signal”
- “High literature signal”

### Card 2 — Tested in practice

Source: trial/study results.

Examples:
- “No practical testing found”
- “Some testing found”
- “Multiple practical tests found”
- “Stopped or withdrawn studies found”

### Card 3 — Translation signal

Source: drugs/interventions and optional regulatory records.

Examples:
- “No translation signal found”
- “Early translation signal”
- “Late-stage or approved signal”

### Card 4 — Competitive pressure

Source: optional patent/commercial records and number of known interventions.

Examples:
- “Low competitive pressure”
- “Moderate competitive pressure”
- “High competitive pressure”

## 8. Simplified scoring

Use transparent rules. Do not present arbitrary weighted formulas as scientific truth.

### Inputs

```python
paper_count
trial_count
drug_count
regulatory_count
patent_count
terminated_or_withdrawn_trial_count
approved_or_late_stage_count
```

### Rules

```python
low_data = (paper_count + trial_count + drug_count) < 5

studied_before = (
    "High" if paper_count >= 25 else
    "Moderate" if paper_count >= 8 else
    "Low"
)

tested_in_practice = (
    "High" if trial_count >= 10 else
    "Moderate" if trial_count >= 3 else
    "Low"
)

failure_signal = (
    "High" if terminated_or_withdrawn_trial_count >= 3 else
    "Moderate" if terminated_or_withdrawn_trial_count >= 1 else
    "Low"
)

translation_signal = (
    "High" if approved_or_late_stage_count >= 3 else
    "Moderate" if approved_or_late_stage_count >= 1 else
    "Low"
)

competitive_pressure = (
    "High" if patent_count >= 10 or drug_count >= 10 else
    "Moderate" if patent_count >= 3 or drug_count >= 3 else
    "Low"
)
```

### Recommendation logic

```python
if low_data:
    recommendation = "Proceed"
    rationale = "Limited indexed evidence found; this may be underexplored or the query may need refinement."

elif failure_signal == "High":
    recommendation = "Reframe"
    rationale = "Prior practical testing shows repeated stop or withdrawal signals."

elif competitive_pressure == "High" and translation_signal in ["Moderate", "High"]:
    recommendation = "Reframe"
    rationale = "The space appears crowded and already translated."

elif tested_in_practice in ["Moderate", "High"] or competitive_pressure == "Moderate":
    recommendation = "Review carefully"
    rationale = "There is meaningful prior activity; a clearer differentiating angle is needed."

else:
    recommendation = "Proceed"
    rationale = "No strong crowding or failure signal was found in the retrieved evidence."
```

### Low-data warning

Always show this when total results are low:

> “Low data warning: absence of retrieved records does not prove novelty. The query may be too narrow, newly emerging, or not well indexed.”

## 9. Evidence table

Use one combined table first. Tabs are optional.

Columns:

| Column | Meaning |
|---|---|
| Source | Paper / Trial / Intervention / Regulatory / Patent |
| Title or name | Human-readable record name |
| Status | Study status, stage, authorization status, or record type |
| Date | Publication, start, completion, or authorization date |
| Signal | Why this record matters |
| ID/link | Amass ID or source URL |

The table is more important than the graph. It is reliable, understandable, and demo-safe.

## 10. Optional evidence map

If implemented, keep it simple.

Do not call the product a graph. Call it **Evidence map**.

Rules:

- Max 25 nodes.
- Center node = user idea.
- Other nodes = top retrieved records.
- Edges only mean “retrieved as relevant” unless cross-links are confidently available.
- Do not spend more than 20 minutes debugging this.

If visualization fails, remove it and keep the table.

## 11. Amass usage strategy

### Build first with 3 groups

1. Literature/papers
2. Trials/studies
3. Drugs/interventions

### Add if time

4. Regulatory records
5. Patents

### Skip for MVP

6. Gene/target records, unless the API call is already working and the query clearly contains a target symbol.

## 12. API behavior

Implement one generic client:

```python
search_core(core_name, query, limit=20)
```

Use caching aggressively:

```python
@st.cache_data(ttl=3600)
def cached_search(core_name, query, limit):
    ...
```

Expected result handling:

- If an API call fails, show a warning and continue with available sources.
- If one source is unavailable, do not crash the app.
- If all sources fail, load cached demo data.

## 13. LLM usage

Do not make the LLM essential for the app.

### Required

The app must work using deterministic scoring and a template explanation.

### Optional

Use the local model or DeepSeek-style hosted model only for final wording:

```text
User idea:
{idea}

Evidence counts:
{counts}

Top evidence:
{top_records}

Recommendation:
{recommendation}

Write a concise decision brief with:
1. One-sentence verdict
2. Three evidence-backed reasons
3. Two caveats
```

DSPy can be added later, but do not make DSPy part of the MVP dependency chain.

## 14. Demo strategy

Prepare three cached queries:

1. **Proceed** example — low or early evidence.
2. **Review carefully** example — meaningful prior activity.
3. **Reframe** example — clear crowding, translation, or failure signal.

The live demo should use the most visually reliable query.

### Demo structure for 90 seconds

```text
0–15s: Problem
15–25s: Product
25–65s: Live demo
65–80s: What makes it different
80–90s: Closing
```

### Script

“Most bio ideas sound plausible. The expensive question is whether they are actually worth pursuing, or whether the space is already crowded, tested, or in need of a different angle.

Bio Project Triage gives a first-pass decision brief. I enter an idea, and it checks structured evidence across literature, trials, and intervention records.

The output is intentionally simple: proceed, review carefully, or reframe. Here we can see the reason: this idea has prior practical testing, several related interventions, and enough activity that a team should not treat it as fresh.

The important point is that the model is not inventing the answer. The recommendation is grounded in retrieved records, and the LLM is only used to explain the evidence clearly.”

## 15. Positioning

Use this positioning:

> “Bio Project Triage is not trying to replace expert review. It helps researchers, founders, and builders avoid wasting time by turning scattered evidence into a first-pass project decision.”

Do not lead with “knowledge graph,” “multi-core retrieval,” “DSPy,” or “agentic pipeline.” Those can be mentioned if asked technically.

Lead with:

- decision
- evidence
- time saved
- traceability
- simple recommendation

## 16. Competitive gap

Use this if judges ask why it matters:

> “Existing tools are either deep but expensive, or public but siloed. A founder or researcher can manually check papers, trial registries, regulatory records, and patents, but stitching them together takes hours. This gives a first-pass decision brief in under a minute.”

## 17. Business model one-liner

> “The product could start as a freemium tool for researchers and founders, with paid tiers for deeper evidence expansion, saved projects, team review, alerts, and exportable due-diligence reports.”

## 18. Technical priority order

1. Streamlit shell.
2. Amass client.
3. Three source searches.
4. Cached results.
5. Evidence counts.
6. Recommendation card.
7. Evidence table.
8. Template summary.
9. Regulatory/patent sources.
10. Optional evidence map.
11. Optional LLM synthesis.
12. Optional DSPy.

## 19. What success looks like

A successful hackathon demo does not need to show full technical ambition. It needs to make the audience understand the value in 10 seconds.

The winning screen should show:

1. A clear recommendation.
2. Four evidence signals.
3. A table of supporting records.
4. A short explanation.
5. Optional evidence map.

If those are working, the product is demo-ready.

## 20. Final instruction to Hermes

Build the smallest serious version of Bio Project Triage. Do not overbuild the graph, DSPy layer, or cross-core expansion. The product should feel like a decision brief, not an API showcase.

The app must be able to run from cached demo data if the API fails. The recommendation card and evidence table are the core of the demo. Everything else is secondary.
