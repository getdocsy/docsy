import asyncio
import json
import logging
import os
import tempfile
from textwrap import dedent
import time

from pydantic import BaseModel

from app.models import RepoMap
from app.services.repo_map_service import get_absolute_file_path_list


class ValeAction(BaseModel):
    Name: str
    Params: None | dict | list


class ValeIssue(BaseModel):
    Action: ValeAction
    Span: list[int]
    Check: str
    Description: str
    Link: str
    Message: str
    Severity: str
    Match: str
    Line: int


class ValeFileAnalysis(BaseModel):
    path: str
    issues: list[ValeIssue]


class ValeAnalysisResult(BaseModel):
    analysis: list[ValeFileAnalysis]
    score_components: dict[str, int]
    total_score: int


async def setup_vale_ini_file() -> str:
    vale_ini_file_path = os.path.join(tempfile.gettempdir(), "vale.ini")
    if not os.path.exists(vale_ini_file_path):
        with open(vale_ini_file_path, "w") as f:
            f.write(
                dedent(
                    """
Packages = write-good

[*.md]
BasedOnStyles = write-good
                    """
                )
            )
        
        # Run vale sync to install required packages
        process = await asyncio.create_subprocess_exec(
            "vale",
            "sync",
            "--config",
            vale_ini_file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Vale sync failed: {stderr.decode()}")

    return vale_ini_file_path

# Analyze a patch of a single file
async def analyze_patch_vale(*, patch: str) -> str:
    vale_ini_file_path = await setup_vale_ini_file()
    vale_patch_file_path = os.path.join(tempfile.gettempdir(), "vale_patch.md")

    # Write patch to file
    with open(vale_patch_file_path, "w") as f:
        f.write(patch)

    # Run vale
    process = await asyncio.create_subprocess_exec(
        "vale",
        "--output",
        "JSON",
        "--config",
        vale_ini_file_path,
        vale_patch_file_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"Vale failed: {stderr.decode()}")

    return stdout.decode()


async def analyze_vale(
    *, local_repo_path: str, repo_map: RepoMap
) -> ValeAnalysisResult:
    start_time = time.time()
    vale_ini_file_path = await setup_vale_ini_file()

    absolute_file_path_list = get_absolute_file_path_list(
        repo_map=repo_map,
        local_repo_path=local_repo_path
    )

    # for each file, analyze the style
    analysis = await asyncio.gather(
        *(
            analyze_file_vale(
                absolute_file_path=absolute_file_path,
                vale_ini_file_path=vale_ini_file_path,
                local_repo_path=local_repo_path,
            )
            for absolute_file_path in absolute_file_path_list
        )
    )

    score_components = score_components_vale(analysis=analysis)
    total_score = round(sum(score_components.values()) / len(score_components))

    elapsed_time = time.time() - start_time
    logging.info(f"Vale analysis completed in {elapsed_time:.2f} seconds")

    return ValeAnalysisResult(
        analysis=analysis, score_components=score_components, total_score=total_score
    )


async def analyze_file_vale(
    *, absolute_file_path: str, vale_ini_file_path: str, local_repo_path: str
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

    # Vale outputs formatted JSON, so we need to parse it
    output_dict = json.loads(stdout.decode())
    
    # When there are no issues, Vale returns an empty dict
    if not output_dict:
        return ValeFileAnalysis(
            path=os.path.relpath(absolute_file_path, local_repo_path),
            issues=[]
        )

    # The output is a dict where the key is the file path and value is list of issues
    file_path = list(output_dict.keys())[0]  # Get the first (and only) key
    issues = output_dict[file_path]  # Get the issues for that file

    return ValeFileAnalysis(
        path=os.path.relpath(file_path, local_repo_path),
        issues=issues
    )


def score_components_vale(*, analysis: list[ValeFileAnalysis]) -> dict[str, int]:
    score_components = {}
    for file in analysis:
        score = max(100 - len(file.issues) * 2, 0)
        score_components[f"{file.path} has {len(file.issues)} issues"] = score

    return score_components
