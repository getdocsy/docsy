import { Command } from "commander";
import { getSettings } from "./settings";

const program = new Command();

export const suggestCmd = program.command('suggest')
  .description('Suggest changes based on current context')
  .action(() => {
    const settings = getSettings();
    const url = `${settings.auth.apiUrl}/engine/suggestion`;
    const data = { context: [ { github_repository_name: 'felixzieger/docsy', pull_request_number: 1 } ] };



    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(response => response.json())
      .then(result => {
        console.log('Suggestion received:', result);
      })
      .catch(error => {
        console.error('Error suggesting changes:', error);
      });
  });