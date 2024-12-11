import logging
import os
from pathlib import Path

import frontmatter

from docutils import frontend, utils, nodes
from docutils.parsers.rst import Parser

from app.models import Repo
import tempfile
import git
import shutil
from contextlib import contextmanager


@contextmanager
def temp_clone_repo(*, repo: Repo):
    temp_local_repo_path = tempfile.mkdtemp()
    logging.info(f"Cloning repo {repo.nfkc_github_full_name}")
    try:
        git.Repo.clone_from(repo.nfkc_clone_url, temp_local_repo_path, depth=1)
        logging.info(f"Cloned repo {repo.nfkc_github_full_name}")
        yield temp_local_repo_path
    finally:
        shutil.rmtree(temp_local_repo_path, ignore_errors=True)


def get_commit_sha(*, local_repo_path: str) -> str:
    repo = git.Repo(local_repo_path)
    return repo.head.commit.hexsha


def get_file_content(*, local_repo_path: str, relative_file_path: str) -> str:
    absolute_file_path = os.path.join(local_repo_path, relative_file_path)
    with open(absolute_file_path, "r", encoding="utf-8") as file:
        return file.read()


def get_file_content_with_line_numbers(
    *, local_repo_path: str, relative_file_path: str
) -> str:
    absolute_file_path = os.path.join(local_repo_path, relative_file_path)
    with open(absolute_file_path, "r", encoding="utf-8") as file:
        return "\n".join([f"{i}| {line}" for i, line in enumerate(file, start=1)])


def get_relative_markdown_file_path_to_headings(
    *, local_repo_path: str, filter_on_subdir: str | None = None
) -> dict:
    if filter_on_subdir:
        path = Path(local_repo_path).joinpath(filter_on_subdir)
    else:
        path = Path(local_repo_path)

    relative_file_path_to_headings = {}
    for pattern in ["*.md", "*.rst"]:
        for absolute_file_path in path.rglob(pattern):
            relative_file_path_to_headings[
                os.path.relpath(absolute_file_path, local_repo_path)
            ] = get_documentation_file_headings(absolute_file_path=absolute_file_path)


def get_sidebar_file_path(*, local_repo_path: str) -> str | None:
    for file_path in Path(local_repo_path).glob("*sidebars.*"):
        return os.path.relpath(file_path, local_repo_path)
    return None


# only supports .md and .rst
def get_relative_documentation_file_path_list(
    *, local_repo_path: str, filter_on_subdir: str | None = None
) -> list[str]:
    if filter_on_subdir:
        path = Path(local_repo_path).joinpath(filter_on_subdir)
    else:
        path = Path(local_repo_path)

    markdown_files = path.rglob("*.md")
    rst_files = path.rglob("*.rst")

    return [
        os.path.relpath(absolute_file_path, local_repo_path)
        for absolute_file_path in list(markdown_files) + list(rst_files)
    ]


def get_absolute_documentation_file_path_list(*, local_repo_path: str) -> list[str]:
    relative_file_path_list = get_relative_documentation_file_path_list(
        local_repo_path=local_repo_path
    )
    return [
        os.path.join(local_repo_path, relative_file_path)
        for relative_file_path in relative_file_path_list
    ]


def get_documentation_file_headings(*, absolute_file_path: str) -> list[str]:
    headings = []
    in_code_block = False

    settings = frontend.get_default_settings(Parser)
    settings.report_level = 4  # Only report severe errors
    settings.halt_level = 5  # Don't halt on errors

    with open(absolute_file_path, "r", encoding="utf-8") as file:
        if absolute_file_path.endswith(".rst"):
            try:
                document = utils.new_document(file.name, settings)
                Parser().parse(file.read(), document)
                for node in document.traverse(nodes.title):
                    headings.append(node.astext())
            except Exception as e:
                logging.warning(
                    f"Error parsing RST file {absolute_file_path}: {str(e)}"
                )
                # Fallback to simple heading detection for RST
                file.seek(0)
                prev_line = ""
                for line in file:
                    line = line.strip()
                    # RST headings are often underlined with = or -
                    if line and (
                        all(c == "=" for c in line) or all(c == "-" for c in line)
                    ):
                        if prev_line and not prev_line.startswith(".."):
                            headings.append(prev_line)
                    prev_line = line

        elif absolute_file_path.endswith(".md"):
            for line in file:
                line = line.strip()

                # Check for code block delimiters
                if line.startswith("```"):
                    in_code_block = not in_code_block
                    continue

                # Only collect headings when not in a code block
                if not in_code_block and line.startswith("#"):
                    headings.append(line)
    return headings


def get_markdown_frontmatter(*, absolute_file_path: str) -> dict:
    with open(absolute_file_path, "r", encoding="utf-8") as file:
        return frontmatter.load(file).to_dict()
