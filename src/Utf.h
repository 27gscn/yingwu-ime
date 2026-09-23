#pragma once

#include <string>

namespace hengma {

std::string WideToUtf8(const std::wstring& value);
std::wstring Utf8ToWide(const std::string& value);

}  // namespace hengma
