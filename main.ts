const fs = require('fs');
const path = require('path');

const source = path.join(__dirname, 'entry.png');
// The front page pairs an escalating global-news cycle with a dry broadsheet tone.
const outDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
fs.mkdirSync(outDir, { recursive: true });
fs.copyFileSync(source, path.join(outDir, 'entry.png'));
