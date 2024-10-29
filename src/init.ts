import { Command } from "commander";
import Ora from 'ora';
import { getConfig, saveConfig } from "./config";
import { defaultConfig } from "./spec/config";

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

    await saveConfig(defaultConfig);

    spinner.succeed('Docsy project initialized');
  });
  