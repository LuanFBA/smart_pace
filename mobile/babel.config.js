const path = require("path");

const babelPresetExpoPath = require.resolve("babel-preset-expo", {
  paths: [path.join(__dirname, "node_modules", "expo")],
});

module.exports = function (api) {
  api.cache(true);
  return {
    presets: [babelPresetExpoPath],
  };
};
