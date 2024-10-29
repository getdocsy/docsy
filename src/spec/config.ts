import Z from 'zod';

// factories
type ConfigDefinition<T extends Z.ZodRawShape, P extends Z.ZodRawShape> = {
  schema: Z.ZodObject<T>;
  defaultValue: Z.infer<Z.ZodObject<T>>;
  parse: (rawConfig: unknown) => Z.infer<Z.ZodObject<T>>;
};
const createConfigDefinition = <T extends Z.ZodRawShape, P extends Z.ZodRawShape>(
  definition: ConfigDefinition<T, P>,
) => definition;


type ConfigDefinitionExtensionParams<T extends Z.ZodRawShape, P extends Z.ZodRawShape> = {
  createSchema: (baseSchema: Z.ZodObject<P>) => Z.ZodObject<T>;
  createDefaultValue: (baseDefaultValue: Z.infer<Z.ZodObject<P>>) => Z.infer<Z.ZodObject<T>>;
  createUpgrader: (
    config: Z.infer<Z.ZodObject<P>>,
    schema: Z.ZodObject<T>,
    defaultValue: Z.infer<Z.ZodObject<T>>,
  ) => Z.infer<Z.ZodObject<T>>;
};
const extendConfigDefinition = <T extends Z.ZodRawShape, P extends Z.ZodRawShape>(
  definition: ConfigDefinition<P, any>,
  params: ConfigDefinitionExtensionParams<T, P>,
) => {
  const schema = params.createSchema(definition.schema);
  const defaultValue = params.createDefaultValue(definition.defaultValue);
  const upgrader = (config: Z.infer<Z.ZodObject<P>>) => params.createUpgrader(config, schema, defaultValue);

  return createConfigDefinition({
    schema,
    defaultValue,
    parse: (rawConfig) => {
      const safeResult = schema.safeParse(rawConfig);
      if (safeResult.success) {
        return safeResult.data;
      }

      const baseConfig = definition.parse(rawConfig);
      const result = upgrader(baseConfig);
      return result;
    }
  });
};

// any -> v0
const configV0Schema = Z.object({
  version: Z.number().default(0),
});
export const configV0Definition = createConfigDefinition({
  schema: configV0Schema,
  defaultValue: { version: 0 },
  parse: (rawConfig) => {
    return configV0Schema.parse(rawConfig);
  },
});

// v0 -> v1
export const configV1Definition = extendConfigDefinition(configV0Definition, {
  createSchema: (baseSchema) => baseSchema.extend({
    defaultBranch: Z.string(),
  }),
  createDefaultValue: () => ({
    version: 1,
    defaultBranch: 'main',
  }),
  createUpgrader: () => ({
    version: 1, 
    defaultBranch: 'main',
  }),
});

// exports
const LATEST_CONFIG_DEFINITION = configV1Definition;

export type DocsyConfig = Z.infer<typeof LATEST_CONFIG_DEFINITION['schema']>;

export function parseDocsyConfig(rawConfig: unknown) {
  try {
    const result = LATEST_CONFIG_DEFINITION.parse(rawConfig);
    return result;
  } catch (error: any) {
    throw new Error(`Failed to parse config: ${error.message}`);
  }
}

export const defaultConfig = LATEST_CONFIG_DEFINITION.defaultValue;