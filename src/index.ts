#!/usr/bin/env node
import dotenv from 'dotenv';
dotenv.config();

import { Command } from "commander";
import { suggestCmd } from './suggest';
import packageJson from '../package.json';

const program = new Command();

program
  .version(`v${packageJson.version}`)
  .description('Docsy CLI')
  .option('-n, --name <name>', 'specify a name')
  .addCommand(suggestCmd)
  .parse(process.argv);

