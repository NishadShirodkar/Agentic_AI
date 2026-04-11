from flask import Flask, jsonify, render_template, request

from executor import execute_plan
from planner import create_plan
from synthesizer import synthesize

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/research")
def research():
    payload = request.get_json(silent=True) or {}
    query = str(payload.get("query", "")).strip()

    if not query:
        return jsonify({"error": "Query is required."}), 400

    plan = create_plan(query)
    data = execute_plan(plan, query)
    result = synthesize(query, data)

    return jsonify(
        {
            "plan": plan,
            "source_count": len(data),
            "result": result,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
