# Stage 1: init
FROM python:3.12 AS init

ARG uv=/root/.cargo/bin/uv

# Install `uv` for faster package boostrapping
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Copy local context to `/app` inside container (see .dockerignore)
WORKDIR /app
COPY . .
RUN mkdir -p /app/data /app/uploaded_files

# Create virtualenv which will be copied into final container
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN $uv venv

# Install app requirements and reflex inside virtualenv
RUN $uv pip install -r requirements.txt

# Upgrade reflex
RUN pip reflex --upgrade

# Deploy templates and prepare app
RUN reflex init

# Stage 2: copy artifacts into slim image
FROM python:3.12-slim AS frontend
# install curl for healthcheck
RUN apt-get -y update; apt-get -y install curl
# for frontend
RUN apt-get -y install unzip
WORKDIR /app
RUN adduser --disabled-password --home /app reflex
RUN chown reflex:reflex -R /app
COPY --chown=reflex --from=init /app /app

USER reflex
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1

# make environment variable
# ENV WHICH_END

# Needed until Reflex properly passes SIGTERM on backend.
STOPSIGNAL SIGKILL

EXPOSE 3000

ENTRYPOINT ["/app/entrypoint.sh"]
