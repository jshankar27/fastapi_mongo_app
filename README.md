# Starting virtual env
python3 -m venv venv

# Activating the virtual env
source venv/bin/activate

# Installing libraries
pip install -r requirements.txt

# Starting the app
python3 app/main.py

# Deactivating the virtual env
deactivate


## MONGO DB installation:
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# to stop mongo services:
brew services stop mongodb-community

# Install mongo compass using homebrew
brew install --cask mongodb-compass