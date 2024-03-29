FROM ubuntu:jammy

RUN : \
    && apt-get update --yes --fix-missing \
    && apt-get install --yes \
        python3 \
        python3-numpy \
        python3-pip \
        python3-scipy \
        python3-venv \
    && ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime \
    && rm -rf /var/lib/apt/lists/* \
    && :

WORKDIR /code

COPY lunations lunations
COPY requirements-ml-minimal.txt .
RUN : \
    && python3 -m venv /code/venv \
    && /code/venv/bin/pip install --upgrade pip \
    && /code/venv/bin/pip install --requirement=requirements-ml-minimal.txt \
    && :
ENV PATH="/code/venv/bin:${PATH}"

COPY lunations.csv.gz .
