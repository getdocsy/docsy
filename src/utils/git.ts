import { execSync } from 'child_process';
import path from 'path';

export interface GitCommit {
  sha: string;
  message: string;
  diff: string;
}

export class GitRepo {
  private repoPath: string;
  fullName: string;

  constructor(repoPath: string) {
    this.repoPath = path.resolve(repoPath);
    this.fullName = this.getOriginFullName();
  }

  /**
   * Gets commits that the current branch is ahead of the default branch
   * @param defaultBranch The name of the default branch (e.g. 'main')
   * @returns Array of commits that are ahead of the default branch
   */
  getCommitsAheadOfDefault(defaultBranch: string): GitCommit[] {
    // Get the merge base (common ancestor) between current HEAD and default branch
    const mergeBaseCommand = `git -C "${this.repoPath}" merge-base HEAD ${defaultBranch}`;
    const mergeBase = execSync(mergeBaseCommand, { encoding: 'utf-8' }).trim();

    // Get commits between merge base and HEAD
    return this.getCommitsBetween(mergeBase, 'HEAD');
  }

  /**
   * Gets a list of commits between two SHAs
   * @param fromSha Starting SHA (older)
   * @param toSha Ending SHA (newer)
   * @returns Array of commits between the two SHAs
   */
  getCommitsBetween(fromSha: string, toSha: string): GitCommit[] {
    // Get list of commit SHAs between fromSha and toSha
    const logCommand = `git -C "${this.repoPath}" log --format=%H ${fromSha}..${toSha}`;
    const commitShas = execSync(logCommand, { encoding: 'utf-8' }).trim().split('\n');
    
    // Get diff for each commit
    const commits: GitCommit[] = [];
    for (let i = 0; i < commitShas.length; i++) {
      const sha = commitShas[i];
      const parentSha = i === commitShas.length - 1 ? fromSha : commitShas[i + 1];
      const command = `git -C "${this.repoPath}" diff ${parentSha} ${sha}`;
      const diff = execSync(command, { encoding: 'utf-8' }).trim();
      commits.push({ sha, message: '', diff });
    }
    return commits;
  }

  /**
   * Gets the URL of the origin remote
   * @returns The URL of the origin remote
   */
  private getOriginUrl(): string {
    const command = `git -C "${this.repoPath}" config --get remote.origin.url`;
    return execSync(command, { encoding: 'utf-8' }).trim();
  }

  /**
   * Gets the owner and repo name from the origin remote URL
   * @returns Object containing owner and repo name
   */
  private getOriginFullName(): string {
    const url = this.getOriginUrl();
    
    // Handle SSH or HTTPS URLs
    const match = url.match(/(?:git@github\.com:|https:\/\/github\.com\/)([^\/]+)\/(.+?)(?:\.git)?$/);
    if (!match) {
      throw new Error('Could not parse GitHub repository URL');
    }

    return `${match[1]}/${match[2]}`;
  }
}