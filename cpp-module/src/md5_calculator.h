#ifndef MD5_CALCULATOR_H
#define MD5_CALCULATOR_H

#include <string>
#include <vector>

class MD5Calculator {
public:
    static std::string calculate(const std::string& filepath);
    static std::string calculate(const std::vector<unsigned char>& data);
    static std::string calculateChunk(const std::vector<unsigned char>& chunk);
};

#endif
