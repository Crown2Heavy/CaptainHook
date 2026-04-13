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

# Step 2: Install Windows Python using the "Embeddable" Zip
WORKDIR /python
RUN wget -q https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip && \
    unzip python-3.11.5-embed-amd64.zip && \
    rm python-3.11.5-embed-amd64.zip

# Step 3: Enable site-packages in the embeddable environment
RUN sed -i 's/#import site/import site/' python311._pth

# Step 4: Install pip for the Windows environment
# Using "wine" instead of "wine64" as it is the standard wrapper in Bookworm
RUN wget -q https://bootstrap.pypa.io/get-pip.py && \
    wine python.exe get-pip.py && \
    wineserver -w

# Step 5: Set up symlink so "winpy" points to our Windows Python
RUN echo '#!/bin/bash\nwine /python/python.exe "$@"' > /usr/local/bin/winpy && \
    chmod +x /usr/local/bin/winpy

# Step 6: Install PyInstaller and dependencies
# We use winpy to ensure everything goes into the Windows environment
RUN winpy -m pip install --upgrade pip && \
    winpy -m pip install pyinstaller==6.3.0 && \
    wineserver -w

WORKDIR /src
CMD ["bash"]
