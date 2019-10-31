# Clone this github repo and enter the project directory
git clone https://github.com/TeMU-BSC/distributor.git
cd distributor

# Update your repositories
sudo apt update

# Ensure that your system has python3 and pip3 installed and updated
sudo apt install -y python3 python3-pip
pip3 install --user --upgrade pip

# Install pipenv --  https://pipenv.kennethreitz.org/en/latest/
pip3 install --user --upgrade pipenv

# Set the neeeded environment variable to tell pipenv to create the virtual environment inside the working directory

# Option A: Just export the variable
export PIPENV_VENV_IN_PROJECT="enabled"

# Option B: Install and setup direnv -- https://direnv.net
# sudo apt install -y direnv
# echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
# direnv allow .
