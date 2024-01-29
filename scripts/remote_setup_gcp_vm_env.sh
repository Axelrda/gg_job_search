# installing & setting up pyenv
gcloud compute ssh $INSTANCE --zone=$ZONE --command "\
git clone https://github.com/pyenv/pyenv.git ~/.pyenv && \
echo 'export PYENV_ROOT=\$HOME/.pyenv' >> ~/.bashrc && \
echo 'command -v pyenv >/dev/null || export PATH=\"\$PYENV_ROOT/bin:\$PATH\"' >> ~/.bashrc && \
echo 'eval \"\$(pyenv init -)\"' >> ~/.bashrc"

#installing dependdencies to build python from pyenv
gcloud compute ssh $INSTANCE --zone=$ZONE --command "sudo apt-get update; sudo apt-get -y install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
python3-dev"

# installing python
gcloud compute ssh $INSTANCE --zone=$ZONE --command "source ~/.bashrc \
pyenv install 3.10.6 \
pyenv global 3.10.6"

# installing pyenv-virtualenv plugin & creating ggjobsearch env
gcloud compute ssh $INSTANCE --zone=$ZONE --command "\
git clone https://github.com/pyenv/pyenv-virtualenv.git \$HOME/.pyenv/plugins/pyenv-virtualenv"

# creating ggjobsearch environment & stting it up as global env
gcloud compute ssh $INSTANCE --zone=$ZONE --command "source ~/.bashrc \
pyenv virtualenv 3.10.6 ggjobsearch \
pyenv global ggjobsearch"

# transfer entire local project dir to VM
rsync -avz $PROJECT_DIR_PATH $INSTANCE.$ZONE.$PROJECT:~/
