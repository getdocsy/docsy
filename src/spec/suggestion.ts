import { z as Z } from 'zod';
import table from 'table';
export const suggestionFileSchema = Z.object({
  path: Z.string(),
  action: Z.enum(['~', '+', '-']),
  explanation: Z.string().optional()
});

export const suggestionSchema = Z.object({
  suggestion: Z.object({
    files: Z.array(suggestionFileSchema)
  })
});

export type SuggestionFile = Z.infer<typeof suggestionFileSchema>;
export type Suggestion = Z.infer<typeof suggestionSchema>;

export function formatSuggestionAsTable(suggestion: Suggestion): string {

  const header = ['Action', 'Path', 'Explanation'];
  const rows = suggestion.suggestion.files.map(file => [
    file.action,
    file.path,
    file.explanation || ''
  ]);

  const data = [header, ...rows];
  const config = {
    border: table.getBorderCharacters('norc'),
  };

  return table.table(data, config);
}
