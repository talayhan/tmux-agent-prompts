# Reproducible local and CI test environment for tmux-agent-prompts.
# Build: docker build -t tmux-agent-prompts:test .
# Run:   docker run --rm tmux-agent-prompts:test
FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        bash \
        ca-certificates \
        curl \
        fzf \
        git \
        make \
        shellcheck \
        tmux \
    && rm -rf /var/lib/apt/lists/*

# shfmt and bats are installed by the development bootstrap once versions are
# locked in requirements-dev.txt / tooling configuration.
COPY . /workspace

RUN python -m pip install --no-cache-dir --upgrade pip \
    && if [ -f requirements-dev.txt ]; then python -m pip install --no-cache-dir -r requirements-dev.txt; fi

ENV HOME=/tmp/tmux-agent-prompts-home \
    XDG_CONFIG_HOME=/tmp/tmux-agent-prompts-config \
    XDG_CACHE_HOME=/tmp/tmux-agent-prompts-cache \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p "$HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"

CMD ["make", "check"]
