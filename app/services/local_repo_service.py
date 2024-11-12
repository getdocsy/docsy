from app.models import Repo
import tempfile
import git
import shutil
from contextlib import contextmanager

@contextmanager
def clone_repo(*, repo: Repo):
    temp_dir = tempfile.mkdtemp()
    try:
        git.Repo.clone_from(repo.nfkc_clone_url, temp_dir)
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
