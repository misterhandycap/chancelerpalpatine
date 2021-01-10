FROM python:3.7-alpine

RUN apk add --no-cache gcc libc-dev libffi-dev

# Cairo deps
RUN apk add build-base cairo-dev cairo cairo-tools

# Pillow deps
RUN apk add freetype-dev \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    openjpeg-dev \
    tcl-dev \
    tiff-dev \
    tk-dev \
    zlib-dev

# AsyncSSH deps
RUN apk add openssl openssl-dev

# Numpy deps
RUN apk --no-cache add musl-dev linux-headers g++ gfortran libpng-dev openblas-dev wget

# Postgres deps
RUN apk add postgresql-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "run.py" ]
