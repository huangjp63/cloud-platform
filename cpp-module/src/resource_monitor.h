#ifndef RESOURCE_MONITOR_H
#define RESOURCE_MONITOR_H

#include <string>
#include <map>

struct ResourceInfo {
    double cpu_usage;
    double memory_usage;
    double disk_usage;
    long memory_total;
    long memory_used;
    long disk_total;
    long disk_used;
};

class ResourceMonitor {
public:
    ResourceMonitor();
    ~ResourceMonitor();
    
    ResourceInfo getResourceInfo();
    double getCpuUsage();
    double getMemoryUsage();
    double getDiskUsage();
    
private:
    long getTotalMemory();
    long getUsedMemory();
    long getTotalDisk();
    long getUsedDisk();
    std::map<std::string, long> parseMemInfo();
};

#endif
