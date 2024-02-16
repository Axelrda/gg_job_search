#!/bin/bash

# This script is designed to be run after SSHing into the VM

# Clone pyenv and update .bashrc
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT=$HOME/.pyenv' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Install dependencies to build Python from pyenv
sudo apt-get update
sudo apt-get -y install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
python3-dev

# Source .bashrc and install Python 3.10.6
source ~/.bashrc

sleep 10 # sleep seems necessary as VM ask for a restart (proly what's making the script fail after this point)
pyenv install 3.10.6
pyenv global 3.10.6

# Clone pyenv-virtualenv plugin
git clone https://github.com/pyenv/pyenv-virtualenv.git $HOME/.pyenv/plugins/pyenv-virtualenv

# Create and set ggjobsearch environment as global
source ~/.bashrc
pyenv virtualenv 3.10.6 ggjobsearch
pyenv global ggjobsearch
pyenv activate ggjobsearch


pip install jupyter
pip install --upgrade pip
pip install pandas serpapi torch transformers tqdm openai scikit-learn 


code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
pip install openai serpapi
pip install -e .

code --install-extension VisualStudioExptTeam.intellicode-api-usage-examples
code --install-extension VisualStudioExptTeam.vscodeintellicode

sudo timedatectl set-timezone Europe/Paris
