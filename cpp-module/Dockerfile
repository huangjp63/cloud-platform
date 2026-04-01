FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pybind11

COPY . .

RUN mkdir build && cd build && cmake .. && make

CMD ["python3", "-c", "import cloud_platform_cpp; print('C++ module loaded successfully')"]
