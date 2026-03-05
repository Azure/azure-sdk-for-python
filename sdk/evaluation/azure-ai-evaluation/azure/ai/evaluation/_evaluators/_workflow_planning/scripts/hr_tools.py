# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Mock HR data and function tools for the bug-bash notebook.

Provides a self-contained HR recruitment scenario with:
- Mock data: job postings, candidates (external + internal), calendar slots
- Function tools for job lookup, candidate sourcing, evaluation, compliance,
  scheduling, and communication
"""

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
        return f"Job ID '{job_id}' not found in the system."

    if job["status"] != "open":
        return f"Warning: Job '{job_id}' is not open. Current status: {job['status']}"

    must_have = "\n".join(f"  - {r} (Required)" for r in job["requirements"]["must_have"])
    nice_to_have = "\n".join(f"  - {r} (Preferred)" for r in job["requirements"]["nice_to_have"])

    return f"""Job Details for {job_id}:
Title: {job['title']}
Department: {job['department']}
Location: {job['location']}
Remote Allowed: {'Yes' if job['remote_allowed'] else 'No'}
Salary Range: ${job['salary_range'][0]:,} - ${job['salary_range'][1]:,}
Hiring Manager: {job['hiring_manager']}
Status: {job['status']}
Urgency: {job['urgency']}

Requirements:
{must_have}
{nice_to_have}

Description: {job['description']}"""


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

    must = ", ".join(job["requirements"]["must_have"])
    nice = ", ".join(job["requirements"]["nice_to_have"])

    return f"""Structured Requirements for {job_id} ({job['title']}):

MUST HAVE: {must}
NICE TO HAVE: {nice}
Salary Range: ${job['salary_range'][0]:,} - ${job['salary_range'][1]:,}
Location: {job['location']} {'(Remote OK)' if job['remote_allowed'] else '(On-site required)'}"""


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
        c
        for c in EXTERNAL_CANDIDATES.values()
        if job_id in c["applied_jobs"] and c["years_experience"] >= min_experience
    ]
    if not candidates:
        return f"No external candidates found for job {job_id} matching the criteria."

    lines = [f"External Candidates for {job_id} ({len(candidates)} found):"]
    for c in candidates:
        visa = " [Visa Required]" if c["visa_required"] else ""
        lines.append(
            f"\n- {[k for k, v in EXTERNAL_CANDIDATES.items() if v is c][0]}: {c['name']}\n"
            f"  Experience: {c['years_experience']} years | Location: {c['location']}{visa}\n"
            f"  Skills: {', '.join(c['skills'][:6])}\n"
            f"  Current: {c['current_title']} at {c['current_company']}\n"
            f"  Salary Expectation: ${c['salary_expectation']:,}"
        )
    return "\n".join(lines)


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
    candidates = [c for c in INTERNAL_CANDIDATES.values() if job_id in c["applied_jobs"]]
    if eligible_only:
        candidates = [c for c in candidates if c["transfer_eligible"]]

    if not candidates:
        return f"No internal candidates found for job {job_id}."

    lines = [f"Internal Candidates for {job_id} ({len(candidates)} found):"]
    for c in candidates:
        lines.append(
            f"\n- {[k for k, v in INTERNAL_CANDIDATES.items() if v is c][0]} (Employee: {c['employee_id']}): {c['name']}\n"
            f"  Current Role: {c['current_title']} ({c['department']})\n"
            f"  Tenure: {c['tenure_years']} years | Performance: {c['performance_rating']}/5.0\n"
            f"  Transfer Eligible: {'Yes' if c['transfer_eligible'] else 'No'}\n"
            f"  Skills: {', '.join(c['skills'][:6])}"
        )
    return "\n".join(lines)


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
        raise ValueError(f"Candidate '{candidate_id}' not found.")

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

    return f"""Scoring Report for {candidate_id} ({candidate['name']}) against {job_id}:
Overall Score: {score}/100
Skills Matched (Must Have): {', '.join(must_matched) or 'None'}
Skills Gaps (Must Have): {', '.join(must_gaps) or 'None'}
Nice-to-Have Matches: {nice_matches}/{len(nice_to_have)}
Experience: {candidate['years_experience']} years
Salary Expectation: ${candidate.get('salary_expectation', 0):,} (Budget: ${job['salary_range'][0]:,}-${job['salary_range'][1]:,})"""


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
    ids = [c.strip() for c in candidate_ids.split(",")]
    job = JOBS.get(job_id)
    if not job:
        raise ValueError(f"Job '{job_id}' not found.")

    scored = []
    for cid in ids:
        cand = EXTERNAL_CANDIDATES.get(cid) or INTERNAL_CANDIDATES.get(cid)
        if not cand:
            continue
        skills_lower = [s.lower() for s in cand["skills"]]
        must_have = job["requirements"]["must_have"]
        nice_to_have = job["requirements"]["nice_to_have"]
        must_matches = sum(1 for r in must_have if any(r.lower() in s for s in skills_lower))
        nice_matches = sum(1 for r in nice_to_have if any(r.lower() in s for s in skills_lower))
        score = int((must_matches / max(len(must_have), 1)) * 70 + (nice_matches / max(len(nice_to_have), 1)) * 30)
        score = min(100, score + min(cand["years_experience"], 10))
        scored.append((cid, cand["name"], score))

    scored.sort(key=lambda x: x[2], reverse=True)

    lines = [f"Candidate Ranking for {job_id} ({job['title']}):"]
    for rank, (cid, name, score) in enumerate(scored, 1):
        lines.append(f"  #{rank}: {cid} ({name}) — Score: {score}/100")

    if scored:
        lines.append(f"\nRecommended Shortlist (top 3): {', '.join(s[0] for s in scored[:3])}")
    return "\n".join(lines)


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
    return f"""Compliance Report for {job_id}:
Shortlist Size: {len(ids)} candidates
EEOC Status: PASS
Adverse Impact Analysis: No adverse impact detected (4/5ths rule satisfied)
Demographic Distribution: Diverse candidate pool
Recommendation: Shortlist is compliant — proceed to interviews."""


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
    return f"""Bias Detection Report for {job_id}:
Selection Criteria Analysis: All criteria are job-related
Geographic Bias: Not detected
Experience Bias: Not detected (range 4-9 years in pool)
Education Bias: Not detected (mix of BS/MS/PhD)
Overall Risk: LOW
Recommendation: No corrective action needed."""


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
        return f"No calendar data found for manager {hiring_manager_id}."

    available = [s for s in slots if s["available"]]
    if not available:
        return f"No available slots found for manager {hiring_manager_id}."

    lines = [f"Available Interview Slots for {hiring_manager_id}:"]
    for s in available:
        lines.append(f"  - {s['date']} at {s['time']}")
    return "\n".join(lines)


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
    name = cand["name"] if cand else candidate_id

    _booked_interviews.append(
        {
            "candidate_id": candidate_id,
            "manager": hiring_manager_id,
            "date": date,
            "time": time,
        }
    )

    return f"""Interview Booked:
Candidate: {name} ({candidate_id})
Hiring Manager: {hiring_manager_id}
Date: {date} at {time}
Format: Video Conference (Teams link will be sent)
Confirmation: Sent to all participants."""
