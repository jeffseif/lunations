# OS

FROM    ubuntu:focal
RUN     apt-get update \
&&      apt-get upgrade \
            --yes \
&&      ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime \
        ;

# System dependencies

RUN     apt-get install \
            --no-install-recommends \
            --yes \
            dumb-init \
            python3 \
            python3-numpy \
            python3-pip \
            python3-scipy \
            python3-setuptools \
            virtualenv \
        ;

# Python packages

RUN     virtualenv \
            --python=$(which python3) \
            /code/venv \
&&      /code/venv/bin/pip install \
            --upgrade pip \
        ;
COPY    requirements-minimal.txt /code/
RUN     /code/venv/bin/pip install \
            --requirement /code/requirements-minimal.txt \
        ;

# Bust any downstream caches upon new commits

ARG     GIT_SHA
ENV     GIT_SHA=${GIT_SHA}

# Code

WORKDIR /code
COPY    lunations/ lunations/

# Run

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD     ["/bin/bash"]
