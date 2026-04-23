#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <cctype>

static std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> out;
    std::stringstream ss(line);
    std::string token;
    while (std::getline(ss, token, ',')) {
        out.push_back(token);
    }
    return out;
}

static std::string normalize_col(std::string c) {
    for (char& ch : c) {
        if (ch >= 'A' && ch <= 'Z') ch = static_cast<char>(ch + 32);
        if (!(std::isalnum(static_cast<unsigned char>(ch)))) ch = '_';
    }
    std::string out;
    out.reserve(c.size());
    bool prev_us = false;
    for (char ch : c) {
        if (ch == '_') {
            if (!prev_us) out.push_back(ch);
            prev_us = true;
        } else {
            out.push_back(ch);
            prev_us = false;
        }
    }
    while (!out.empty() && out.front() == '_') out.erase(out.begin());
    while (!out.empty() && out.back() == '_') out.pop_back();
    return out;
}

static double parse_num(const std::string& x) {
    if (x.empty() || x == "?" || x == "NA" || x == "NaN") return std::numeric_limits<double>::quiet_NaN();
    try {
        return std::stod(x);
    } catch (...) {
        return std::numeric_limits<double>::quiet_NaN();
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: risk_profile <input_csv>\n";
        return 1;
    }

    std::ifstream in(argv[1]);
    if (!in.is_open()) {
        std::cerr << "Cannot open: " << argv[1] << "\n";
        return 1;
    }

    std::string header;
    if (!std::getline(in, header)) {
        std::cerr << "Empty CSV\n";
        return 1;
    }

    auto cols = split_csv_line(header);
    int age_idx = -1, biopsy_idx = -1;
    for (size_t i = 0; i < cols.size(); ++i) {
        std::string c = normalize_col(cols[i]);
        if (c == "age") age_idx = static_cast<int>(i);
        if (c == "biopsy") biopsy_idx = static_cast<int>(i);
    }

    if (age_idx < 0 || biopsy_idx < 0) {
        std::cerr << "Required columns age/biopsy not found\n";
        return 1;
    }

    std::string line;
    long long rows = 0;
    double age_sum = 0.0;
    long long age_n = 0;
    double biopsy_sum = 0.0;
    long long biopsy_n = 0;

    while (std::getline(in, line)) {
        auto vals = split_csv_line(line);
        if (static_cast<int>(vals.size()) <= std::max(age_idx, biopsy_idx)) continue;
        rows += 1;

        double age = parse_num(vals[age_idx]);
        double biopsy = parse_num(vals[biopsy_idx]);

        if (!std::isnan(age)) {
            age_sum += age;
            age_n += 1;
        }
        if (!std::isnan(biopsy)) {
            biopsy_sum += biopsy;
            biopsy_n += 1;
        }
    }

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "{\n";
    std::cout << "  \"rows\": " << rows << ",\n";
    std::cout << "  \"age_mean\": " << (age_n ? age_sum / age_n : 0.0) << ",\n";
    std::cout << "  \"biopsy_rate\": " << (biopsy_n ? biopsy_sum / biopsy_n : 0.0) << "\n";
    std::cout << "}\n";

    return 0;
}
