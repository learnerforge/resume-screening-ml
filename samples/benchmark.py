"""
Benchmark script: validates matching quality across sample resume/JD pairs.
Run: python -m samples.benchmark
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "resume_matcher"))

from src.matcher import match_resume_to_job

SAMPLES = Path(__file__).parent
SKILL_FILE = SAMPLES.parent / "resume_matcher" / "data" / "skills.txt"


def load(name: str) -> str:
    return (SAMPLES / name).read_text(encoding="utf-8").strip()


SCENARIOS = [
    # (resume, job, min_score, max_score, label)
    ("resume_data_scientist.txt",  "job_data_scientist.txt",    45, 100, "Data Scientist - good match"),
    ("resume_fullstack_dev.txt",   "job_fullstack_dev.txt",     45, 100, "Full Stack Dev - good match"),
    ("resume_devops_engineer.txt", "job_devops_engineer.txt",   45, 100, "DevOps Engineer - good match"),
    ("resume_data_scientist.txt",  "job_fullstack_dev.txt",      0,  40, "Data Scientist vs Full Stack - low match"),
    ("resume_fullstack_dev.txt",   "job_devops_engineer.txt",    0,  35, "Full Stack vs DevOps - low match"),
    ("resume_devops_engineer.txt", "job_data_scientist.txt",     0,  35, "DevOps vs Data Scientist - low match"),
]

PASS = 0
FAIL = 0

print("=" * 70)
print("RESUME MATCHER BENCHMARK")
print("=" * 70)

for resume_file, job_file, lo, hi, label in SCENARIOS:
    resume_text = load(resume_file)
    job_text = load(job_file)

    result = match_resume_to_job(
        resume_text,
        job_text,
        str(SKILL_FILE),
        text_weight=0.5,
        skill_weight=0.4,
        experience_weight=0.1,
    )

    score = result["final_score"]
    ok = lo <= score <= hi
    status = "PASS" if ok else "FAIL"

    if ok:
        PASS += 1
    else:
        FAIL += 1

    print(f"\n[{status}] {label}")
    print(f"       Score: {score:.1f}  (expected {lo}-{hi})")
    print(f"       Text:  {result['text_similarity']:.1f}  |  Skill: {result['skill_score']:.1f}  |  Exp: {result['experience_score']:.1f}")
    matched = ", ".join(result["matched_skills"][:8])
    missing = ", ".join(result["missing_skills"][:6])
    if matched:
        print(f"       Matched: {matched}")
    if missing:
        print(f"       Missing: {missing}")

print("\n" + "=" * 70)
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {len(SCENARIOS)}")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
