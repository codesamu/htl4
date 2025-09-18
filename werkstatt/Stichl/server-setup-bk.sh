#!/usr/bin/env bash
set -e

# -------------------------------
# Basic system update & tools
# -------------------------------
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget unzip build-essential

# -------------------------------
# Install zoxide
# -------------------------------
curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash
echo 'eval "$(zoxide init bash)"' >>~/.bashrc

# -------------------------------
# Install Neovim (latest stable)
# -------------------------------
if ! command -v nvim &>/dev/null; then
  sudo apt install -y neovim
fi

# -------------------------------
# Install tmux
# -------------------------------
if ! command -v tmux &>/dev/null; then
  sudo apt install -y tmux
fi

# -------------------------------
# Install yazi
# -------------------------------
if ! command -v yazi &>/dev/null; then
  YA_VER=$(curl -s https://api.github.com/repos/sxyazi/yazi/releases/latest | grep "tag_name" | cut -d '"' -f 4)
  wget https://github.com/sxyazi/yazi/releases/download/${YA_VER}/yazi-${YA_VER}-x86_64-unknown-linux-gnu.zip -O /tmp/yazi.zip
  unzip /tmp/yazi.zip -d /tmp/yazi
  sudo mv /tmp/yazi/yazi /usr/local/bin/
  rm -rf /tmp/yazi /tmp/yazi.zip
fi

# -------------------------------
# Clone dotfiles and apply configs
# -------------------------------
DOTFILES_DIR="$HOME/dotfiles"

if [ ! -d "$DOTFILES_DIR" ]; then
  git clone https://github.com/codesamu/dotfiles.git "$DOTFILES_DIR"
else
  echo "Dotfiles already cloned, pulling latest..."
  cd "$DOTFILES_DIR" && git pull
fi

# Symlink configs
mkdir -p ~/.config
ln -sf "$DOTFILES_DIR/nvim" ~/.config/nvim
ln -sf "$DOTFILES_DIR/tmux" ~/.config/tmux
ln -sf "$DOTFILES_DIR/yazi" ~/.config/yazi

echo "✅ Installation complete! Restart your shell to apply zoxide."
