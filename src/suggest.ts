import { Command } from "commander";
import Ora from 'ora';
import { getSettings } from "./settings";
import { getConfig } from "./config";

const program = new Command();

export const suggestCmd = program.command('suggest')
  .description('Suggest changes based on current context')
  .action(async () => {
    const spinner = Ora();
    const settings = getSettings();
    const config = getConfig();
    const url = `${settings.auth.apiUrl}/engine/suggestion`;
    const data = { context: [ { github_repository_name: 'felixzieger/docsy', pull_request_number: 1 } ] };

    spinner.start('Connecting to Docsy...');
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      spinner.succeed();
      const result = await response.json();
      spinner.succeed('Suggestion received');
      console.log(result);
    } catch (error) {
      spinner.fail("Error suggesting changes");
      console.error(error);
    }
  });