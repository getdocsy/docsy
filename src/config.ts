import _ from 'lodash';
import fs from 'fs';
import path from 'path';
import { DocsyConfig, parseDocsyConfig } from './spec/config';

export function getConfig(resave = true): DocsyConfig | null {
  const configFilePath = _getConfigFilePath();

  const configFileExists = fs.existsSync(configFilePath);
  if (!configFileExists) { return null; }

  const fileContents = fs.readFileSync(configFilePath, "utf8");
  const rawConfig = JSON.parse(fileContents);

  const result = parseDocsyConfig(rawConfig);
  const didConfigChange = !_.isEqual(rawConfig, result);

  if (resave && didConfigChange) {
    // Ensure the config is saved with the latest version / schema
    saveConfig(result);
  }

  return result;
}

export function saveConfig(config: DocsyConfig) {
  const configFilePath = _getConfigFilePath();

  const serialized = JSON.stringify(config, null, 2);
  fs.writeFileSync(configFilePath, serialized);

  return config;
}

// Private

function _getConfigFilePath() {
  return path.join(process.cwd(), "docsy.json");
}
