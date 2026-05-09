# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Mock HR data and function tools for the bug-bash notebook.

Provides a self-contained HR recruitment scenario with:
- Mock data: job postings, candidates (external + internal), calendar slots
- Function tools for job lookup, candidate sourcing, evaluation, compliance,
  scheduling, and communication
"""

from pprint import pformat
from typing import Annotated

from agent_framework import tool

# ============================================================================
# Mock Data
# ============================================================================

JOBS = {
    "JOB-SWE-2025-001": {
        "title": "Senior Software Engineer",
        "department": "Engineering",
        "location": "Seattle, WA",
        "remote_allowed": True,
        "salary_range": (150000, 200000),
        "status": "open",
        "hiring_manager": "EMP-MGR-100",
        "urgency": "high",
        "description": "Build and maintain cloud-native microservices for our AI platform.",
        "requirements": {
            "must_have": ["Python", "Distributed Systems", "Cloud (Azure/AWS)", "5+ years experience"],
            "nice_to_have": ["Kubernetes", "Machine Learning", "Go", "System Design"],
        },
    },
    "JOB-PM-2025-042": {
        "title": "Product Manager - AI Platform",
        "department": "Product",
        "location": "San Francisco, CA",
        "remote_allowed": True,
        "salary_range": (140000, 180000),
        "status": "open",
        "hiring_manager": "EMP-MGR-200",
        "urgency": "medium",
        "description": "Define product strategy and roadmap for our AI developer tools.",
        "requirements": {
            "must_have": ["Product Management", "AI/ML domain knowledge", "3+ years experience"],
            "nice_to_have": ["Technical background", "B2B SaaS", "Developer tools"],
        },
    },
    "JOB-DATA-2025-015": {
        "title": "Data Engineer",
        "department": "Data",
        "location": "Austin, TX",
        "remote_allowed": False,
        "salary_range": (130000, 170000),
        "status": "open",
        "hiring_manager": "EMP-MGR-300",
        "urgency": "medium",
        "description": "Design and build data pipelines for large-scale ML training datasets.",
        "requirements": {
            "must_have": ["Python", "SQL", "Spark/Databricks", "3+ years experience"],
            "nice_to_have": ["Azure Data Factory", "dbt", "Airflow"],
        },
    },
}

EXTERNAL_CANDIDATES = {
    "CAND-EXT-1001": {
        "name": "Alice Zhang",
        "email": "alice.zhang@email.com",
        "skills": ["Python", "Distributed Systems", "Kubernetes", "Azure", "Machine Learning"],
        "years_experience": 7,
        "education": "MS Computer Science, Stanford",
        "current_company": "TechCorp",
        "current_title": "Software Engineer II",
        "location": "Seattle, WA",
        "visa_required": False,
        "salary_expectation": 185000,
        "applied_jobs": ["JOB-SWE-2025-001"],
    },
    "CAND-EXT-1002": {
        "name": "Bob Patel",
        "email": "bob.patel@email.com",
        "skills": ["Python", "Cloud (Azure/AWS)", "Go", "System Design", "CI/CD"],
        "years_experience": 9,
        "education": "BS Computer Engineering, MIT",
        "current_company": "CloudScale Inc",
        "current_title": "Senior Backend Engineer",
        "location": "San Francisco, CA",
        "visa_required": False,
        "salary_expectation": 195000,
        "applied_jobs": ["JOB-SWE-2025-001"],
    },
    "CAND-EXT-1003": {
        "name": "Clara Kim",
        "email": "clara.kim@email.com",
        "skills": ["Python", "Distributed Systems", "Azure", "Microservices"],
        "years_experience": 5,
        "education": "MS Software Engineering, Carnegie Mellon",
        "current_company": "DataFlow",
        "current_title": "Software Engineer",
        "location": "Remote",
        "visa_required": True,
        "salary_expectation": 165000,
        "applied_jobs": ["JOB-SWE-2025-001"],
    },
    "CAND-EXT-1004": {
        "name": "Daniel Okafor",
        "email": "daniel.okafor@email.com",
        "skills": ["Java", "Python", "AWS", "Kafka", "Spark"],
        "years_experience": 6,
        "education": "BS Computer Science, Georgia Tech",
        "current_company": "StreamTech",
        "current_title": "Platform Engineer",
        "location": "Austin, TX",
        "visa_required": False,
        "salary_expectation": 170000,
        "applied_jobs": ["JOB-SWE-2025-001", "JOB-DATA-2025-015"],
    },
    "CAND-EXT-1005": {
        "name": "Eva Martinez",
        "email": "eva.martinez@email.com",
        "skills": ["Python", "SQL", "Spark/Databricks", "Azure Data Factory", "dbt"],
        "years_experience": 4,
        "education": "MS Data Science, UT Austin",
        "current_company": "DataWorks",
        "current_title": "Data Engineer",
        "location": "Austin, TX",
        "visa_required": False,
        "salary_expectation": 155000,
        "applied_jobs": ["JOB-DATA-2025-015"],
    },
}

INTERNAL_CANDIDATES = {
    "CAND-INT-2001": {
        "name": "Frank Liu",
        "employee_id": "EMP-4001",
        "skills": ["Python", "Azure", "Distributed Systems", "Machine Learning", "Kubernetes"],
        "years_experience": 8,
        "education": "PhD Computer Science, UC Berkeley",
        "current_title": "Software Engineer II",
        "department": "ML Platform",
        "location": "Seattle, WA",
        "tenure_years": 3.5,
        "performance_rating": 4.2,
        "transfer_eligible": True,
        "on_pip": False,
        "applied_jobs": ["JOB-SWE-2025-001"],
    },
    "CAND-INT-2002": {
        "name": "Grace Thompson",
        "employee_id": "EMP-4002",
        "skills": ["Python", "SQL", "Cloud (Azure/AWS)", "System Design"],
        "years_experience": 5,
        "education": "MS Computer Science, University of Washington",
        "current_title": "Software Engineer",
        "department": "Backend Services",
        "location": "Seattle, WA",
        "tenure_years": 2.0,
        "performance_rating": 3.8,
        "transfer_eligible": True,
        "on_pip": False,
        "applied_jobs": ["JOB-SWE-2025-001"],
    },
}

CALENDAR_SLOTS = {
    "EMP-MGR-100": [
        {"date": "2025-03-10", "time": "10:00 AM", "available": True},
        {"date": "2025-03-10", "time": "2:00 PM", "available": True},
        {"date": "2025-03-11", "time": "9:00 AM", "available": False},
        {"date": "2025-03-11", "time": "3:00 PM", "available": True},
        {"date": "2025-03-12", "time": "11:00 AM", "available": True},
    ],
}

# Track booked interviews
_booked_interviews = []


def _to_structured_string(payload: object) -> str:
    """Render tool output as a deterministic dict-like string."""
    return pformat(payload, width=100, sort_dicts=False)


# ============================================================================
# Job Requisition Tools
# ============================================================================


@tool(
    name="get_job_details",
    description="Retrieves detailed information about a job posting including title, department, requirements, salary range, and hiring manager.",
    approval_mode="never_require",
)
def get_job_details(
    job_id: Annotated[str, "The job ID to retrieve (e.g., JOB-SWE-2025-001)"],
) -> str:
    """Get job posting details."""
    job = JOBS.get(job_id)
    if not job:
        raise ValueError(f"Job ID '{job_id}' not found in the system.")

    if job["status"] != "open":
        raise ValueError(f"Job '{job_id}' is not open. Current status: {job['status']}")

    return _to_structured_string(
        {
            "status": "ok",
            "job": {
                "job_id": job_id,
                "title": job["title"],
                "department": job["department"],
                "location": job["location"],
                "remote_allowed": job["remote_allowed"],
                "salary_range": {
                    "min": job["salary_range"][0],
                    "max": job["salary_range"][1],
                },
                "hiring_manager": job["hiring_manager"],
                "status": job["status"],
                "urgency": job["urgency"],
                "description": job["description"],
                "requirements": {
                    "must_have": list(job["requirements"]["must_have"]),
                    "nice_to_have": list(job["requirements"]["nice_to_have"]),
                },
            },
        }
    )


@tool(
    name="extract_requirements",
    description="Extracts structured requirements from a job posting, separating must-have from nice-to-have skills.",
    approval_mode="never_require",
)
def extract_requirements(
    job_id: Annotated[str, "The job ID to extract requirements from"],
) -> str:
    """Extract structured requirements from job posting."""
    job = JOBS.get(job_id)
    if not job:
        raise ValueError(f"Job ID '{job_id}' not found.")

    return _to_structured_string(
        {
            "status": "ok",
            "job_id": job_id,
            "title": job["title"],
            "requirements": {
                "must_have": list(job["requirements"]["must_have"]),
                "nice_to_have": list(job["requirements"]["nice_to_have"]),
            },
            "salary_range": {
                "min": job["salary_range"][0],
                "max": job["salary_range"][1],
            },
            "location": job["location"],
            "remote_allowed": job["remote_allowed"],
        },
    )


# ============================================================================
# Candidate Sourcing Tools
# ============================================================================


@tool(
    name="query_external_candidates",
    description="Queries the external candidate database (job board applicants) for candidates who applied to a specific job.",
    approval_mode="never_require",
)
def query_external_candidates(
    job_id: Annotated[str, "The job ID to find candidates for"],
    min_experience: Annotated[int, "Minimum years of experience required"] = 0,
) -> str:
    """Query external candidates from job boards."""
    candidates = [
        (candidate_id, candidate)
        for candidate_id, candidate in EXTERNAL_CANDIDATES.items()
        if job_id in candidate["applied_jobs"] and candidate["years_experience"] >= min_experience
    ]
    if not candidates:
        return _to_structured_string(
            {
                "status": "ok",
                "job_id": job_id,
                "candidate_count": 0,
                "candidates": [],
            }
        )

    result_candidates = []
    for candidate_id, c in candidates:
        result_candidates.append(
            {
                "candidate_id": candidate_id,
                "name": c["name"],
                "years_experience": c["years_experience"],
                "location": c["location"],
                "visa_required": c["visa_required"],
                "skills": list(c["skills"]),
                "current_title": c["current_title"],
                "current_company": c["current_company"],
                "salary_expectation": c["salary_expectation"],
            }
        )
    return _to_structured_string(
        {
            "status": "ok",
            "job_id": job_id,
            "candidate_count": len(result_candidates),
            "candidates": result_candidates,
        }
    )


@tool(
    name="query_internal_employees",
    description="Queries the internal HRIS system for current employees interested in a job opening.",
    approval_mode="never_require",
)
def query_internal_employees(
    job_id: Annotated[str, "The job ID to find internal candidates for"],
    eligible_only: Annotated[bool, "Only return transfer-eligible employees"] = True,
) -> str:
    """Query internal employees for mobility."""
    candidates = [
        (candidate_id, candidate)
        for candidate_id, candidate in INTERNAL_CANDIDATES.items()
        if job_id in candidate["applied_jobs"]
    ]
    if eligible_only:
        candidates = [(candidate_id, c) for candidate_id, c in candidates if c["transfer_eligible"]]

    if not candidates:
        return _to_structured_string(
            {
                "status": "ok",
                "job_id": job_id,
                "candidate_count": 0,
                "candidates": [],
            }
        )

    result_candidates = []
    for candidate_id, c in candidates:
        result_candidates.append(
            {
                "candidate_id": candidate_id,
                "employee_id": c["employee_id"],
                "name": c["name"],
                "current_title": c["current_title"],
                "department": c["department"],
                "tenure_years": c["tenure_years"],
                "performance_rating": c["performance_rating"],
                "transfer_eligible": c["transfer_eligible"],
                "skills": list(c["skills"]),
            }
        )
    return _to_structured_string(
        {
            "status": "ok",
            "job_id": job_id,
            "eligible_only": eligible_only,
            "candidate_count": len(result_candidates),
            "candidates": result_candidates,
        }
    )


# ============================================================================
# Evaluation Tools
# ============================================================================


@tool(
    name="score_candidate",
    description="Scores a candidate against job requirements. Returns a score from 0-100.",
    approval_mode="never_require",
)
def score_candidate(
    candidate_id: Annotated[str, "The candidate ID to score"],
    job_id: Annotated[str, "The job ID to score against"],
) -> str:
    """Score a candidate against job requirements."""
    job = JOBS.get(job_id)
    if not job:
        raise ValueError(f"Job '{job_id}' not found.")

    # Look up candidate
    candidate = EXTERNAL_CANDIDATES.get(candidate_id) or INTERNAL_CANDIDATES.get(candidate_id)
    if not candidate:
        raise ValueError(f"candidate_id '{candidate_id}' was not found.")

    # Simple scoring
    must_have = job["requirements"]["must_have"]
    nice_to_have = job["requirements"]["nice_to_have"]
    skills_lower = [s.lower() for s in candidate["skills"]]

    must_matches = sum(1 for r in must_have if any(r.lower() in s for s in skills_lower))
    nice_matches = sum(1 for r in nice_to_have if any(r.lower() in s for s in skills_lower))

    score = int((must_matches / max(len(must_have), 1)) * 70 + (nice_matches / max(len(nice_to_have), 1)) * 30)
    score = min(100, score + min(candidate["years_experience"], 10))

    must_matched = [r for r in must_have if any(r.lower() in s for s in skills_lower)]
    must_gaps = [r for r in must_have if not any(r.lower() in s for s in skills_lower)]

    return _to_structured_string(
        {
            "status": "ok",
            "candidate_id": candidate_id,
            "candidate_name": candidate["name"],
            "job_id": job_id,
            "overall_score": score,
            "must_have_matches": must_matched,
            "must_have_gaps": must_gaps,
            "nice_to_have_match_count": nice_matches,
            "nice_to_have_total": len(nice_to_have),
            "years_experience": candidate["years_experience"],
            "salary_expectation": candidate.get("salary_expectation"),
            "job_salary_range": {
                "min": job["salary_range"][0],
                "max": job["salary_range"][1],
            },
        },
    )


@tool(
    name="rank_candidates",
    description="Ranks a list of scored candidates and produces a shortlist.",
    approval_mode="never_require",
)
def rank_candidates(
    candidate_ids: Annotated[str, "Comma-separated candidate IDs to rank"],
    job_id: Annotated[str, "The job ID candidates are being ranked for"],
) -> str:
    """Rank candidates and produce shortlist."""
    if isinstance(candidate_ids, list):
        ids = [str(candidate_id).strip() for candidate_id in candidate_ids if str(candidate_id).strip()]
    else:
        ids = [candidate_id.strip() for candidate_id in str(candidate_ids).split(",") if candidate_id.strip()]

    job = JOBS.get(job_id)
    if not job:
        raise ValueError(f"Job '{job_id}' not found.")

    scored = []
    missing_candidate_ids = []
    for cid in ids:
        cand = EXTERNAL_CANDIDATES.get(cid) or INTERNAL_CANDIDATES.get(cid)
        if not cand:
            missing_candidate_ids.append(cid)
            continue
        skills_lower = [s.lower() for s in cand["skills"]]
        must_have = job["requirements"]["must_have"]
        nice_to_have = job["requirements"]["nice_to_have"]
        must_matches = sum(1 for r in must_have if any(r.lower() in s for s in skills_lower))
        nice_matches = sum(1 for r in nice_to_have if any(r.lower() in s for s in skills_lower))
        score = int((must_matches / max(len(must_have), 1)) * 70 + (nice_matches / max(len(nice_to_have), 1)) * 30)
        score = min(100, score + min(cand["years_experience"], 10))
        scored.append((cid, cand["name"], score))

    if missing_candidate_ids:
        if len(missing_candidate_ids) == 1:
            raise ValueError(f"candidate_id '{missing_candidate_ids[0]}' was not found.")
        missing = ", ".join(missing_candidate_ids)
        raise ValueError(f"candidate_id values were not found: {missing}")

    scored.sort(key=lambda x: x[2], reverse=True)

    ranked_candidates = []
    for rank, (cid, name, score) in enumerate(scored, 1):
        ranked_candidates.append(
            {
                "rank": rank,
                "candidate_id": cid,
                "candidate_name": name,
                "score": score,
            }
        )

    return _to_structured_string(
        {
            "status": "ok",
            "job_id": job_id,
            "ranked_candidates": ranked_candidates,
            "recommended_shortlist_candidate_ids": [s[0] for s in scored[:3]],
        }
    )


# ============================================================================
# Compliance Tools
# ============================================================================


@tool(
    name="check_compliance",
    description="Checks a shortlist for EEOC compliance and adverse impact using the 4/5ths rule.",
    approval_mode="never_require",
)
def check_compliance(
    candidate_ids: Annotated[str, "Comma-separated candidate IDs in the shortlist"],
    job_id: Annotated[str, "The job ID the shortlist is for"],
) -> str:
    """Check shortlist for compliance."""
    ids = [c.strip() for c in candidate_ids.split(",")]
    return _to_structured_string(
        {
            "status": "ok",
            "job_id": job_id,
            "shortlist_candidate_ids": ids,
            "shortlist_size": len(ids),
            "eeoc_status": "PASS",
            "adverse_impact": "No adverse impact detected (4/5ths rule satisfied)",
            "demographic_distribution": "Diverse candidate pool",
            "recommendation": "Shortlist is compliant — proceed to interviews.",
        }
    )


@tool(
    name="detect_bias",
    description="Analyzes the selection process for potential bias patterns.",
    approval_mode="never_require",
)
def detect_bias(
    candidate_ids: Annotated[str, "Comma-separated candidate IDs that were selected"],
    job_id: Annotated[str, "The job ID"],
) -> str:
    """Detect potential bias in selection."""
    ids = [c.strip() for c in candidate_ids.split(",") if c.strip()]
    return _to_structured_string(
        {
            "status": "ok",
            "job_id": job_id,
            "selected_candidate_ids": ids,
            "selection_criteria_analysis": "All criteria are job-related",
            "geographic_bias": "Not detected",
            "experience_bias": "Not detected (range 4-9 years in pool)",
            "education_bias": "Not detected (mix of BS/MS/PhD)",
            "overall_risk": "LOW",
            "recommendation": "No corrective action needed.",
        }
    )


# ============================================================================
# Scheduling Tools
# ============================================================================


@tool(
    name="get_calendar_availability",
    description="Checks calendar availability for the hiring manager.",
    approval_mode="never_require",
)
def get_calendar_availability(
    hiring_manager_id: Annotated[str, "The hiring manager's employee ID"],
) -> str:
    """Get calendar availability."""
    slots = CALENDAR_SLOTS.get(hiring_manager_id)
    if not slots:
        raise ValueError(f"No calendar data found for manager {hiring_manager_id}.")

    available = [s for s in slots if s["available"]]
    if not available:
        raise ValueError(f"No available slots found for manager {hiring_manager_id}.")

    return _to_structured_string(
        {
            "status": "ok",
            "hiring_manager_id": hiring_manager_id,
            "available_slots": available,
        }
    )


@tool(
    name="book_interview",
    description="Books an interview slot for a candidate with the hiring manager.",
    approval_mode="never_require",
)
def book_interview(
    candidate_id: Annotated[str, "The candidate ID"],
    hiring_manager_id: Annotated[str, "The hiring manager's employee ID"],
    date: Annotated[str, "Interview date (YYYY-MM-DD)"],
    time: Annotated[str, "Interview time (e.g., '10:00 AM')"],
) -> str:
    """Book an interview slot."""
    cand = EXTERNAL_CANDIDATES.get(candidate_id) or INTERNAL_CANDIDATES.get(candidate_id)
    if not cand:
        raise ValueError(f"candidate_id '{candidate_id}' was not found.")
    name = cand["name"]

    _booked_interviews.append(
        {
            "candidate_id": candidate_id,
            "manager": hiring_manager_id,
            "date": date,
            "time": time,
        }
    )

    return _to_structured_string(
        {
            "status": "ok",
            "booking": {
                "candidate_id": candidate_id,
                "candidate_name": name,
                "hiring_manager_id": hiring_manager_id,
                "date": date,
                "time": time,
                "format": "Video Conference",
                "confirmation": "Sent to all participants.",
            },
        },
    )
