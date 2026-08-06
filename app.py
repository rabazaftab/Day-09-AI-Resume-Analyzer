import json
import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field


load_dotenv()


app = FastAPI(
    title="AI Resume Analyzer",
    description="AI-powered resume and job description analyzer",
    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


templates = Jinja2Templates(
    directory="templates"
)


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)


OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


MODEL = "openai/gpt-4.1-mini"


class ResumeRequest(BaseModel):

    resume: str = Field(
        min_length=50,
        max_length=10000
    )

    job_description: str = Field(
        min_length=20,
        max_length=10000
    )


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/analyze")
async def analyze_resume(
    data: ResumeRequest
):

    if not OPENROUTER_API_KEY:

        return JSONResponse(
            status_code=500,
            content={
                "error":
                "OpenRouter API key is not configured."
            }
        )


    prompt = f"""
You are an expert ATS resume analyzer and career advisor.

Analyze the candidate's resume against the job description.

Return ONLY valid JSON.

Do not use Markdown.
Do not use code blocks.
Do not add explanations outside the JSON.

The JSON MUST contain exactly these fields:

{{
    "match_score": 0,
    "summary": "",
    "strengths": [],
    "missing_skills": [],
    "suggestions": []
}}

Rules:

1. match_score must be an integer from 0 to 100.
2. summary must be a concise explanation.
3. strengths must contain relevant skills or qualifications
   found in the resume.
4. missing_skills must contain important skills from the job
   description that are missing or weak in the resume.
5. suggestions must contain practical resume improvement tips.
6. Do not invent experience or qualifications.
7. Keep each list concise.
8. Use plain text strings.

Resume:

{data.resume}


Job Description:

{data.job_description}
"""


    payload = {

        "model": MODEL,

        "messages": [

            {
                "role": "user",
                "content": prompt
            }

        ],

        "temperature": 0.2,

        "max_tokens": 800

    }


    headers = {

        "Authorization":
        f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
        "application/json"

    }


    try:

        response = requests.post(

            OPENROUTER_URL,

            headers=headers,

            json=payload,

            timeout=60

        )


        if response.status_code != 200:

            return JSONResponse(

                status_code=500,

                content={

                    "error":
                    "OpenRouter request failed.",

                    "details":
                    response.text

                }

            )


        result = response.json()


        content = (
            result["choices"][0]
            ["message"]["content"]
        )


        content = content.strip()


        # Remove accidental Markdown fences

        if content.startswith("```"):

            content = content.replace(
                "```json",
                ""
            )

            content = content.replace(
                "```",
                ""
            )

            content = content.strip()


        analysis = json.loads(content)


        required_fields = {

            "match_score",
            "summary",
            "strengths",
            "missing_skills",
            "suggestions"

        }


        if not required_fields.issubset(
            analysis.keys()
        ):

            raise ValueError(
                "Invalid AI response structure."
            )


        # Validate score

        score = int(
            analysis["match_score"]
        )


        if score < 0 or score > 100:

            raise ValueError(
                "Match score must be between 0 and 100."
            )


        return {

            "match_score": score,

            "summary":
                str(analysis["summary"]),

            "strengths":
                analysis["strengths"],

            "missing_skills":
                analysis["missing_skills"],

            "suggestions":
                analysis["suggestions"]

        }


    except json.JSONDecodeError:

        return JSONResponse(

            status_code=500,

            content={

                "error":
                "The AI returned invalid JSON."

            }

        )


    except requests.RequestException:

        return JSONResponse(

            status_code=500,

            content={

                "error":
                "Unable to connect to OpenRouter."

            }

        )


    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "error":
                f"Unexpected error: {str(error)}"

            }

        )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )