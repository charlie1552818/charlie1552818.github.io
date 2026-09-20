from __future__ import annotations
import argparse, fnmatch, hashlib, json, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EXCLUDE_FILE = Path(__file__).resolve().parents[1] / "paper-index-excludes.txt"

CATEGORY_RULES = [
    ("Safety-Critical Control / CBF", ["control barrier", "barrier function", "cbf", "safety-critical", "safety critical", "safe control", "安全临界", "控制障碍", "安全控制", "nonsmooth safe"]),
    ("Marine / AUV / Underwater", ["auv", "underwater", "marine", "ocean", "docking", "水下", "海洋", "对接", "潜航"]),
    ("Soft Robotics / Morphology", ["spirob", "octobot", "soft robot", "soft robotics", "tendon", "morphology", "仿生", "软体", "触手", "绳驱", "对数螺旋"]),
    ("System Identification / Data-Driven / MPC", ["system identification", "identification", "parameter estimation", "gray-box", "grey-box", "data-driven", "koopman", "model predictive", "mpc", "辨识", "参数估计", "灰盒", "数据驱动", "模型预测"]),
    ("Multi-Agent / Distributed Control", ["multi-agent", "multiagent", "distributed", "consensus", "formation", "cooperative", "leader-following", "multi agent", "多智能体", "协同", "一致性", "编队", "分布式"]),
    ("Learning / AI / World Models", ["world model", "reinforcement learning", "deep learning", "machine learning", "neural network", "policy iteration", "q-learning", "世界模型", "强化学习", "深度学习", "机器学习", "神经网络", "感知"]),
    ("Adaptive / Nonlinear / Broad Learning", ["broad learning", "bls", "adaptive control", "adaptive", "nussbaum", "backstepping", "nonlinear", "fixed-time", "prescribed-time", "predefined", "宽度学习", "自适应", "非线性", "反步", "预设时间", "固定时间"]),
    ("Robust / Constrained Control", ["robust", "constrained", "constraint", "saturation", "disturbance rejection", "鲁棒", "受限", "约束", "饱和", "扰动抑制"]),
    ("Robotics / Manipulation", ["robot", "robotics", "manipulator", "grasp", "机器人", "机械臂", "抓取"]),
]

def clean_title(stem: str) -> str:
    s = stem.replace("_", " ").replace("+", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def category_for(text: str) -> str:
    t = text.lower()
    for category, keys in CATEGORY_RULES:
        if any(k.lower() in t for k in keys):
            return category
    return "General Control / Other"

def load_exclude_patterns(path: Path | None) -> list[str]:
    if path is None or not path.is_file():
        return []
    patterns = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            patterns.append(line.replace("\\", "/"))
    return patterns


def is_excluded(rel: Path, patterns: list[str]) -> bool:
    candidate = rel.as_posix().lower()
    name = rel.name.lower()
    return any(
        fnmatch.fnmatch(candidate, pattern.lower()) or fnmatch.fnmatch(name, pattern.lower())
        for pattern in patterns
    )


def build(source: Path, output: Path, summary_output: Path | None = None, exclude_patterns: list[str] | None = None) -> dict:
    items = []
    excludes = exclude_patterns or []
    for p in sorted(source.rglob("*.pdf"), key=lambda x: str(x).lower()):
        if not p.is_file():
            continue
        rel = p.relative_to(source)
        if is_excluded(rel, excludes):
            continue
        parts = rel.parts
        group = parts[0] if len(parts) > 1 else "Root"
        collection = parts[1] if len(parts) > 2 else group
        searchable = " / ".join(parts)
        stable = hashlib.sha1(rel.as_posix().encode("utf-8")).hexdigest()[:16]
        st = p.stat()
        items.append({
            "id": stable,
            "title": clean_title(p.stem),
            "fileName": p.name,
            "category": category_for(searchable),
            "group": group,
            "collection": collection,
            "sizeMB": round(st.st_size / 1024 / 1024, 2),
            "modified": datetime.fromtimestamp(st.st_mtime).date().isoformat(),
            "publicPdf": None,
        })
    counts = Counter(x["category"] for x in items)
    groups = Counter(x["group"] for x in items)
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": len(items),
        "categories": [{"name": k, "count": v} for k, v in counts.most_common()],
        "groups": [{"name": k, "count": v} for k, v in groups.most_common()],
        "items": items,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("window.PAPER_LIBRARY = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    if summary_output is not None:
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary = {
            "generatedAt": payload["generatedAt"],
            "total": payload["total"],
            "categories": payload["categories"],
        }
        summary_output.write_text("window.PAPER_LIBRARY_SUMMARY = " + json.dumps(summary, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="Local research root; absolute path is never written to output")
    ap.add_argument("--output", default="papers-data.js")
    ap.add_argument("--summary-output", default=None)
    ap.add_argument("--exclude-file", default=str(DEFAULT_EXCLUDE_FILE), help="UTF-8 file of relative glob patterns to exclude")
    ap.add_argument("--exclude-glob", action="append", default=[], help="Additional relative glob pattern to exclude; repeatable")
    args = ap.parse_args()
    patterns = load_exclude_patterns(Path(args.exclude_file) if args.exclude_file else None)
    patterns.extend(args.exclude_glob)
    payload = build(Path(args.source), Path(args.output), Path(args.summary_output) if args.summary_output else None, patterns)
    print(json.dumps({"total": payload["total"], "categories": payload["categories"]}, ensure_ascii=True))
