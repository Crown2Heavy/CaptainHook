# Use a lightweight Debian-based image with Wine
FROM debian:trixie-slim

# Enable multi-arch for wine32 (required for WOW64 even on 64-bit prefixes)
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

# Install Windows Python inside Wine
# Using Python 3.11.x for Windows
# We use /quiet and Wait=1 to ensure the installer finishes
RUN xvfb-run wine boot --init && \
    wget -q https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe && \
    xvfb-run wine python-3.11.5-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm python-3.11.5-amd64.exe

# Set up a symlink for easy access to Windows python
# Python usually installs to C:\Python311\python.exe or C:\Program Files\Python311\python.exe
# We'll check both common locations
RUN echo 'if [ -f "/wine/drive_c/Python311/python.exe" ]; then wine "C:\Python311\python.exe" "$@"; else wine "C:\Program Files\Python311\python.exe" "$@"; fi' > /usr/local/bin/winpy && \
    chmod +x /usr/local/bin/winpy

# Install PyInstaller and dependencies in the Windows environment
RUN xvfb-run winpy -m pip install --upgrade pip && \
    xvfb-run winpy -m pip install pyinstaller==6.3.0

WORKDIR /src

# The entrypoint will be handled by docker-compose
CMD ["bash"]
