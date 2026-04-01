#ifndef FILE_PROCESSOR_H
#define FILE_PROCESSOR_H

#include <string>
#include <vector>
#include <functional>

struct ChunkInfo {
    int index;
    int total;
    std::string data;
};

class FileProcessor {
public:
    FileProcessor(size_t chunkSize = 5 * 1024 * 1024);
    ~FileProcessor();
    
    std::vector<ChunkInfo> splitFile(const std::string& filepath);
    bool mergeChunks(const std::vector<std::string>& chunkPaths, const std::string& outputPath);
    void setChunkSize(size_t size);
    size_t getChunkSize() const;
    
private:
    size_t chunkSize_;
};

#endif
