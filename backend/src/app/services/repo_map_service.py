import os
from pathlib import Path
from pydantic import BaseModel
import asyncio
from app.models import Repo, RepoMap
from app.services import local_repo_service


class FileMap(BaseModel):
    relative_path: str
    headings: list[str]
    title: str | None = None
    description: str | None = None
    line_number_in_sidebar: int | None = None


# The RepoMap is used to store structured information about a repo files without AI analysis.
class RepoMapResult(BaseModel):
    documentation_files: list[FileMap]
    sidebars_file_path: str | None = None
    created_for_commit_sha: str | None = None


def get_relative_file_path_to_headings(*, repo_map: RepoMap) -> dict:
    return {file.relative_path: file.headings for file in repo_map.documentation_files}


def get_absolute_file_path_list(
    *, repo_map: RepoMap, local_repo_path: str
) -> list[str]:
    return [
        os.path.join(local_repo_path, file.relative_path)
        for file in repo_map.documentation_files
    ]


def get_title(*, frontmatter_dict: dict, headings: list[str]) -> str:
    if "title" in frontmatter_dict:
        return frontmatter_dict["title"]
    if headings:
        # we assume the first heading is the title
        return headings[0].lstrip("#").strip()
    return None


def get_description(*, frontmatter_dict: dict) -> str | None:
    if "description" in frontmatter_dict:
        return frontmatter_dict["description"]
    return None


def get_line_number_of_file_in_sidebar(
    *,
    local_repo_path: str,
    relative_sidebars_file_path: str,
    relative_file_path: str,
    frontmatter_dict: dict
) -> int | None:

    if not relative_sidebars_file_path:
        return None

    absolute_sidebars_file_path = os.path.join(
        local_repo_path, relative_sidebars_file_path
    )

    with open(absolute_sidebars_file_path, "r") as file:
        for line_number, line in enumerate(file, start=1):
            # id
            if "id" in frontmatter_dict and frontmatter_dict["id"] in line:
                return line_number

            # filename without extension
            if os.path.splitext(os.path.basename(relative_file_path))[0] in line:
                return line_number

            # title
            if "title" in frontmatter_dict and frontmatter_dict["title"] in line:
                return line_number
    return None


async def create_repo_map(*, repo: Repo, local_repo_path: str) -> RepoMap:
    sidebars_file_path = local_repo_service.get_sidebar_file_path(
        local_repo_path=local_repo_path
    )

    # We try to find out where all relevant files are.
    # Since I don't want to use AI in the repo map creation, we try to find out where the files are by checking if the docs folder exists and has more than 3 files.
    if (
        Path(local_repo_path).joinpath("docs").exists()
        and len(
            local_repo_service.get_relative_documentation_file_path_list(
                local_repo_path=local_repo_path, filter_on_subdir="docs"
            )
        )
        > 3
    ):
        filter_on_subdir = "docs"
    elif (
        Path(local_repo_path).joinpath("documentation/docs").exists()
        and len(
            local_repo_service.get_relative_documentation_file_path_list(
                local_repo_path=local_repo_path, filter_on_subdir="documentation/docs"
            )
        )
        > 3
    ):
        filter_on_subdir = "documentation/docs"
    elif (
        Path(local_repo_path).joinpath("documentation").exists()
        and len(
            local_repo_service.get_relative_documentation_file_path_list(
                local_repo_path=local_repo_path, filter_on_subdir="documentation"
            )
        )
        > 3
    ):
        filter_on_subdir = "documentation"
    else:
        filter_on_subdir = None

    relative_file_path_list = (
        local_repo_service.get_relative_documentation_file_path_list(
            local_repo_path=local_repo_path,
            filter_on_subdir=filter_on_subdir,
        )
    )

    documentation_files = []
    for relative_file_path in relative_file_path_list:
        absolute_file_path = os.path.join(local_repo_path, relative_file_path)
        frontmatter_dict = local_repo_service.get_markdown_frontmatter(
            absolute_file_path=absolute_file_path
        )
        headings = local_repo_service.get_documentation_file_headings(
            absolute_file_path=absolute_file_path
        )
        documentation_files.append(
            FileMap(
                relative_path=relative_file_path,
                title=get_title(frontmatter_dict=frontmatter_dict, headings=headings),
                description=get_description(frontmatter_dict=frontmatter_dict),
                headings=headings,
                line_number_in_sidebar=get_line_number_of_file_in_sidebar(
                    local_repo_path=local_repo_path,
                    relative_sidebars_file_path=sidebars_file_path,
                    relative_file_path=relative_file_path,
                    frontmatter_dict=frontmatter_dict,
                ),
            )
        )

    repo_map_result = RepoMapResult(
        documentation_files=documentation_files,
        sidebars_file_path=sidebars_file_path,
    )

    await RepoMap.objects.acreate(
        repo=repo,
        result=repo_map_result.model_dump(),
        created_for_commit_sha=local_repo_service.get_commit_sha(
            local_repo_path=local_repo_path
        ),
    )

    return repo_map_result
