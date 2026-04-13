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

# Step 1: Initialize Wine
RUN wineboot --init && wineserver -w

# Step 2: Install Windows Python using the "Embeddable" Zip (Bypasses all GUI installers)
WORKDIR /python
RUN wget -q https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip && \
    unzip python-3.11.5-embed-amd64.zip && \
    rm python-3.11.5-embed-amd64.zip

# Step 3: Enable site-packages in the embeddable environment
# This is a special step for embeddable python to work like a normal one
RUN sed -i 's/#import site/import site/' python311._pth

# Step 4: Install pip for the Windows environment
RUN wget -q https://bootstrap.pypa.io/get-pip.py && \
    wine64 python.exe get-pip.py && \
    wineserver -w

# Step 5: Set up symlink so "winpy" points to our new Windows Python
RUN echo '#!/bin/bash\nwine64 /python/python.exe "$@"' > /usr/local/bin/winpy && \
    chmod +x /usr/local/bin/winpy

# Step 6: Pre-install PyInstaller
RUN winpy -m pip install pyinstaller==6.3.0 && wineserver -w

WORKDIR /src
CMD ["bash"]
