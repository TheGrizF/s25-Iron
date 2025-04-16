# TasteBuddies
Team Iron - Spring 2025
Old Dominion University

# Members
  - TheGrizF - Grant Fitch - gfitc002@odu.edu
  - cwodu - Colette Woods - cwood076@odu.edu
  - ashleyb171 - Ashley Barasebwa - abara007@odu.edu
  - benyameen-zeev - Ben Nissley - bniss001@odu.edu
  - Oronde25 - Oronde Brown - obrow008@odu.edu
  - GreenNate - Nate Donald - ndona004@odu.edu

# Setup
(in your own venv)
1. run `pip install -r requirements.txt`
2. FLASK_APP should be set correctly in .flaskenv. If not, run `export FLASK_APP=tastebuddies.py`
3. run `flask run`

If you would like to debug  run `flask run --debug`
If you already have a copy of tastebuddies.db on your local, remember to delete it before running

# Digital Ocean
SSH keys required.

1. `ssh root@167.172.145.100`
2. `source venv/bin/activate`
3. `cd ../var/www/tastebuddies`
4. After pulling from github branch, run `systemctl restart tastebuddies`
5. Run `systemctl status tastebuddies` to check the status. 
