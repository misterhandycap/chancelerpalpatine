FROM python:3.11-alpine3.19 AS builder

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

FROM python:3.11-alpine

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11

# Runtime dependencies
RUN apk add git cairo libjpeg openjpeg tiff openblas postgresql-libs

# For some reason, Cairo requests libcairo.so.2 instead of installed libcairo.so
RUN ln -s /usr/lib/libcairo.so.2 /usr/lib/libcairo.so

# Updated SSL certificates
RUN apk update && apk add ca-certificates && rm -rf /var/cache/apk/*

# Stockfish dependencies
RUN apk add libgcc libstdc++ musl

# Add run time non root user
RUN addgroup -g 1000 run_user && adduser -G run_user -u 1000 run_user -D
USER run_user

COPY --chown=1000:1000 . /app
WORKDIR /app

# Bot healthcheck
HEALTHCHECK CMD python3 -m discordhealthcheck || exit 1

CMD [ "python3", "run.py" ]
