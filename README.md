# ANT-Man

# Setup the requirements

`conda env create -f environment.yaml`

## RUN

Firstly deploy applications,

- https://github.com/FudanSELab/train-ticket
- https://github.com/delimitrou/DeathStarBench

Then run as following,

- `python collect_train.py` run trainticket service
- `python collect_social.py` run social network service
- `python collect.py` run with different settings
