#!/usr/bin/env python3

import json
from pathlib import Path
from flask import Flask, jsonify, render_template

app = Flask(__name__)

ETC = Path("/etc/aidrax/ai-core")
VAR = Path("/var/lib/aidrax/ai-core")


def read_json(path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def tail_jsonl(path, count=10):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-count:]
        result = []
        for line in lines:
            try:
                result.append(json.loads(line))
            except Exception:
                pass
        return result
    except Exception:
        return []


def provider_summary():
    data = read_json(ETC / "providers.json", {"providers": []})
    return data.get("providers", [])


def node_summary():
    data = read_json(ETC / "orchestrator.json", {"nodes": {}})
    result = []

    for node_id, node in data.get("nodes", {}).items():
        result.append({
            "id": node_id,
            "role": node.get("role", "unknown"),
            "enabled": node.get("enabled", False),
        })

    return result


def evolution_summary():
    return {
        "observation": (ETC / "evolution.json").exists(),
        "scoring": (ETC / "scoring.json").exists(),
        "skill_learning": (ETC / "skill-learning.json").exists(),
        "proposal_engine": (ETC / "proposals.json").exists(),
        "sandbox": (ETC / "sandbox.json").exists(),
        "self_healing": (ETC / "self-healing.json").exists(),
        "dataset_pipeline": (ETC / "local-learning.json").exists(),
        "controller": (ETC / "evolution-controller.json").exists(),
    }


def dashboard_data():
    state = read_json(
        VAR / "state/core-state.json",
        {}
    )

    owner = read_json(
        ETC / "owner-gate.json",
        {}
    )

    observations = tail_jsonl(
        VAR / "evolution/observations/events.jsonl",
        10
    )

    audit = tail_jsonl(
        VAR / "audit/ledger.jsonl",
        10
    )

    proposals_dir = VAR / "evolution/proposals"
    proposals = []

    if proposals_dir.exists():
        for path in sorted(
            proposals_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:10]:
            data = read_json(path)
            if data:
                proposals.append(data)

    skills_dir = VAR / "evolution/skills"
    skills = []

    if skills_dir.exists():
        for path in sorted(
            skills_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:10]:
            data = read_json(path)
            if data:
                skills.append(data)

    return {
        "build": "AO-028C-01",
        "state": state,
        "providers": provider_summary(),
        "nodes": node_summary(),
        "evolution": evolution_summary(),
        "owner_gate": owner,
        "observations": observations,
        "audit": audit,
        "proposals": proposals,
        "skills": skills,
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        data=dashboard_data()
    )


@app.route("/api/status")
def api_status():
    return jsonify(dashboard_data())


@app.route("/api/health")
def api_health():
    data = dashboard_data()

    return jsonify({
        "service": "aidrax-evolution-console",
        "build": data["build"],
        "status": "green"
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=18229,
        debug=False
    )
