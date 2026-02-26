# NexoBI Demo Script
### Full Demo · 5–7 Minutes

> **Before you start:** Have the app open on the Dashboard in CSV mode. Databricks should be ready to switch live. Use the story cards and AI questions below in order — they build on each other.

---

## Opening (30 sec)

> *"What I'm going to show you today is NexoBI — a real-time marketing intelligence platform built specifically for healthcare practices. Most practices are flying blind between their ad platforms, CRM, and revenue data. NexoBI connects all of that in one place and puts an AI analyst on top of it. Let me show you."*

---

## Act 1 — Command Center (1 min)

**What to show:** The top section of the Dashboard.

**Say:**
> *"The first thing a practice owner sees every morning is this — a Platform Health Score. It's not just a vanity metric. It's computed from four things that actually matter: ROAS, cost per lead, show rate, and revenue growth. Right now we're at [X] out of 100."*

Point to the four stat pills (Revenue · ROAS · CPL · Show Rate):
> *"Each one benchmarks against healthcare industry averages — so you instantly know not just what your numbers are, but whether they're good or not."*

Point to the Revenue Forecast chart:
> *"And this is a 14-day revenue projection based on linear regression of your actual daily data. Not a guess — math."*

Point to the Top Signals column:
> *"On the right, the system proactively surfaces the three most important things happening right now. No need to go looking for problems — they come to you."*

---

## Act 2 — Patient Funnel (1 min)

**What to show:** Scroll to the Patient Acquisition Funnel section.

**Say:**
> *"This is where most practices are losing money without knowing it. The funnel shows Leads → Booked → Attended. Three stages, and there's a drop at every one."*

Point to the funnel chart:
> *"Your booking rate tells you how good your front desk is at converting inquiries. Your show rate tells you how many of those patients actually show up. If either one drops, revenue drops — even if your ads are performing perfectly."*

Point to the table on the right:
> *"The table breaks it down with exact conversion rates at each stage and flags your total funnel drop-off. This one number — [X]% — tells you how much revenue you're leaving on the table before a single patient walks through the door."*

---

## Act 3 — Story Mode (30 sec)

**What to show:** Click one of the Story Cards (e.g. "ROAS Drop").

**Say:**
> *"We also built in guided demo scenarios — real situations practices face. I'll activate the ROAS Drop scenario."*

Point to the banner that appears:
> *"It tells you exactly what to look at in the dashboard and — this is key — gives you AI questions pre-written and ready to ask. This is how we turn data into a conversation."*

---

## Act 4 — AI Agent, CSV Mode (1 min)

**What to show:** Switch to the AI Agent page.

**Say:**
> *"This is the AI Agent. Even in offline mode — no cloud, no live connection — it answers data questions directly from your dataset."*

Type and submit:
> `"Google vs Facebook — revenue, ROAS, and leads"`

**Say while it responds:**
> *"It's pulling from the same data as the dashboard — so the numbers are always consistent. No hallucinations, no made-up figures."*

When the comparison table appears:
> *"Side-by-side. Revenue, ROAS, leads. Instantly. Now watch what happens when we go live."*

---

## Act 5 — AI Agent, Live Mode (2 min)

**What to show:** Click "Switch to Live →" in the sidebar.

**Say:**
> *"We're now connected to Databricks. The AI Agent is running on Llama 3.3 70B — Meta's most capable open model — served through Databricks Model Serving. This is enterprise-grade AI, not a wrapper around ChatGPT."*

**Question 1** — type and submit:
> `"Where are we losing the most patients in the funnel — from leads to booked to attended — and which source has the worst drop-off?"`

**Say while it loads:**
> *"This is a multi-stage reasoning question. It has to analyze three metrics across multiple sources and rank them. A junior analyst would spend 30 minutes on this."*

When the answer appears:
> *"[Pause — let them read it.] That's the source you need to have a conversation with your front desk about."*

**Question 2** — type and submit:
> `"Show me the week-over-week trend for ROAS by channel over the last 60 days and flag any significant drops."`

**Say while it loads:**
> *"Now we're asking for a time-series analysis with anomaly detection — and because I used the word 'show me', it knows to generate a chart."*

When chart appears:
> *"[Point to any drop.] This is the moment a practice owner calls their agency. Except with NexoBI, they see it before the agency does."*

---

## Act 6 — Competitive Edge (30 sec)

**Say:**
> *"Here's what makes this different from every other healthcare analytics tool out there:"*

> *"Most dashboards just show you what happened. NexoBI tells you why it happened and what to do about it — through the AI Agent, the Health Score, and the proactive signals."*

> *"It runs on your Databricks infrastructure, so your data never leaves your environment. No third-party AI provider touching patient-adjacent data."*

> *"And unlike generic BI tools like Tableau or Looker, this is built for one vertical — healthcare marketing — with the benchmarks, the funnel logic, and the language already embedded."*

---

## Close (30 sec)

**Say:**
> *"What you saw today is a working product — not a mockup. Everything is live, the AI is real, and it's deployable on Databricks Apps in under a day if you already have a Unity Catalog table."*

> *"The question for your practice is: how much revenue are you currently leaving in your funnel, and how long does it take you to find out? NexoBI makes that answer available every morning before your first coffee."*

> *"What questions do you have?"*

---

## Quick Reference Card

| Section | Time | Key line |
|---|---|---|
| Opening | 0:00 – 0:30 | "Flying blind between ad platforms, CRM, and revenue" |
| Command Center | 0:30 – 1:30 | "Health Score — four things that actually matter" |
| Patient Funnel | 1:30 – 2:30 | "How much revenue you're leaving on the table" |
| Story Mode | 2:30 – 3:00 | "AI questions pre-written and ready to ask" |
| AI Agent CSV | 3:00 – 4:00 | "Google vs Facebook — no hallucinations" |
| AI Agent Live | 4:00 – 6:00 | "Llama 3.3 70B — not a wrapper around ChatGPT" |
| Competitive Edge | 6:00 – 6:30 | "Built for one vertical — benchmarks already embedded" |
| Close | 6:30 – 7:00 | "Deployable in under a day" |

---

## Tech Stack (for technical audiences)

| Layer | Technology |
|---|---|
| Frontend | Streamlit (Python) |
| Charts | Plotly |
| Data warehouse | Databricks Unity Catalog (Delta tables) |
| AI model | Llama 3.3 70B via Databricks Model Serving |
| AI routing | Native `ai_query()` SQL function — no external API calls |
| Deployment | Databricks Apps |
| Offline fallback | Local CSV + pattern-matched engine |

---

## Competitive Advantages (one-liners)

- **vs Tableau / Looker / Power BI** — Those are blank canvases. NexoBI ships with healthcare marketing logic, benchmarks, and AI built in.
- **vs Generic ChatGPT wrappers** — Data never leaves your Databricks environment. No third-party AI touching your data.
- **vs Agency dashboards** — Practices see the same data the agency sees — in real time, not in a monthly PDF.
- **vs Manual reporting** — The Health Score, signals, and AI Agent replace 80% of the questions a practice owner asks their marketing team every week.
- **vs Other AI analytics tools** — Built on open-source Llama via Databricks, not locked into a proprietary model with unpredictable pricing.

---

*NexoBI · Demo Script · February 2026*
