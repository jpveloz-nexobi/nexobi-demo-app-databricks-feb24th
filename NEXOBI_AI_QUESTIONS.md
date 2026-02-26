# NexoBI AI Agent — Demo Questions Reference

> Quick reference for all AI Agent questions by mode. Use this during demos, training, or QA testing.

---

## CSV Mode (Offline Engine)

Pattern-matched against the loaded CSV. No LLM. Works without Databricks.
Each question below is guaranteed to trigger the correct response path.

> ⚠️ **Avoid typos** — CSV mode uses exact keyword matching. Stick to the phrasing below.

| # | Question | Response type | Keywords triggered |
|---|---|---|---|
| 1 | "How much revenue did we generate last 30 days?" | Revenue summary + growth badge | default path |
| 2 | "What's our ROAS last 7 days?" | ROAS + spend + revenue breakdown | `roas`, `last 7` |
| 3 | "How many leads did we get and what's our cost per lead?" | Lead count + CPL + booking rate | `lead` |
| 4 | "What was our total ad spend last quarter?" | Spend + ROAS + revenue | `spend`, `quarter` |
| 5 | "What's our attendance rate and how many no-shows did we have?" | Show rate + booked vs attended | `attendance`, `no show` |
| 6 | "How many appointments were booked and what's our booking rate?" | Bookings + lead-to-book rate + show rate | `book`, `appointment` |
| 7 | "Google vs Facebook — revenue, ROAS, and leads" | Side-by-side comparison table | two sources detected |
| 8 | "Show me revenue by source last 90 days" | Ranked source table (Revenue · ROAS · Leads) | `by source`, `90 day` |

**Bonus questions that also work:**
- `"Top campaigns by ROAS"` → campaign table sorted by ROAS
- `"Leads by campaign last 7 days"` → campaign table sorted by leads
- `"Meta vs LinkedIn performance"` → comparison table
- `"What's our conversion rate?"` → leads path

**What does NOT work in CSV mode** (returns generic revenue fallback):
- Week-over-week / daily trends
- "Why did X drop?"
- Forecasting or projections
- Multi-condition questions ("campaigns where spend is up but leads are down")
- Save those for Live mode.

---

## Live Mode (Databricks — Llama 3.3 70B)

Full natural language. Typo-tolerant. Generates SQL, returns charts for visual questions.
Ordered from broad overview → deep diagnosis for maximum demo flow.

| # | Question | What it showcases |
|---|---|---|
| 1 | "Which campaigns are generating the most revenue per dollar spent, and how has that changed compared to last month?" | Campaign ROAS trend + period comparison |
| 2 | "Where are we losing the most patients in the funnel — from leads to booked to attended — and which source has the worst drop-off?" | Multi-stage funnel + source breakdown |
| 3 | "Compare ROAS across all channels over the last 90 days and tell me which channel deserves more budget" | Cross-channel efficiency + budget recommendation |
| 4 | "Are there any campaigns where spend is increasing but leads are dropping? Show me the worst offenders." | Anomaly detection + waste identification |
| 5 | "Which booking sources have the lowest show rates, and what's the revenue impact of our no-shows?" | Show rate + revenue leakage |
| 6 | "What is our cost per patient acquired by channel, and which channels are above our $45 benchmark?" | CPL benchmarking |
| 7 | "What drove our revenue growth this month compared to last month? Break it down by source and campaign." | Revenue attribution + growth drivers |
| 8 | "Show me the week-over-week trend for ROAS by channel over the last 60 days and flag any significant drops." | Time-series trend + anomaly with chart |

**Tips for triggering charts** — include any of these words to get a visual:
`chart · graph · plot · show me · trend · over time · daily · weekly · monthly · by source · compare · vs · breakdown · last 30 · mtd · traffic`

**Power follow-up questions** (after any answer):
- `"Which of those should I fix first?"`
- `"What would you recommend we do about that?"`
- `"Break that down by campaign"`
- `"Same question but for last 7 days"`

---

## Side-by-Side Comparison

| Capability | CSV Mode | Live Mode |
|---|---|---|
| Requires Databricks | ❌ No | ✅ Yes |
| Typo tolerant | ❌ No — exact keywords | ✅ Yes |
| Natural language | ❌ Limited patterns | ✅ Full |
| Charts / visualizations | ❌ No | ✅ Yes |
| Trend analysis | ❌ No | ✅ Yes |
| "Why did X drop?" | ❌ No | ✅ Yes |
| Budget recommendations | ❌ No | ✅ Yes |
| Response time | ⚡ Instant | ~3–8 seconds |
| Best for | Offline demos, no-cloud environments | Live client presentations |

---

*NexoBI · February 2026*
