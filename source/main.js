const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 720,
    backgroundColor: '#2b1b4a',
    autoHideMenuBar: true,
    title: 'Газява и Хрумки'
  });
  win.setMenuBarVisibility(false);
  win.loadFile(path.join(__dirname, 'game', 'index.html'));
  // F11 — полный экран
  win.webContents.on('before-input-event', (event, input) => {
    if (input.type === 'keyDown' && input.key === 'F11') {
      win.setFullScreen(!win.isFullScreen());
    }
  });
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
