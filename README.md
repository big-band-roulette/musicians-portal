# Big Band Roulette Portal

This is the portal for the big band roulette page.
To build this repository, create a new python env and run:

`python -m pip install flask-security-too[common,mfa,fsqla]`

`python -m pip install zxcvbn`

`python -m pip install pandas`

`python -m pip install mysql-connector-python`

This should install all of the necessary modules. You can then run the `app.py` python file, which should create the app at port 5001.

There are two users pre-enabled on the system (all simulation data can be found in data simulator.py) These are:

username: `test@me.com`, password: `password`. This is enabled with one audition already signed up, but no auditions completed.

username: `2@me.com`, password: `2`. This is enabled with no auditions signed up, but they have already completed their audition so you can see the upcoming gigs and my gigs pages.

## Useful extensions
`djlint` along with the python djlint package for autolinting of the html files
`better jinja` helps with the html file highlighting 

## TODO and important comments
These are in place to explain obvious parts for improvement and to warn against editing the security templates.

## Please feel free to add comments wherever!
Follow the `better comments` extension if working in vscode (or just copy pre-existing formatting) so that they can be seen clearly.

# TO RUN

- first set the environment variables. In powershell, run `. .\set_env_vars.ps1`.

- Then run `python init_db.py`. This will seed the database.
- Then start all the usual running of `run.sh` or `systemct1` (or if testing locally just run `app.py`)

