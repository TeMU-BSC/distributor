# Update your repositories.
sudo apt update

# Ensure that your system has python3, pip3 and tree installed and updated.
sudo apt install -y python3 python3-pip tree
pip3 install --user --upgrade pip

# Install pipenv. https://pipenv.kennethreitz.org/en/latest/
pip3 install --user --upgrade pipenv

# Tell pipenv to create the virtual environment inside the working directory
# setting the following variable to a non-empty value.
export PIPENV_VENV_IN_PROJECT=1

# [ The following commands are optional]

# Install and setup direnv. https://direnv.net
# sudo apt install -y direnv
# echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
# direnv allow .
# echo export PIPENV_VENV_IN_PROJECT=enabled >> .envrc