const fs = require('node:fs');
const path = require('node:path');
const asar = require('@electron/asar');
const root = path.resolve(__dirname, '..');
const stage = path.join(__dirname, 'app');
fs.mkdirSync(path.join(stage, 'game'), { recursive: true });
let html = fs.readFileSync(path.join(root, 'source/index (2).html'), 'utf8');
// Use system fonts so that every build works without network access.
html = html.replace(/<link[^>]+https:\/\/fonts\.googleapis\.com[^>]*>\s*/g, '');
fs.writeFileSync(path.join(stage, 'game/index.html'), html);
for (const name of ['three.min.js', 'sw.js', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png', 'golda.png']) {
  fs.copyFileSync(path.join(root, 'source', name), path.join(stage, 'game', name));
}
fs.copyFileSync(path.join(root, 'source/main.js'), path.join(stage, 'main.js'));
const pkg = JSON.parse(fs.readFileSync(path.join(root, 'source/package.json')));
fs.writeFileSync(path.join(stage, 'package.json'), JSON.stringify({name:pkg.name,version:pkg.version,description:pkg.description,author:pkg.author,main:'main.js'}, null, 2));
fs.mkdirSync(path.join(root, 'Web'), { recursive: true });
fs.cpSync(path.join(stage, 'game'), path.join(root, 'Web'), { recursive: true });
asar.createPackage(stage, path.join(__dirname, 'app.asar')).then(() => {
  console.log('Prepared offline Web assets and app.asar');
}).catch(error => { console.error(error); process.exitCode = 1; });
