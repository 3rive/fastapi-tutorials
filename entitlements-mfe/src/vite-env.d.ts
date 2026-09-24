/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
}

declare module "*.css?inline" {
  const source: string;
  export default source;
}
