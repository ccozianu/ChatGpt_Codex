FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG INSTALL_CODEX_CLI=0

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl wget git openssh-client gnupg2 xauth \
    build-essential make cmake pkg-config gcc g++ gdb lldb \
    python3 python3-pip python3-venv python3-dev \
    netcat-openbsd dnsutils iproute2 iputils-ping traceroute \
    procps psmisc lsof strace tcpdump socat telnet whois \
    jq ripgrep fd-find fzf tree less vim-tiny nano \
    tini \
    libx11-6 libxext6 libxrender1 libxtst6 libxi6 libxrandr2 libxss1 libxkbfile1 \
    libgtk-3-0 libnss3 libnspr4 libasound2t64 libfontconfig1 libfreetype6 \
    libdbus-1-3 xdg-utils fonts-dejavu fonts-liberation \
    libgl1 \
    libglx-mesa0 \
    libgl1-mesa-dri \
    mesa-utils \
 && rm -rf /var/lib/apt/lists/*


RUN if [ "$INSTALL_CODEX_CLI" = "1" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends nodejs npm \
      && npm install -g @openai/codex \
      && npm cache clean --force \
      && codex --version ; \
    fi

COPY pycharm/ /opt/pycharm/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /opt/pycharm/bin/pycharm.sh \
 && ln -s /opt/pycharm/bin/pycharm.sh /usr/local/bin/pycharm

ENV PROJECT_PATH=/project \
    HOME=/ide-state/home \
    XDG_CONFIG_HOME=/ide-state/home/.config \
    XDG_CACHE_HOME=/ide-state/home/.cache \
    XDG_DATA_HOME=/ide-state/home/.local/share \
    QT_X11_NO_MITSHM=1 \
    _JAVA_AWT_WM_NONREPARENTING=1

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
