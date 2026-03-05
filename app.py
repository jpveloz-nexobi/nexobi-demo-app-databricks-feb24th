import html
import json
import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# set_page_config MUST be the very first Streamlit command
st.set_page_config(
    page_title="NexoBI · Genie",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# CONFIG
# ==========================================================
def _secret(key: str, default: str = "") -> str:
    env_val = os.environ.get(key)
    if env_val:
        return env_val
    try:
        return st.secrets[key]
    except Exception:
        return default


def _bool_env(key: str, default: bool = False) -> bool:
    raw = _secret(key, str(default)).strip().lower()
    return raw in {"1", "true", "yes", "on"}


_raw_host = _secret("DATABRICKS_HOST", "dbc-51730115-505d.cloud.databricks.com")
DATABRICKS_HOST = _raw_host.replace("https://", "").replace("http://", "").rstrip("/")
GENIE_SPACE_ID = _secret("NEXOBI_GENIE_SPACE_ID", "")
LLM_ENDPOINT = _secret("NEXOBI_LLM_ENDPOINT", "databricks-meta-llama-3-1-70b-instruct")
ENABLE_LLM = _bool_env("NEXOBI_ENABLE_LLM", True)
MAX_HISTORY = int(_secret("NEXOBI_MAX_HISTORY", "10"))
MAX_TOOL_STEPS = int(_secret("NEXOBI_MAX_TOOL_STEPS", "4"))
GENIE_TIMEOUT_SEC = int(_secret("NEXOBI_GENIE_TIMEOUT_SEC", "90"))
GENIE_POLL_SEC = int(_secret("NEXOBI_GENIE_POLL_SEC", "2"))

PLAYBOOK_VS_ENDPOINT = _secret("NEXOBI_PLAYBOOK_VS_ENDPOINT", "")
PLAYBOOK_INDEX_NAME = _secret("NEXOBI_PLAYBOOK_INDEX_NAME", "")
PLAYBOOK_TEXT_COLUMN = _secret("NEXOBI_PLAYBOOK_TEXT_COLUMN", "content")
PLAYBOOK_ID_COLUMN = _secret("NEXOBI_PLAYBOOK_ID_COLUMN", "id")
PLAYBOOK_K = int(_secret("NEXOBI_PLAYBOOK_K", "4"))


# ==========================================================
# LOGGING
# ==========================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexobi_agent")


def _log(event: str, request_id: str, **kwargs: Any) -> None:
    logger.info(json.dumps({"event": event, "request_id": request_id, **kwargs}, default=str))


# ==========================================================
# CSS (original style)
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;900&family=DM+Sans:wght@400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;}
.stApp{background:#060D1A!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{max-width:720px;padding:1rem 1.5rem 3rem;}

@keyframes floatA{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(28px,-22px) scale(1.08)}}
@keyframes floatB{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-22px,20px) scale(.94)}}
@keyframes breathe{0%,100%{opacity:.9;transform:scale(1)}50%{opacity:1;transform:scale(1.08)}}
@keyframes drift1{0%{transform:translate(0,0)}25%{transform:translate(18px,-24px)}50%{transform:translate(-12px,-40px)}75%{transform:translate(22px,-14px)}100%{transform:translate(0,0)}}
@keyframes drift2{0%{transform:translate(0,0)}33%{transform:translate(-20px,14px)}66%{transform:translate(12px,28px)}100%{transform:translate(0,0)}}
@keyframes twinkle{0%,100%{opacity:.25;transform:scale(1)}50%{opacity:.75;transform:scale(1.5)}}
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes slideUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes inputGlow{0%,100%{box-shadow:0 0 0 0 rgba(0,192,107,0)}50%{box-shadow:0 0 22px 4px rgba(0,192,107,.16)}}

.page-orbs{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.page-orbs .op1{position:absolute;width:560px;height:560px;background:rgba(0,192,107,.12);border-radius:50%;filter:blur(95px);top:-160px;right:-90px;animation:floatA 9s ease-in-out infinite,breathe 7s ease-in-out infinite;}
.page-orbs .op2{position:absolute;width:440px;height:440px;background:rgba(0,153,82,.08);border-radius:50%;filter:blur(90px);bottom:-110px;left:-70px;animation:floatB 13s ease-in-out infinite,breathe 10s ease-in-out infinite reverse;}
.page-orbs .op3{position:absolute;width:280px;height:280px;background:rgba(0,192,107,.05);border-radius:50%;filter:blur(75px);top:40%;right:-40px;animation:floatA 17s ease-in-out infinite reverse;}
.page-orbs .pt{position:absolute;border-radius:50%;pointer-events:none;}
.page-orbs .pt1{width:3px;height:3px;background:rgba(0,192,107,.7);top:18%;left:12%;animation:drift1 9s ease-in-out infinite,twinkle 3.2s ease-in-out infinite;}
.page-orbs .pt2{width:2px;height:2px;background:rgba(0,192,107,.5);top:35%;left:72%;animation:drift2 11s ease-in-out infinite,twinkle 4.1s ease-in-out .8s infinite;}
.page-orbs .pt3{width:4px;height:4px;background:rgba(0,212,120,.6);top:62%;left:28%;animation:drift1 8s ease-in-out infinite,twinkle 2.8s ease-in-out 1.5s infinite;}
.page-orbs .pt4{width:2px;height:2px;background:rgba(0,192,107,.4);top:78%;left:58%;animation:drift2 14s ease-in-out infinite,twinkle 5s ease-in-out infinite;}

.ai-hero-wrap{text-align:center;padding:3rem 1rem 2rem;}
.ai-catch{font-family:'Plus Jakarta Sans',sans-serif;font-size:3rem;font-weight:900;color:#FFFFFF;line-height:1.08;margin-bottom:.6rem;}
.ai-catch-hi{background:linear-gradient(120deg,#00C06B 0%,#38BDF8 40%,#00C06B 80%);background-size:250% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation:shimmer 4s linear infinite;}
.ai-catch-sub{font-size:.85rem;color:rgba(255,255,255,.45);max-width:400px;margin:0 auto 2rem;}

.ai-bubble-user{display:flex;justify-content:flex-end;margin:.8rem 0 .15rem;animation:slideUp .18s ease-out;}
.ai-bubble-user span{background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);color:#F1F5F9;border-radius:18px 18px 4px 18px;padding:11px 16px;font-size:.87rem;font-weight:500;max-width:80%;display:inline-block;box-shadow:0 4px 18px rgba(0,0,0,.18);}
.ai-msg-label{display:flex;align-items:center;gap:6px;font-size:.68rem;font-weight:700;color:#00C06B;letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px;margin-top:.9rem;}
.ai-msg-label::before{content:'◆';font-size:.6rem;background:linear-gradient(135deg,#00C06B,#38BDF8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.ai-bubble-ai{background:rgba(255,255,255,.95)!important;border:none!important;border-left:3px solid #00C06B!important;border-radius:4px 18px 18px 18px!important;padding:14px 18px!important;margin:0 0 .3rem!important;font-size:.88rem!important;color:#1E293B!important;line-height:1.7!important;box-shadow:0 6px 28px rgba(0,0,0,.07)!important;animation:slideUp .2s ease-out;}
.ai-bubble-ai *{color:#334155!important;}
.ai-bubble-ai b,.ai-bubble-ai strong{color:#0F172A!important;}

html body textarea,[data-testid="stTextArea"] textarea{color:#000!important;-webkit-text-fill-color:#000!important;caret-color:#00C06B!important;background:#fff!important;border:1.5px solid rgba(0,192,107,.35)!important;border-radius:16px!important;padding:13px 16px!important;font-size:.9rem!important;line-height:1.5!important;resize:none!important;animation:inputGlow 3.5s ease-in-out infinite!important;}
html body textarea::placeholder{color:#475569!important;-webkit-text-fill-color:#475569!important;}
[data-testid="stTextArea"]>div,[data-testid="stTextArea"]>div>div{border:none!important;background:transparent!important;}

html body [data-testid="stBaseButton-primary"]{border-radius:50%!important;width:46px!important;min-width:46px!important;height:46px!important;padding:0!important;font-size:1.1rem!important;background:linear-gradient(135deg,#00C06B,#00875A)!important;color:#fff!important;border:none!important;box-shadow:0 4px 18px rgba(0,192,107,.35)!important;}
html body [data-testid="stBaseButton-primary"]:hover{box-shadow:0 6px 26px rgba(0,192,107,.5)!important;transform:scale(1.07)!important;}

.stButton>button{background:rgba(255,255,255,.07)!important;color:#CBD5E1!important;border:1px solid rgba(255,255,255,.12)!important;border-radius:12px!important;font-weight:600!important;}

.ai-label-rec{display:flex;align-items:center;gap:6px;font-size:.68rem;font-weight:700;color:#F59E0B;letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px;margin-top:.9rem;}
.ai-label-rec::before{content:'◆';font-size:.6rem;color:#F59E0B;}
.ai-bubble-rec{background:rgba(251,191,36,.07)!important;border-left:3px solid #F59E0B!important;border-radius:4px 18px 18px 18px!important;padding:14px 18px!important;margin:0 0 .3rem!important;font-size:.88rem!important;line-height:1.7!important;box-shadow:0 6px 28px rgba(0,0,0,.07)!important;animation:slideUp .2s ease-out;}
.ai-bubble-rec,.ai-bubble-rec *{color:#FEF3C7!important;}
.ai-bubble-rec b,.ai-bubble-rec strong{color:#FFFBEB!important;}

[data-testid="stExpander"]{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,.09)!important;border-radius:12px!important;}
[data-testid="stExpander"] summary{color:#CBD5E1!important;}
[data-testid="stDataFrame"]{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:12px!important;}
[data-testid="stDataFrame"] *{color:#CBD5E1!important;}
.stMarkdownContainer p{color:rgba(255,255,255,.3)!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-orbs">
  <div class="op1"></div><div class="op2"></div><div class="op3"></div>
  <div class="pt pt1"></div><div class="pt pt2"></div>
  <div class="pt pt3"></div><div class="pt pt4"></div>
</div>
""", unsafe_allow_html=True)


# ==========================================================
# Databricks API helpers
# ==========================================================
@st.cache_resource(show_spinner=False)
def _workspace_client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient()


def _dbx_do(method: str, path: str, request_id: str, body: Optional[dict] = None, retries: int = 4) -> dict:
    w = _workspace_client()
    backoff = 1.0
    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            t0 = time.time()
            out = w.api_client.do(method, path, body=body)
            _log("dbx_call_ok", request_id, method=method, path=path, attempt=attempt, ms=int((time.time() - t0) * 1000))
            return out
        except Exception as exc:
            last_exc = exc
            err = str(exc)
            retriable = any(t in err.lower() for t in ["429", "503", "502", "504", "timeout", "tempor"])
            _log("dbx_call_err", request_id, method=method, path=path, attempt=attempt, retriable=retriable, error=err)
            if not retriable or attempt == retries:
                break
            time.sleep(backoff)
            backoff = min(backoff * 2, 8)
    raise RuntimeError(f"Databricks API call failed: {method} {path}: {last_exc}")


def _typed_cell(v: dict) -> Any:
    if "null" in v:
        return None
    if "long" in v:
        return int(v["long"])
    if "int" in v:
        return int(v["int"])
    if "double" in v:
        return float(v["double"])
    if "float" in v:
        return float(v["float"])
    if "bool" in v:
        return bool(v["bool"])
    if "str" in v:
        return str(v["str"])
    return next((x for x in v.values() if x is not None), None)


def _call_genie(question: str, request_id: str) -> Dict[str, Any]:
    if not GENIE_SPACE_ID:
        return {"text": "", "sql": "", "df": pd.DataFrame(), "error": "no_genie_space"}

    base = f"/api/2.0/genie/spaces/{GENIE_SPACE_ID}"
    conv_id = st.session_state.get("genie_conversation_id")

    if conv_id:
        data = _dbx_do("POST", f"{base}/conversations/{conv_id}/messages", request_id=request_id, body={"content": question})
    else:
        data = _dbx_do("POST", f"{base}/start-conversation", request_id=request_id, body={"content": question})

    conv_id = data.get("conversation_id", conv_id)
    msg_id = data.get("message_id") or data.get("id")
    st.session_state["genie_conversation_id"] = conv_id

    poll = f"{base}/conversations/{conv_id}/messages/{msg_id}"
    status, payload, elapsed = "PENDING", {}, 0
    while status not in ("COMPLETED", "FAILED") and elapsed < GENIE_TIMEOUT_SEC:
        time.sleep(GENIE_POLL_SEC)
        elapsed += GENIE_POLL_SEC
        payload = _dbx_do("GET", poll, request_id=request_id)
        status = payload.get("status", "PENDING")

    if status != "COMPLETED":
        return {"text": "", "sql": "", "df": pd.DataFrame(), "error": payload.get("error", "Genie query failed")}

    answer_text, answer_sql, answer_desc = "", "", ""
    for att in payload.get("attachments", []):
        if "text" in att:
            answer_text = att["text"].get("content", "")
        if "query" in att:
            answer_sql = att["query"].get("query", "")
            answer_desc = att["query"].get("description", "")
    if not answer_text and answer_desc:
        answer_text = answer_desc

    df = pd.DataFrame()
    if answer_sql:
        try:
            rdata = _dbx_do("GET", f"{poll}/query-result", request_id=request_id)
            cols = [c["name"] for c in rdata.get("manifest", {}).get("schema", {}).get("columns", [])]
            rows = [[_typed_cell(v) for v in r.get("values", [])] for r in rdata.get("result", {}).get("data_typed_array", [])[:200]]
            if cols:
                df = pd.DataFrame(rows, columns=cols)
        except Exception as exc:
            _log("genie_result_parse_err", request_id, error=str(exc))

    return {"text": answer_text, "sql": answer_sql, "df": df, "error": None}


@st.cache_resource(show_spinner=False)
def _vector_search_client():
    from databricks.vector_search.client import VectorSearchClient
    return VectorSearchClient()


def _extract_vs_rows(raw: dict) -> List[dict]:
    cols = [c.get("name") if isinstance(c, dict) else str(c) for c in raw.get("manifest", {}).get("columns", [])]
    arr = raw.get("result", {}).get("data_array")
    if arr and cols:
        return [{cols[i]: row[i] for i in range(min(len(cols), len(row)))} for row in arr]
    docs = raw.get("result", {}).get("docs")
    if isinstance(docs, list):
        return docs
    if isinstance(raw.get("results"), list):
        return raw["results"]
    if isinstance(raw.get("data"), list):
        return raw["data"]
    return []


def _tool_retrieve_playbook(query: str, request_id: str, k: Optional[int] = None) -> Dict[str, Any]:
    if not PLAYBOOK_VS_ENDPOINT or not PLAYBOOK_INDEX_NAME:
        return {"ok": True, "count": 0, "snippets": [], "summary": ""}
    try:
        top_k = max(1, min(int(k or PLAYBOOK_K), 10))
        c = _vector_search_client()
        idx = c.get_index(endpoint_name=PLAYBOOK_VS_ENDPOINT, index_name=PLAYBOOK_INDEX_NAME)
        raw = idx.similarity_search(query_text=query, columns=[PLAYBOOK_ID_COLUMN, PLAYBOOK_TEXT_COLUMN], num_results=top_k)
        rows = _extract_vs_rows(raw if isinstance(raw, dict) else {})
        snippets = []
        for r in rows:
            did = r.get(PLAYBOOK_ID_COLUMN) or r.get("id") or "doc"
            txt = str(r.get(PLAYBOOK_TEXT_COLUMN) or r.get("content") or r.get("text") or "").strip()
            if txt:
                snippets.append({"id": str(did), "text": txt[:1200]})
        return {"ok": True, "count": len(snippets), "snippets": snippets, "summary": "\n".join([s["text"][:250] for s in snippets[:3]])}
    except Exception as exc:
        _log("playbook_retrieve_err", request_id, error=str(exc))
        return {"ok": False, "count": 0, "snippets": [], "summary": "", "error": str(exc)}


def _extract_assistant_text(resp: dict) -> str:
    return ((resp.get("choices") or [{}])[0].get("message") or {}).get("content", "") or ""


def _llm_invoke(messages: List[dict], request_id: str, tools: Optional[List[dict]] = None) -> dict:
    if not ENABLE_LLM or not LLM_ENDPOINT:
        raise RuntimeError("LLM disabled or endpoint missing")
    body: Dict[str, Any] = {"messages": messages, "temperature": 0.3, "max_tokens": 450}
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    return _dbx_do("POST", f"/serving-endpoints/{LLM_ENDPOINT}/invocations", request_id=request_id, body=body)


def _llm_synthesize(question: str, genie_text: str, df: pd.DataFrame, playbook: List[dict], request_id: str) -> str:
    parts = [f"Question: {question}"]
    if genie_text:
        parts.append(f"Metrics answer: {genie_text}")
    if df is not None and not df.empty:
        parts.append("Top data rows:\n" + df.head(15).to_string(index=False))
    if playbook:
        pb = "\n\n".join([f"[{p.get('id','doc')}] {p.get('text','')[:500]}" for p in playbook[:3]])
        parts.append("Playbook context:\n" + pb)

    resp = _llm_invoke(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an advisor for dental/medical practices. "
                    "Respond in plain prose with: direct answer, key insight, and one action this week. "
                    "Use playbook guidance when provided. Keep under 170 words."
                ),
            },
            {"role": "user", "content": "\n\n".join(parts)},
        ],
        request_id=request_id,
    )
    return _extract_assistant_text(resp)


def _agent_answer(question: str, request_id: str) -> Dict[str, Any]:
    tools: List[dict] = [
        {
            "type": "function",
            "function": {
                "name": "ask_genie",
                "description": "Query Genie for factual KPI/SQL answers.",
                "parameters": {
                    "type": "object",
                    "properties": {"question": {"type": "string"}},
                    "required": ["question"],
                },
            },
        }
    ]
    if PLAYBOOK_VS_ENDPOINT and PLAYBOOK_INDEX_NAME:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": "retrieve_playbook",
                    "description": "Fetch SOP snippets relevant to the question.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "k": {"type": "integer"},
                        },
                        "required": ["query"],
                    },
                },
            }
        )

    # Try tool-calling first.
    try:
        msgs: List[dict] = [
            {
                "role": "system",
                "content": (
                    "You are NexoBI Agent. Call ask_genie for metric questions. "
                    "Call retrieve_playbook for SOP guidance when useful. "
                    "After tools, produce final concise answer with direct answer, insight, action."
                ),
            },
            {"role": "user", "content": question},
        ]

        latest = {"text": "", "sql": "", "df": pd.DataFrame(), "playbook_snippets": []}
        for _ in range(MAX_TOOL_STEPS):
            r = _llm_invoke(messages=msgs, tools=tools, request_id=request_id)
            m = ((r.get("choices") or [{}])[0].get("message") or {})
            tool_calls = m.get("tool_calls") or []
            content = m.get("content", "")
            msgs.append({"role": "assistant", "content": content, "tool_calls": tool_calls if tool_calls else None})

            if not tool_calls:
                return {
                    "ok": True,
                    "text": content.strip() or latest["text"],
                    "sql": latest["sql"],
                    "df": latest["df"],
                    "playbook_snippets": latest["playbook_snippets"],
                    "error": None,
                }

            for tc in tool_calls:
                fn = (tc.get("function") or {}).get("name")
                call_id = tc.get("id", str(uuid.uuid4()))
                raw_args = (tc.get("function") or {}).get("arguments", "{}")
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception:
                    args = {}

                if fn == "ask_genie":
                    gp = _call_genie(args.get("question") or question, request_id=request_id)
                    if not gp.get("error"):
                        latest["text"] = gp.get("text", "")
                        latest["sql"] = gp.get("sql", "")
                        latest["df"] = gp.get("df", pd.DataFrame())
                    tool_payload = {k: v for k, v in gp.items() if k != "df"}
                elif fn == "retrieve_playbook":
                    pp = _tool_retrieve_playbook(args.get("query") or question, request_id=request_id, k=args.get("k"))
                    latest["playbook_snippets"] = pp.get("snippets", [])
                    tool_payload = pp
                else:
                    tool_payload = {"ok": False, "error": f"unknown tool {fn}"}

                msgs.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "name": fn,
                        "content": json.dumps(tool_payload, default=str),
                    }
                )

        return {"ok": False, "text": "", "sql": "", "df": pd.DataFrame(), "playbook_snippets": [], "error": "tool_step_limit"}

    except Exception as exc:
        # Fallback path for endpoints that do not support tools/tool_choice.
        _log("tool_calling_fallback", request_id, error=str(exc))
        genie = _call_genie(question, request_id=request_id)
        if genie.get("error"):
            return {
                "ok": False,
                "text": "",
                "sql": genie.get("sql", ""),
                "df": genie.get("df", pd.DataFrame()),
                "playbook_snippets": [],
                "error": f"Agent failed and Genie failed: {genie.get('error')}",
            }

        playbook = _tool_retrieve_playbook(question, request_id=request_id).get("snippets", [])
        try:
            final_text = _llm_synthesize(
                question=question,
                genie_text=genie.get("text", ""),
                df=genie.get("df", pd.DataFrame()),
                playbook=playbook,
                request_id=request_id,
            ) if ENABLE_LLM else genie.get("text", "")
        except Exception as llm_exc:
            _log("llm_synthesize_err", request_id, error=str(llm_exc))
            final_text = genie.get("text", "")

        return {
            "ok": True,
            "text": final_text,
            "sql": genie.get("sql", ""),
            "df": genie.get("df", pd.DataFrame()),
            "playbook_snippets": playbook,
            "error": None,
        }


def _auto_chart(df: pd.DataFrame) -> bool:
    if df is None or df.empty or len(df) < 2:
        return False

    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    for c in df.columns:
        if c in date_cols or c in numeric_cols:
            continue
        converted = pd.to_datetime(df[c], errors="coerce")
        if converted.notna().mean() > 0.7:
            df = df.copy()
            df[c] = converted
            date_cols.append(c)

    if date_cols and numeric_cols:
        idx = date_cols[0]
        chart_df = df[[idx] + numeric_cols[:3]].dropna().set_index(idx)
        if not chart_df.empty:
            st.line_chart(chart_df)
            return True

    if numeric_cols:
        first_num = numeric_cols[0]
        cat_cols = [c for c in df.columns if c not in numeric_cols]
        if cat_cols:
            idx = cat_cols[0]
            chart_df = df[[idx, first_num]].dropna().set_index(idx).sort_values(first_num, ascending=False).head(15)
            if not chart_df.empty:
                st.bar_chart(chart_df)
                return True
        st.line_chart(df[numeric_cols[:3]].dropna())
        return True

    return False


# ==========================================================
# MAIN
# ==========================================================
if "ai_history" not in st.session_state:
    st.session_state.ai_history = []
if "ai_nonce" not in st.session_state:
    st.session_state.ai_nonce = 0
if "genie_conversation_id" not in st.session_state:
    st.session_state.genie_conversation_id = None

has_history = len(st.session_state.ai_history) > 0
if not has_history:
    st.markdown("""
<div class="ai-hero-wrap">
  <div class="ai-catch">Ask anything about<br><span class="ai-catch-hi">your practice.</span></div>
  <div class="ai-catch-sub">Get straight answers from your data. No dashboards needed.</div>
</div>
""", unsafe_allow_html=True)

_icol, _scol = st.columns([11, 1])
with _icol:
    user_q = st.text_area(
        "", placeholder="Ask anything about your data…",
        label_visibility="collapsed",
        key=f"ai_input_{st.session_state.ai_nonce}",
        height=80
    )
with _scol:
    st.markdown('<div style="height:1.55rem"></div>', unsafe_allow_html=True)
    ask = st.button("↑", use_container_width=True, key="ai_ask", type="primary")

components.html("""<script>
(function(){
  var Q=["What was my production last month?","Which treatments have the highest show rate?","How many new patients this week?","Compare Google vs Facebook"],
      qi=0,ci=0,del=false;
  function ta(){return window.parent.document.querySelector('[data-testid="stTextArea"] textarea');}
  function tick(){
    var t=ta();if(!t||t.value.length>0){setTimeout(tick,400);return;}
    var q=Q[qi];
    if(del){ci=Math.max(0,ci-1);t.setAttribute("placeholder",q.slice(0,ci));if(ci===0){del=false;qi=(qi+1)%Q.length;setTimeout(tick,480);}else setTimeout(tick,28);}
    else{ci=Math.min(q.length,ci+1);t.setAttribute("placeholder",q.slice(0,ci));if(ci===q.length){del=true;setTimeout(tick,2200);}else setTimeout(tick,65);}
  }
  setTimeout(tick,900);
})();
(function(){
  var _b=null;
  function bind(){
    var t=window.parent.document.querySelector('[data-testid="stTextArea"] textarea');
    if(!t){setTimeout(bind,300);return;}if(t===_b){setTimeout(bind,600);return;}_b=t;
    t.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();var btn=window.parent.document.querySelector('[data-testid="stBaseButton-primary"]');if(btn)btn.click();}});
    setTimeout(bind,600);
  }
  setTimeout(bind,600);
})();
</script>""", height=0)

run_q = user_q.strip() if ask and user_q.strip() else None
if run_q:
    req_id = str(uuid.uuid4())
    with st.spinner("Thinking…"):
        try:
            result = _agent_answer(run_q, request_id=req_id)
        except Exception as exc:
            _log("agent_fatal", req_id, error=str(exc))
            result = {
                "ok": False,
                "text": "",
                "sql": "",
                "df": pd.DataFrame(),
                "playbook_snippets": [],
                "error": f"Request failed: {exc}",
            }

    st.session_state.ai_history.insert(0, {
        "q": run_q,
        "text": result.get("text", ""),
        "sql": result.get("sql", ""),
        "df": result.get("df", pd.DataFrame()),
        "error": result.get("error"),
        "is_llm": bool(result.get("text")),
        "playbook_snippets": result.get("playbook_snippets", []),
        "request_id": req_id,
    })
    st.session_state.ai_history = st.session_state.ai_history[:MAX_HISTORY]
    st.rerun()

for item in st.session_state.ai_history:
    q = item.get("q", "")
    text = item.get("text", "")
    sql = item.get("sql", "")
    df = item.get("df")
    error = item.get("error")
    req_id = item.get("request_id", "")

    st.markdown(f'<div class="ai-bubble-user"><span>{html.escape(q)}</span></div>', unsafe_allow_html=True)

    if error == "no_genie_space":
        st.markdown(
            '<div class="ai-msg-label">NexoBI AI</div>'
            '<div class="ai-bubble-ai" style="border-left:3px solid #F59E0B!important;">'
            '<b style="color:#92400E!important;">Genie not configured</b> — '
            'Set <code>NEXOBI_GENIE_SPACE_ID</code> in your Databricks Apps environment variables.'
            '</div>', unsafe_allow_html=True)
        continue

    if error:
        st.markdown(
            '<div class="ai-msg-label">NexoBI AI</div>'
            f'<div class="ai-bubble-ai" style="border-left:3px solid #EF4444!important;">'
            f'<b style="color:#991B1B!important;">Error</b> — {html.escape(str(error))}</div>'
            f'<div style="font-size:.72rem;color:#94A3B8;margin:.2rem 0 .4rem">Request ID: {html.escape(req_id)}</div>',
            unsafe_allow_html=True)
        continue

    if text:
        st.markdown(
            '<div class="ai-label-rec">NexoBI AI · Insights</div>'
            f'<div class="ai-bubble-rec">{html.escape(text)}</div>',
            unsafe_allow_html=True)

    snippets = item.get("playbook_snippets", [])
    if snippets:
        with st.expander("📚 Playbook context", expanded=False):
            for s in snippets:
                st.markdown(f"**{s.get('id','doc')}**")
                st.write(s.get("text", ""))

    if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
        _auto_chart(df)
        with st.expander("📋 View data", expanded=False):
            st.dataframe(df, use_container_width=True, hide_index=True)

    if sql:
        with st.expander("🔍 View SQL", expanded=False):
            st.code(sql, language="sql")

if has_history:
    st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
    _, _nc = st.columns([8, 2])
    with _nc:
        if st.button("↺  New chat", key="ai_reset", use_container_width=True):
            st.session_state.ai_history = []
            st.session_state.ai_nonce += 1
            st.session_state.genie_conversation_id = None
            st.rerun()
