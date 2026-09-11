import sys
import time
from app.agent.router import AgentRouter

def run_benchmark():
    router = AgentRouter()

    test_cases = [
        {
            "id": 1,
            "type": "RAG",
            "query": "What is your refund policy?",
            "expected_route": "rag"
        },
        {
            "id": 2,
            "type": "RAG",
            "query": "How long is the product warranty?",
            "expected_route": "rag"
        },
        {
            "id": 3,
            "type": "KAG",
            "query": "Where is my order #4521?",
            "expected_route": "kag"
        },
        {
            "id": 4,
            "type": "KAG",
            "query": "Who is handling my complaint for order #4521?",
            "expected_route": "kag"
        },
        {
            "id": 5,
            "type": "Hybrid",
            "query": "My order #4521 arrived damaged, what's your policy on that and who can help me?",
            "expected_route": "hybrid"
        },
        {
            "id": 6,
            "type": "Escalation",
            "query": "Can you hack into my account to reset my password manually?",
            "expected_route": "escalated"
        },
        {
            "id": 7,
            "type": "Escalation",
            "query": "Where is order #9999999?",
            "expected_route": "escalated"
        },
        {
            "id": 8,
            "type": "Direct",
            "query": "Hello, good morning!",
            "expected_route": "direct"
        }
    ]

    print("\n" + "="*80)
    print("      RUNNING LIVE END-TO-END SCENARIO BENCHMARK (PRD SECTION 17)")
    print("="*80 + "\n")

    results = []

    for tc in test_cases:
        print(f"[{tc['id']}/8] Testing [{tc['type']}]: \"{tc['query']}\"")
        t0 = time.time()
        res = router.process_message(tc["query"], session_id=f"bench_{tc['id']}")
        elapsed = round((time.time() - t0) * 1000, 2)

        match = (res.route_taken == tc["expected_route"])
        status = "MATCH" if match else f"MISMATCH (got {res.route_taken})"

        results.append({
            "id": tc["id"],
            "type": tc["type"],
            "query": tc["query"],
            "expected": tc["expected_route"],
            "actual": res.route_taken,
            "confidence": res.confidence_score,
            "escalated": res.escalated,
            "latency_ms": elapsed,
            "answer": res.answer,
            "match": match
        })

        print(f"       -> Route: {res.route_taken.upper()} | Confidence: {res.confidence_score} | Latency: {elapsed}ms | Status: {status}")
        preview_answer = res.answer[:140].replace("\n", " ")
        print(f"       -> Answer Preview: {preview_answer}...\n")

    print("\n" + "="*80)
    print("                           SUMMARY BENCHMARK TABLE")
    print("="*80)
    header = f"{'#':<3} | {'Type':<11} | {'Expected':<10} | {'Actual':<10} | {'Conf':<6} | {'Escalated':<9} | {'Latency':<9} | {'Status'}"
    print(header)
    print("-" * len(header))

    total_matches = 0
    for r in results:
        if r["match"]:
            total_matches += 1
        stat = "PASS" if r["match"] else "FAIL"
        print(f"{r['id']:<3} | {r['type']:<11} | {r['expected']:<10} | {r['actual']:<10} | {r['confidence']:<6.2f} | {str(r['escalated']):<9} | {r['latency_ms']:<7.0f}ms | {stat}")

    accuracy = (total_matches / len(results)) * 100
    print("-" * len(header))
    print(f"Total Scenarios: {len(results)} | Passed: {total_matches} | Accuracy: {accuracy:.1f}%\n")

if __name__ == "__main__":
    run_benchmark()
