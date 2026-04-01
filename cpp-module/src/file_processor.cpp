#include "file_processor.h"
#include <fstream>
#include <vector>

FileProcessor::FileProcessor(size_t chunkSize) : chunkSize_(chunkSize) {}

FileProcessor::~FileProcessor() {}

std::vector<ChunkInfo> FileProcessor::splitFile(const std::string& filepath) {
    std::vector<ChunkInfo> chunks;
    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    
    if (!file.is_open()) {
        return chunks;
    }
    
    std::streamsize fileSize = file.tellg();
    file.seekg(0, std::ios::beg);
    
    int totalChunks = (fileSize + chunkSize_ - 1) / chunkSize_;
    
    for (int i = 0; i < totalChunks; i++) {
        std::streamsize currentChunkSize = std::min(
            static_cast<std::streamsize>(chunkSize_),
            fileSize - static_cast<std::streamsize>(i * chunkSize_)
        );
        
        std::vector<char> buffer(currentChunkSize);
        file.read(buffer.data(), currentChunkSize);
        
        ChunkInfo chunk;
        chunk.index = i;
        chunk.total = totalChunks;
        chunk.data = std::string(buffer.begin(), buffer.end());
        chunks.push_back(chunk);
    }
    
    return chunks;
}

bool FileProcessor::mergeChunks(const std::vector<std::string>& chunkPaths, const std::string& outputPath) {
    std::ofstream outFile(outputPath, std::ios::binary);
    if (!outFile.is_open()) {
        return false;
    }
    
    for (const auto& chunkPath : chunkPaths) {
        std::ifstream chunkFile(chunkPath, std::ios::binary);
        if (!chunkFile.is_open()) {
            return false;
        }
        
        outFile << chunkFile.rdbuf();
    }
    
    return true;
}

void FileProcessor::setChunkSize(size_t size) {
    chunkSize_ = size;
}

size_t FileProcessor::getChunkSize() const {
    return chunkSize_;
}
