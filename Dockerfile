# Use Debian Bookworm for better stability
FROM debian:bookworm-slim

# Enable multi-arch for wine32
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y \
    wine \
    wine64 \
    wine32 \
    wget \
    python3 \
    python3-pip \
    ca-certificates \
    xvfb \
    gcc \
    g++ \
    make \
    libasound2-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Wine environment
ENV WINEDEBUG=-all
ENV WINEPREFIX=/wine
ENV WINEARCH=win64

# Step 1: Initialize Wine Prefix
RUN xvfb-run wineboot --init && wineserver -w

# Step 2: Download and Install Windows Python
# We use a specific version known to work well with Wine
RUN wget -q https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe && \
    xvfb-run wine python-3.11.5-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 && \
    wineserver -w && \
    rm python-3.11.5-amd64.exe

# Set up a symlink for easy access to Windows python
RUN echo '#!/bin/bash\nxvfb-run wine "C:\\Python311\\python.exe" "$@"' > /usr/local/bin/winpy && \
    chmod +x /usr/local/bin/winpy

# Step 3: Install PyInstaller and dependencies
# We do this in one block to ensure wineserver settles
RUN winpy -m pip install --upgrade pip && \
    winpy -m pip install pyinstaller==6.3.0 && \
    wineserver -w

WORKDIR /src

CMD ["bash"]
