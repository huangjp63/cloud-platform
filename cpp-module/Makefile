CXX = g++
CXXFLAGS = -std=c++17 -O3 -fPIC
PYTHON_INCLUDE = $(shell python3 -c "import sysconfig; print(sysconfig.get_path('include'))")
PYBIND11_INCLUDE = $(shell python3 -c "import pybind11; print(pybind11.get_include())")
OPENSSL_INCLUDE = /usr/include/openssl
OPENSSL_LIBS = -lssl -lcrypto

SRC_DIR = src
BUILD_DIR = build

SOURCES = $(SRC_DIR)/md5_calculator.cpp $(SRC_DIR)/resource_monitor.cpp $(SRC_DIR)/file_processor.cpp $(SRC_DIR)/bindings.cpp

all: $(BUILD_DIR)/cloud_platform_cpp.so

$(BUILD_DIR)/cloud_platform_cpp.so: $(SOURCES)
	mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -I$(PYTHON_INCLUDE) -I$(PYBIND11_INCLUDE) -I$(SRC_DIR) \
	-shared -o $@ $^ $(OPENSSL_LIBS)

clean:
	rm -rf $(BUILD_DIR)

.PHONY: all clean
