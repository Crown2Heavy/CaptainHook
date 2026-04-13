FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wine \
    gcc \
    g++ \
    make \
    libasound2-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

ENV WINEDEBUG=-all
ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN pip install pyinstaller==6.3.0

CMD ["bash"]