Выберите x64 для Intel или arm64 для Apple Silicon.
Распакуйте ZIP на Mac и перенесите Gazyava-i-Hrumki.app в Applications.
Архив сохраняет символические ссылки и права исполняемых файлов.
Сборка не имеет подписи Apple Developer и нотариального заверения.
Перед первым запуском выполните локальную ad-hoc-подпись на Mac:
codesign --force --deep --sign - "/Applications/Gazyava-i-Hrumki.app"
Это необходимо, поскольку исходный подписанный Electron изменён при упаковке.
Проверка запуска на macOS здесь не проводилась.
