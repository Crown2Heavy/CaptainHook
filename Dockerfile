# Use Debian Bookworm for a solid base
FROM debian:bookworm-slim

# Enable multi-arch for wine32 and install dependencies
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y \
    wine \
    wine64 \
    wine32 \
    wget \
    unzip \
    ca-certificates \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set up Wine environment
ENV WINEDEBUG=-all
ENV WINEPREFIX=/wine
ENV WINEARCH=win64

# Step 1: Initialize Wine
RUN wineboot --init && wineserver -w

# Step 2: Install Windows Python using the FULL Installer (more stable than embeddable)
# We use XVFB to handle any GUI popups from the installer in a headless environment
WORKDIR /install
RUN wget -q https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe && \
    xvfb-run wine python-3.11.5-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 && \
    wineserver -w && \
    rm python-3.11.5-amd64.exe

# Step 3: Install pip and essential build tools
RUN wine python -m pip install --upgrade pip && \
    wineserver -w

# Step 4: Pre-install heavy dependencies to cache them in the image
# This speeds up the local builder significantly
RUN wine python -m pip install \
    pyinstaller==6.3.0 \
    discord.py \
    aiohttp \
    mss \
    psutil \
    pyautogui \
    pynput \
    ping3 \
    rich \
    && wineserver -w

WORKDIR /src
CMD ["bash"]
