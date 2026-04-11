from planner import create_plan
from executor import execute_plan
from synthesizer import synthesize


def run_agent(query: str):
    print("\n==============================")
    print("🔍 AI RESEARCH AGENT STARTED")
    print("==============================\n")

    print(f"[QUERY]: {query}")

    # -------------------------
    # Step 1: Planning
    # -------------------------
    print("\n[STEP 1] PLANNING...")
    plan = create_plan(query)
    print("[PLAN]:", plan)

    # -------------------------
    # Step 2: Execution
    # -------------------------
    print("\n[STEP 2] EXECUTION...")
    data = execute_plan(plan, query)

    print(f"[DATA COLLECTED]: {len(data)} sources")

    # -------------------------
    # Step 3: Synthesis
    # -------------------------
    print("\n[STEP 3] SYNTHESIS...")
    result = synthesize(query, data)

    # -------------------------
    # Final Output
    # -------------------------
    print("\n==============================")
    print("✅ FINAL OUTPUT")
    print("==============================\n")

    for key, value in result.items():
        print(f"{key.upper()}:\n{value}\n")

    return result


if __name__ == "__main__":
    query = input("Enter your research query: ")
    run_agent(query)