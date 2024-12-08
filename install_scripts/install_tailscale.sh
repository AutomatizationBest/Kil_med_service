#!/bin/bash

# Относительный путь к Tailscale
TAILSCALE_PATH="/install_scripts/tailscale"

# Стандартный путь для пользовательских программ
INSTALL_PATH="/usr/local/bin/tailscale"

# Проверка, существует ли файл
if [ -f "$TAILSCALE_PATH" ]; then
    # Копирование Tailscale в /usr/local/bin
    sudo cp "$TAILSCALE_PATH" "$INSTALL_PATH"
    echo "Tailscale был успешно скопирован в /usr/local/bin/"
else
    echo "Ошибка: файл Tailscale не найден в $TAILSCALE_PATH"
fi

# chmod +x /home/automatization/install_tailscale.sh
# ./install_tailscale.sh
