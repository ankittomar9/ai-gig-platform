import asyncio
import pytest
from app.services.interview_agent import start_new_interview, process_interview_reply
from app.database import set_setting

def test_interview_initial_state():
    session = asyncio.run(start_new_interview("direct_turing_java_engineer"))
    assert session["current_round"] == 1
    assert session["total_rounds"] == 4
    assert session["is_completed"] is False
    assert session["overall_score"] is None
    assert len(session["messages"]) == 1
    assert session["messages"][0]["score"] is None
    assert session["messages"][0]["sender"] == "ai"

def test_round_advance_and_offline_marking():
    # Force offline mode to guarantee deterministic heuristic evaluation
    set_setting("offline_mode", "true")
    session = asyncio.run(start_new_interview("direct_turing_java_engineer"))
    session_id = session["session_id"]

    # Reply to Round 1
    reply1 = "I have 3 years of hands-on Java and Spring Boot experience building production microservices and SQL databases."
    updated1 = asyncio.run(process_interview_reply(session_id, reply1))

    assert updated1["current_round"] == 2
    assert updated1["is_offline_fallback"] is True
    assert len(updated1["messages"]) == 3 # init AI + user reply + round 1 feedback AI
    round1_eval = updated1["messages"][2]
    assert round1_eval["evaluation_source"] == "heuristic"
    assert round1_eval["score"] is not None
    assert round1_eval["score"] in range(1, 11)

def test_interview_full_completion_honest_score():
    set_setting("offline_mode", "true")
    session = asyncio.run(start_new_interview("direct_turing_java_engineer"))
    session_id = session["session_id"]

    # Play through all 4 rounds
    for r in range(1, 5):
        reply = f"Comprehensive structured engineering response for round {r} detailing architecture, error handling, edge cases, and benchmarks."
        session = asyncio.run(process_interview_reply(session_id, reply))

    assert session["is_completed"] is True
    assert session["current_round"] == 4
    assert session["overall_score"] is not None
    assert 0 <= session["overall_score"] <= 100
    # Ensure it is computed mathematically across scored rounds
    scored_messages = [m for m in session["messages"] if m.get("score") is not None]
    expected_avg = int(sum(m["score"] for m in scored_messages) / len(scored_messages) * 10)
    assert session["overall_score"] == expected_avg
