#include "resource_monitor.h"
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
#else
#include <unistd.h>
#include <sys/statvfs.h>
#endif

ResourceMonitor::ResourceMonitor() {}

ResourceMonitor::~ResourceMonitor() {}

ResourceInfo ResourceMonitor::getResourceInfo() {
    ResourceInfo info;
    info.cpu_usage = getCpuUsage();
    info.memory_usage = getMemoryUsage();
    info.disk_usage = getDiskUsage();
    info.memory_total = getTotalMemory();
    info.memory_used = getUsedMemory();
    info.disk_total = getTotalDisk();
    info.disk_used = getUsedDisk();
    return info;
}

double ResourceMonitor::getCpuUsage() {
#ifdef _WIN32
    static unsigned long long prevTotal = 0, prevIdle = 0;
    
    FILETIME idleTime, kernelTime, userTime;
    GetSystemTimes(&idleTime, &kernelTime, &userTime);
    
    unsigned long long idle = ((unsigned long long)idleTime.dwHighDateTime << 32) | idleTime.dwLowDateTime;
    unsigned long long kernel = ((unsigned long long)kernelTime.dwHighDateTime << 32) | kernelTime.dwLowDateTime;
    unsigned long long user = ((unsigned long long)userTime.dwHighDateTime << 32) | userTime.dwLowDateTime;
    
    unsigned long long total = kernel + user;
    unsigned long long totalDiff = total - prevTotal;
    unsigned long long idleDiff = idle - prevIdle;
    
    prevTotal = total;
    prevIdle = idle;
    
    if (totalDiff == 0) return 0.0;
    return 100.0 * (1.0 - (double)idleDiff / totalDiff);
#else
    std::ifstream file("/proc/stat");
    std::string line;
    std::getline(file, line);
    
    std::istringstream iss(line);
    std::string cpu;
    long user, nice, system, idle, iowait, irq, softirq;
    iss >> cpu >> user >> nice >> system >> idle >> iowait >> irq >> softirq;
    
    long total = user + nice + system + idle + iowait + irq + softirq;
    static long prevTotal = 0, prevIdle = 0;
    
    double usage = 0.0;
    if (prevTotal > 0) {
        long totalDiff = total - prevTotal;
        long idleDiff = idle - prevIdle;
        if (totalDiff > 0) {
            usage = 100.0 * (1.0 - (double)idleDiff / totalDiff);
        }
    }
    
    prevTotal = total;
    prevIdle = idle;
    return usage;
#endif
}

double ResourceMonitor::getMemoryUsage() {
    long total = getTotalMemory();
    long used = getUsedMemory();
    if (total == 0) return 0.0;
    return 100.0 * used / total;
}

double ResourceMonitor::getDiskUsage() {
    long total = getTotalDisk();
    long used = getUsedDisk();
    if (total == 0) return 0.0;
    return 100.0 * used / total;
}

long ResourceMonitor::getTotalMemory() {
#ifdef _WIN32
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    GlobalMemoryStatusEx(&status);
    return status.ullTotalPhys / 1024 / 1024;
#else
    auto memInfo = parseMemInfo();
    return memInfo["MemTotal"];
#endif
}

long ResourceMonitor::getUsedMemory() {
#ifdef _WIN32
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    GlobalMemoryStatusEx(&status);
    return (status.ullTotalPhys - status.ullAvailPhys) / 1024 / 1024;
#else
    auto memInfo = parseMemInfo();
    return memInfo["MemTotal"] - memInfo["MemAvailable"];
#endif
}

long ResourceMonitor::getTotalDisk() {
#ifdef _WIN32
    ULARGE_INTEGER totalBytes;
    GetDiskFreeSpaceExA(NULL, NULL, &totalBytes, NULL);
    return totalBytes.QuadPart / 1024 / 1024 / 1024;
#else
    struct statvfs stat;
    if (statvfs("/", &stat) != 0) return 0;
    return (stat.f_blocks * stat.f_frsize) / 1024 / 1024 / 1024;
#endif
}

long ResourceMonitor::getUsedDisk() {
#ifdef _WIN32
    ULARGE_INTEGER totalBytes, freeBytes;
    GetDiskFreeSpaceExA(NULL, &freeBytes, &totalBytes, NULL);
    return (totalBytes.QuadPart - freeBytes.QuadPart) / 1024 / 1024 / 1024;
#else
    struct statvfs stat;
    if (statvfs("/", &stat) != 0) return 0;
    return ((stat.f_blocks - stat.f_bfree) * stat.f_frsize) / 1024 / 1024 / 1024;
#endif
}

std::map<std::string, long> ResourceMonitor::parseMemInfo() {
    std::map<std::string, long> result;
#ifndef _WIN32
    std::ifstream file("/proc/meminfo");
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string key;
        long value;
        std::string unit;
        iss >> key >> value >> unit;
        key = key.substr(0, key.size() - 1);
        result[key] = value / 1024;
    }
#endif
    return result;
}
