import dotenv from 'dotenv';
dotenv.config();

import { Command } from 'commander';
import { suggestCmd } from './suggest';
import initCmd from './init';
import { version } from '../package.json';

const program = new Command();
program
  .version(`v${version}`)
  .description('Docsy CLI')
  .addCommand(initCmd)
  .addCommand(suggestCmd)
  .parse(process.argv);

