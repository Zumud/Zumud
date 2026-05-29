// Flat config using eslint-config-next's native flat configs (Next 16+).
// Avoids the @eslint/eslintrc FlatCompat layer, which hit a circular-schema
// error when wrapping eslint-config-next 16.
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

const eslintConfig = [
  ...nextCoreWebVitals,
  ...nextTypescript,
];

export default eslintConfig;
