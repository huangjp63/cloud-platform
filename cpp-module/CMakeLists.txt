cmake_minimum_required(VERSION 3.14)
project(cloud_platform_cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG REQUIRED)

find_package(OpenSSL REQUIRED)

add_library(cloud_platform_cpp SHARED
    src/md5_calculator.cpp
    src/resource_monitor.cpp
    src/file_processor.cpp
    src/bindings.cpp
)

target_include_directories(cloud_platform_cpp PRIVATE
    ${CMAKE_SOURCE_DIR}/src
    ${OPENSSL_INCLUDE_DIR}
)

target_link_libraries(cloud_platform_cpp PRIVATE
    pybind11::module
    OpenSSL::SSL
    OpenSSL::Crypto
)

set_target_properties(cloud_platform_cpp PROPERTIES
    PREFIX ""
    OUTPUT_NAME "cloud_platform_cpp"
)
