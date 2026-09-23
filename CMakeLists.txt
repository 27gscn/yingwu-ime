cmake_minimum_required(VERSION 3.24)
project(YingwuIME VERSION 0.57.0 LANGUAGES CXX RC)

if(NOT WIN32 OR NOT MSVC)
  message(FATAL_ERROR "HengmaNative currently requires Windows and MSVC.")
endif()

if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  set(YINGWU_ARCH x64)
else()
  set(YINGWU_ARCH x86)
endif()

set(YINGWU_LIBRIME_ROOT
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/librime/${YINGWU_ARCH}/dist"
    CACHE PATH "Extracted librime SDK root for the active architecture")
set(RIME_INCLUDE_DIR "${YINGWU_LIBRIME_ROOT}/include")
set(RIME_RUNTIME "${YINGWU_LIBRIME_ROOT}/lib/rime.dll")

foreach(required IN ITEMS "${RIME_INCLUDE_DIR}/rime_api.h"
                          "${RIME_RUNTIME}")
  if(NOT EXISTS "${required}")
    message(FATAL_ERROR
      "Missing librime dependency: ${required}. Run scripts/fetch-librime.ps1.")
  endif()
endforeach()

set(YINGWU_SOURCES
  src/CandidateWindow.cpp
  src/Compartment.cpp
  src/Composition.cpp
  src/Diagnostics.cpp
  src/DllMain.cpp
  src/EndComposition.cpp
  src/Globals.cpp
  src/InputMode.cpp
  src/KeyEventSink.cpp
  src/KeyHandler.cpp
  src/Register.cpp
  src/RimeEngine.cpp
  src/Server.cpp
  src/TextEditSink.cpp
  src/TextService.cpp
  src/ThreadMgrEventSink.cpp
  src/Utf.cpp
  src/YingwuTSF.rc
  src/YingwuTSF.def)

add_library(YingwuTSF SHARED ${YINGWU_SOURCES})
target_compile_features(YingwuTSF PRIVATE cxx_std_17)
target_include_directories(YingwuTSF PRIVATE src "${RIME_INCLUDE_DIR}")
target_compile_definitions(YingwuTSF PRIVATE
  UNICODE _UNICODE NOMINMAX WIN32_LEAN_AND_MEAN
  WINVER=0x0A00 _WIN32_WINNT=0x0A00)
target_compile_options(YingwuTSF PRIVATE
  /utf-8 /W4 /EHsc /permissive- /Zc:__cplusplus)
target_link_libraries(YingwuTSF PRIVATE
  ole32 oleaut32 uuid advapi32 shell32 user32 gdi32)
set_target_properties(YingwuTSF PROPERTIES
  OUTPUT_NAME "YingwuTSF"
  PREFIX ""
  # Static CRT keeps the installer independent of a separate VC redist.
  MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

add_custom_command(TARGET YingwuTSF POST_BUILD
  COMMAND "${CMAKE_COMMAND}" -E copy_if_different
          "${RIME_RUNTIME}" "$<TARGET_FILE_DIR:YingwuTSF>/rime.dll"
  COMMENT "Copying librime runtime")

install(TARGETS YingwuTSF RUNTIME DESTINATION "${YINGWU_ARCH}")
install(FILES "${RIME_RUNTIME}" DESTINATION "${YINGWU_ARCH}")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/data/" DESTINATION data
        FILES_MATCHING PATTERN "*.yaml")
install(FILES README.md LICENSE-CODE.txt THIRD_PARTY_NOTICES.md
        DESTINATION docs)
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/docs/" DESTINATION docs
        FILES_MATCHING PATTERN "*.md")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/licenses/"
        DESTINATION docs/licenses)
