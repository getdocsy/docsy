import { Command } from "commander";
import Ora from 'ora';
import { getSettings } from "../settings";
import { getConfig } from "../config";
import { GitRepo } from "../utils/git";
import { formatSuggestionAsTable, suggestionSchema } from "../spec/suggestion";
const program = new Command();

export const suggestCmd = program.command('suggest')
  .description('Suggest changes based on current context')
  .action(async () => {
    const spinner = Ora();

    spinner.start('Loading context...');
    const settings = getSettings();
    const config = getConfig();
    const url = `${settings.auth.apiUrl}/engine/suggestion`;
    
    const gitRepo = new GitRepo(process.cwd());
    const context = [{ github_repo_full_name: gitRepo.fullName, commits: gitRepo.getCommitsAheadOfDefault(config?.defaultBranch ?? 'main') }];

    const target = {
      github_repo_full_name: config?.target?.full_name,
    };
    const data = { context, target };
    spinner.succeed('Context loaded');

    spinner.start('Connecting to Docsy...');
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      const result = await response.json();
      spinner.succeed('Connected to Docsy');

      const suggestion = suggestionSchema.parse(result);
      console.log(formatSuggestionAsTable(suggestion));
    } catch (error) {
      spinner.fail("Error suggesting changes");
      console.error(error);
    }
  });