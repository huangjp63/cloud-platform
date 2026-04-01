#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "md5_calculator.h"
#include "resource_monitor.h"
#include "file_processor.h"

namespace py = pybind11;

PYBIND11_MODULE(cloud_platform_cpp, m) {
    m.doc() = "Cloud Platform C++ high performance module";
    
    py::class_<ResourceInfo>(m, "ResourceInfo")
        .def_readonly("cpu_usage", &ResourceInfo::cpu_usage)
        .def_readonly("memory_usage", &ResourceInfo::memory_usage)
        .def_readonly("disk_usage", &ResourceInfo::disk_usage)
        .def_readonly("memory_total", &ResourceInfo::memory_total)
        .def_readonly("memory_used", &ResourceInfo::memory_used)
        .def_readonly("disk_total", &ResourceInfo::disk_total)
        .def_readonly("disk_used", &ResourceInfo::disk_used);
    
    py::class_<ResourceMonitor>(m, "ResourceMonitor")
        .def(py::init<>())
        .def("get_resource_info", &ResourceMonitor::getResourceInfo)
        .def("get_cpu_usage", &ResourceMonitor::getCpuUsage)
        .def("get_memory_usage", &ResourceMonitor::getMemoryUsage)
        .def("get_disk_usage", &ResourceMonitor::getDiskUsage);
    
    py::class_<MD5Calculator>(m, "MD5Calculator")
        .def_static("calculate_file", &MD5Calculator::calculate)
        .def_static("calculate_data", &MD5Calculator::calculate)
        .def_static("calculate_chunk", &MD5Calculator::calculateChunk);
    
    py::class_<ChunkInfo>(m, "ChunkInfo")
        .def_readonly("index", &ChunkInfo::index)
        .def_readonly("total", &ChunkInfo::total)
        .def_readonly("data", &ChunkInfo::data);
    
    py::class_<FileProcessor>(m, "FileProcessor")
        .def(py::init<size_t>(), py::arg("chunk_size") = 5 * 1024 * 1024)
        .def("split_file", &FileProcessor::splitFile)
        .def("merge_chunks", &FileProcessor::mergeChunks)
        .def("set_chunk_size", &FileProcessor::setChunkSize)
        .def("get_chunk_size", &FileProcessor::getChunkSize);
}
