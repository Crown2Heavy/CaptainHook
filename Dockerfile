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
    && rm -rf /var/lib/apt/lists/*

# Set up Wine environment
ENV WINEDEBUG=-all
ENV WINEPREFIX=/wine
ENV WINEARCH=win64

# Step 1: Initialize Wine
RUN wineboot --init && wineserver -w

# Step 2: Install Windows Python (Embeddable version - No GUI needed)
WORKDIR /wine/drive_c/Python311
RUN wget -q https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip && \
    unzip python-3.11.5-embed-amd64.zip && \
    rm python-3.11.5-embed-amd64.zip

# Step 3: Enable site-packages in the embeddable build
# We need to uncomment the site-packages line in the ._pth file
RUN sed -i 's/#import site/import site/g' python311._pth

# Step 4: Install pip
RUN wget -q https://bootstrap.pypa.io/get-pip.py && \
    wine python.exe get-pip.py && \
    wineserver -w && \
    rm get-pip.py

# Step 5: Add Python to Wine PATH
ENV WINEPATH="C:\Python311;C:\Python311\Scripts"

# Step 6: Install essential build tools & dependencies
# Pre-install heavy dependencies to cache them in the image
RUN wine python.exe -m pip install --upgrade pip && \
    wine python.exe -m pip install \
    pyinstaller==6.3.0 \
    discord.py \
    aiohttp \
    mss \
    psutil \
    pyautogui \
    pynput \
    ping3 \
    rich \
    pyttsx3 \
    cryptography==38.0.4 \
    && wineserver -w

WORKDIR /src
CMD ["bash"]
