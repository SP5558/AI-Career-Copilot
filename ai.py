import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ================= ENV CONFIG =================

env_path = Path(__file__).resolve().parent / ".env"

load_dotenv(
    dotenv_path=env_path,
    override=True
)

groq_api_key = os.getenv("GROQ_API_KEY", "").strip()

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Add it to your .env file."
    )


client = Groq(
    api_key=groq_api_key
)


# ================= DEFAULT RESULT =================

def _empty_result(error_message=None):

    result = {
        "ats_score": 0,
        "job_match": None,
        "resume_summary": "",
        "matching_skills": [],
        "skills": [],
        "missing_skills": [],
        "strengths": [],
        "weaknesses": [],
        "suggestions": [],
        "project_suggestions": [],
        "roadmap": [],
        "interview_questions": []
    }

    if error_message:
        result["error"] = error_message

    return result


# ================= HELPER FUNCTIONS =================

def _clean_text(text):

    return re.sub(
        r"\s+",
        " ",
        text or ""
    ).strip()


def _extract_json(content):

    if not content:
        raise ValueError("AI returned an empty response.")

    content = content.strip()

    # Remove possible markdown code fences
    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "AI did not return valid JSON."
            )

        json_text = content[start:end + 1]

        return json.loads(json_text)


def _normalize_result(data, has_job_description):

    if not isinstance(data, dict):
        raise ValueError(
            "AI response format is invalid."
        )

    result = _empty_result()

    try:
        ats_score = int(
            float(data.get("ats_score", 0))
        )
    except (TypeError, ValueError):
        ats_score = 0

    result["ats_score"] = max(
        0,
        min(100, ats_score)
    )

    if has_job_description:

        try:
            job_match = int(
                float(data.get("job_match", 0))
            )
        except (TypeError, ValueError):
            job_match = 0

        result["job_match"] = max(
            0,
            min(100, job_match)
        )

    else:
        result["job_match"] = None

    result["resume_summary"] = str(
        data.get("resume_summary", "")
    ).strip()

    list_fields = [
        "matching_skills",
        "missing_skills",
        "strengths",
        "weaknesses",
        "suggestions",
        "project_suggestions",
        "roadmap",
        "interview_questions"
    ]

    for field in list_fields:

        value = data.get(field, [])

        if isinstance(value, list):

            result[field] = [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]

        elif value:

            result[field] = [
                str(value).strip()
            ]

    # Old dashboard/history compatibility
    result["skills"] = result["matching_skills"]

    return result


# ================= AI RESUME ANALYSIS =================

def analyse_resume(
    resume_text,
    user_goal,
    job_description=""
):

    resume_text = _clean_text(resume_text)
    user_goal = _clean_text(user_goal)
    job_description = _clean_text(job_description)

    if not resume_text:
        return _empty_result(
            "Resume text is empty or could not be extracted."
        )

    if not user_goal:
        return _empty_result(
            "Please enter a target role."
        )

    has_job_description = bool(job_description)

    if has_job_description:

        analysis_instruction = """
A job description has been provided.

Compare the resume directly with the job description and target role.

The ATS score must reflect:
- Skill and keyword relevance
- Experience relevance
- Project relevance
- Education relevance
- Resume structure and readability
- Measurable achievements
- Job-description alignment

The job_match score must represent how closely the candidate matches
the supplied job description.

Matching skills must include only skills supported by the resume.
Missing skills must include important requirements from the job
description that are absent or not clearly demonstrated in the resume.
"""

        jd_section = f"""
JOB DESCRIPTION:
{job_description}
"""

    else:

        analysis_instruction = """
No job description has been provided.

Perform a general ATS and resume-quality analysis for the target role.

The ATS score must reflect:
- Target-role keyword relevance
- Relevant technical and professional skills
- Education
- Experience or internships
- Projects
- Resume structure and readability
- Action verbs
- Measurable achievements
- Contact and profile sections

Set job_match to null.

Identify matching skills actually present in the resume.
Identify missing or underrepresented skills commonly important for
the target role, but do not use a fixed list for every candidate.
"""

        jd_section = """
JOB DESCRIPTION:
Not provided.
"""

    prompt = f"""
You are a senior ATS specialist, career coach and technical recruiter.

Analyse the candidate's resume professionally.

TARGET ROLE:
{user_goal}

RESUME:
{resume_text}

{jd_section}

ANALYSIS INSTRUCTIONS:
{analysis_instruction}

Important rules:

1. Analyse the actual resume content.
2. Do not assume the candidate has a skill unless it is visible in the resume.
3. Do not give the same generic answer for every role.
4. Tailor all results to the target role and, when provided, the job description.
5. ATS score and job-match score must be realistic and evidence-based.
6. Do not invent experience, projects, education, achievements or certifications.
7. Keep every suggestion practical and concise.
8. Project suggestions must be relevant to the target role.
9. Interview questions must be relevant to the resume, target role and job description.
10. The roadmap must prioritize the most important gaps.
11. Return only valid JSON.
12. Do not include markdown, explanations or code fences.

Return exactly this JSON structure:

{{
    "ats_score": 0,
    "job_match": null,
    "resume_summary": "",
    "matching_skills": [],
    "missing_skills": [],
    "strengths": [],
    "weaknesses": [],
    "suggestions": [],
    "project_suggestions": [],
    "roadmap": [],
    "interview_questions": []
}}

Output requirements:

- ats_score: integer from 0 to 100
- job_match: integer from 0 to 100 when JD is provided, otherwise null
- resume_summary: 3 to 5 concise sentences
- matching_skills: 5 to 12 items when evidence exists
- missing_skills: up to 10 important gaps
- strengths: 3 to 6 items
- weaknesses: 3 to 6 items
- suggestions: 5 to 8 actionable resume improvements
- project_suggestions: 2 to 4 role-relevant projects
- roadmap: 5 to 8 ordered learning steps
- interview_questions: 6 to 10 relevant questions
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            temperature=0.2,

            max_tokens=2200,

            response_format={
                "type": "json_object"
            },

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You are an expert ATS resume reviewer and "
                        "technical recruiter. Return only valid JSON."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]
        )

        content = (
            response.choices[0]
            .message
            .content
        )

        data = _extract_json(content)

        return _normalize_result(
            data,
            has_job_description
        )

    except Exception as error:

        print(
            "Groq Analysis Error:",
            repr(error)
        )

        return _empty_result(
            f"AI analysis failed: {str(error)}"
        )