import os
from pathlib import Path
from app.models import Repo
import tempfile
import git
import shutil
from contextlib import contextmanager

@contextmanager
def temp_clone_repo(*, repo: Repo):
    temp_local_repo_path = tempfile.mkdtemp()
    try:
        git.Repo.clone_from(repo.nfkc_clone_url, temp_local_repo_path)
        yield temp_local_repo_path
    finally:
        shutil.rmtree(temp_local_repo_path, ignore_errors=True)

def get_relative_markdown_file_path_to_headings(*, local_repo_path: str) -> dict:
    relative_file_path_to_headings = {}
    for absolute_file_path in Path(local_repo_path).rglob("*.md"):
        relative_file_path_to_headings[
            os.path.relpath(absolute_file_path, local_repo_path)
        ] = get_markdown_file_headings(absolute_file_path=absolute_file_path)
    return relative_file_path_to_headings

def get_markdown_file_headings(*, absolute_file_path: str) -> list[str]:
    headings = []
    with open(absolute_file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("#"):
                headings.append(line)
    return headings

def get_file_content(*, local_repo_path: str, relative_file_path: str) -> str:
    absolute_file_path = os.path.join(local_repo_path, relative_file_path)
    with open(absolute_file_path, "r", encoding="utf-8") as file:
        return file.read()
