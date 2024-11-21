import asyncio
import os
import tempfile
from textwrap import dedent

from pydantic import BaseModel

from app.models import RepoMap
from app.services.local_repo_service import (
    get_relative_markdown_file_path_list,
)


class ValeFileAnalysis(BaseModel):
    path: str
    issues: list[str]


class ValeAnalysisResult(BaseModel):
    analysis: list[ValeFileAnalysis]
    score_components: dict[str, int]
    total_score: int


def setup_vale_ini_file() -> str:
    vale_ini_file_path = os.path.join(tempfile.gettempdir(), "vale.ini")
    if not os.path.exists(vale_ini_file_path):
        with open(vale_ini_file_path, "w") as f:
            f.write(
                dedent(
                    '''
Packages = write-good

[*.md]
BasedOnStyles = write-good
                    '''
                    )
                )

    return vale_ini_file_path


async def analyze_vale(
    *, local_repo_path: str, repo_map: RepoMap
) -> ValeAnalysisResult:
    vale_ini_file_path = setup_vale_ini_file()

    absolute_file_path_list = get_absolute_markdown_file_path_list(
        local_repo_path=local_repo_path
    )

    # for each file, analyze the style
    analysis = await asyncio.gather(
        *(
            analyze_file_vale(
                absolute_file_path=absolute_file_path,
                vale_ini_file_path=vale_ini_file_path,
            )
            for absolute_file_path in absolute_file_path_list
        )
    )

    score_components = score_components_vale(analysis=analysis)
    total_score = round(sum(score_components.values()) / len(score_components))

    return ValeAnalysisResult(
        analysis=analysis, score_components=score_components, total_score=total_score
    )


async def analyze_file_vale(
    *, absolute_file_path: str, vale_ini_file_path: str
) -> ValeFileAnalysis:
    process = await asyncio.create_subprocess_exec(
        "vale",
        "--config",
        vale_ini_file_path,
        "--output",
        "JSON",
        absolute_file_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        # Vale returns non-zero when it finds issues, which is expected
        # Only raise if we got no output
        if not stdout:
            raise RuntimeError(f"Vale failed: {stderr.decode()}")
    
    # Vale outputs one issue per line in JSON format
    issues = [
        line.strip() for line in stdout.decode().splitlines() 
        if line.strip()  # Filter out empty lines
    ]
    
    return ValeFileAnalysis(
        path=absolute_file_path,
        issues=issues
    )

def score_components_vale(*, analysis: list[ValeFileAnalysis]) -> dict[str, int]:
    pass
