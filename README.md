# ANT-Man

# Setup the requirements

`conda env create -f environment.yaml`

## Tools
- [zipkin](https://github.com/openzipkin/zipkin)
- [Jaeger](https://www.jaegertracing.io/)

## RUN

Firstly deploy applications,

- [train-ticket](https://github.com/FudanSELab/train-ticket)
- [DeathStarBench](https://github.com/delimitrou/DeathStarBench)

Then run as following,

- `python collect_train.py` run trainticket service
- `python collect_social.py` run social network service
- `python collect.py` run with different settings

## Outputs

- Results in Sections 1 and 3 are mainly generated with `collect_train.py` and `collect_social.py` under different load settings (configured with `server_*.py`).

- Results in Section 6 are mainly generated with `collect.py` under different load settings (configured with `server_*.py`).

We plot all the figures with Microsoft Excel.