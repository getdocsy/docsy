import { Command } from "commander";
import Ora from 'ora';
import { getConfig, saveConfig } from "./config";
import { defaultConfig } from "./spec/config";
import { promises as fs } from 'fs';
import path from 'path';

export default new Command()
  .command("init")
  .description("Initialize Docsy project")
  .helpOption("-h, --help", "Show help")
  .action(async (options) => {
    const spinner = Ora().start('Initializing Docsy project');

    let config = await getConfig(false);
    if (config) {
      spinner.fail('Docsy project already initialized');
      return process.exit(1);
    }

    // Add .docsy/ to .gitignore
    try {
      const gitignorePath = path.join(process.cwd(), '.gitignore');
      let gitignoreContent = '';
      
      try {
        gitignoreContent = await fs.readFile(gitignorePath, 'utf8');
      } catch (error) {
        // File doesn't exist, that's okay
      }

      if (!gitignoreContent.includes('.docsy/')) {
        const updatedContent = gitignoreContent + (gitignoreContent.endsWith('\n') ? '' : '\n') + '.docsy/\n';
        await fs.writeFile(gitignorePath, updatedContent, 'utf8');
      }
    } catch (error) {
      spinner.warn('Could not update .gitignore file');
    }

    await saveConfig(defaultConfig);

    spinner.succeed('Docsy project initialized');
  });
  