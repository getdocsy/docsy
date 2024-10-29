import { Command } from "commander";
import Ora from 'ora';
import { getSettings } from "../settings";
import { getConfig } from "../config";
import { GitRepo } from "../utils/git";
import { formatSuggestionAsTable, suggestionSchema } from "../spec/suggestion";
import { DocsyRepo } from "../utils/docsyrepo";
import { select } from '@inquirer/prompts';
const program = new Command();

export const suggestCmd = program.command('suggest')
  .description('Suggest changes based on current context')
  .action(async () => {
    const spinner = Ora();

    spinner.start('Loading context...');
    const settings = getSettings();
    const config = getConfig();
    const gitRepo = new GitRepo(process.cwd());
    const headSha = gitRepo.getHeadSha();
    const docsyRepo = new DocsyRepo(gitRepo);

    if (!docsyRepo.hasSuggestion(headSha)) {
      const url = `${settings.auth.apiUrl}/engine/suggestion`;

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

        docsyRepo.saveSuggestion(suggestion, headSha);
      } catch (error) {
        spinner.fail("Error suggesting changes");
        console.error(error);
      }
    } else {
      spinner.succeed('Found an existing suggestion');
      console.log(formatSuggestionAsTable(docsyRepo.getSuggestion(headSha)));

      const answer = await select({
        message: 'What would you like to do with this suggestion?',
        choices: [
          { value: 'a', name: 'Accept' },
          { value: 'e', name: 'Edit' },
          { value: 'd', name: 'Discard' },
        ],
      });

      switch (answer) {
        case 'a':
          spinner.succeed('Accepted suggestion');
          break;
        case 'e':
          docsyRepo.editSuggestion(headSha);
          spinner.succeed('Edited suggestion');
          break;
        case 'd':
          docsyRepo.discardSuggestion(headSha);
          spinner.succeed('Discarded suggestion');
          break;
        default:
          console.log('Invalid choice, discarding suggestion');
      }
    }
  });
