import { Suggestion, suggestionSchema } from '../spec/suggestion';
import { GitRepo, GitCommit } from './git';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
export class DocsyRepo {
  private gitRepo: GitRepo;

  constructor(gitRepo: GitRepo) {
    this.gitRepo = gitRepo;
  }

  private getSuggestionDir() {
    const docsyDir = path.join(process.cwd(), '.docsy');
    const suggestionDir = path.join(docsyDir, 'suggestion');
    fs.mkdirSync(suggestionDir, { recursive: true });
    return suggestionDir;
  }

  getSuggestion(headSha: string): Suggestion {
    const suggestionDir = this.getSuggestionDir();
    const suggestionPath = path.join(suggestionDir, `${headSha}.json`);
    if (!fs.existsSync(suggestionPath)) {
      throw new Error(`Suggestion for ${headSha} not found`);
    }
    return suggestionSchema.parse(JSON.parse(fs.readFileSync(suggestionPath, 'utf8')));
  }

  saveSuggestion(suggestion: Suggestion, headSha: string) {
    const suggestionDir = this.getSuggestionDir();
    const suggestionPath = path.join(suggestionDir, `${headSha}.json`);
    fs.writeFileSync(suggestionPath, JSON.stringify(suggestion, null, 2));
  }

  editSuggestion(headSha: string) {
    const suggestionDir = this.getSuggestionDir();
    const suggestionPath = path.join(suggestionDir, `${headSha}.json`);
    const editor = process.env.EDITOR || 'vi';
    spawn(editor, [suggestionPath], { stdio: 'inherit' });
  }

  discardSuggestion(headSha: string) {
    const suggestionDir = this.getSuggestionDir();
    const suggestionPath = path.join(suggestionDir, `${headSha}.json`);
    fs.unlinkSync(suggestionPath);
  }

  hasSuggestion(headSha: string): boolean {
    const suggestionDir = this.getSuggestionDir();
    const suggestionPath = path.join(suggestionDir, `${headSha}.json`);
    return fs.existsSync(suggestionPath);
  }

}

