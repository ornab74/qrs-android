module.exports = {
  outputDir: "wasm",           // where generated code will go
  targets: ["react-native"],   // target platform
  scan: {
    paths: ["wasm/qrs.wasm"],  // path(s) to WASM module(s) to integrate
  },
};
