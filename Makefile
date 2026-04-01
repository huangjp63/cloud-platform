.PHONY: all install dev build clean docker-up docker-down docker-build docker-logs

all: install

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cd cpp-module && mkdir -p build && cd build && cmake .. && make

dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	cd frontend && npm run dev

build:
	cd backend && docker build -t cloud-platform-backend .
	cd frontend && docker build -t cloud-platform-frontend .
	cd cpp-module && docker build -t cloud-platform-cpp .
	cd spark-jobs && docker build -t cloud-platform-spark .

clean:
	rm -rf backend/__pycache__
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf cpp-module/build

docker-up:
	cd deploy/docker && docker-compose up -d

docker-down:
	cd deploy/docker && docker-compose down

docker-build:
	cd deploy/docker && docker-compose build

docker-logs:
	cd deploy/docker && docker-compose logs -f

test:
	cd backend && pytest
	cd frontend && npm run test
