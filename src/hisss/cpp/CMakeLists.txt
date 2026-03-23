cmake_minimum_required(VERSION 3.15)
project(hisss_link CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(MSVC)
    add_compile_options(/permissive-)
endif()

set(ALGLIB_SOURCES
    alglib/ap.cpp
    alglib/alglibinternal.cpp
    alglib/alglibmisc.cpp
    alglib/linalg.cpp
    alglib/solvers.cpp
    alglib/optimization.cpp
)

set(PROJECT_SOURCES
    source/battlesnake.cpp
    source/battlesnake_helper.cpp
    source/utils.cpp
    source/nash.cpp
    source/link.cpp
)

add_library(link SHARED ${PROJECT_SOURCES} ${ALGLIB_SOURCES})

target_include_directories(link PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/header
    ${CMAKE_CURRENT_SOURCE_DIR}/alglib
)

set_target_properties(link PROPERTIES POSITION_INDEPENDENT_CODE ON)

# -O3 for GCC/Clang, /O2 for MSVC
target_compile_options(link PRIVATE
    $<$<BOOL:${MSVC}>:/O2>
    $<$<NOT:$<BOOL:${MSVC}>>:-O3>
)

# Alglib: suppress warnings (mirrors hatch_build.py -w)
foreach(src IN LISTS ALGLIB_SOURCES)
    set_source_files_properties(${src} PROPERTIES
        COMPILE_FLAGS "$<IF:$<BOOL:${MSVC}>,/w,-w>")
endforeach()

# Project sources: enable -Wall (mirrors hatch_build.py -Wall)
foreach(src IN LISTS PROJECT_SOURCES)
    set_source_files_properties(${src} PROPERTIES
        COMPILE_FLAGS "$<IF:$<BOOL:${MSVC}>,/W3,-Wall>")
endforeach()

# Install to hisss/cpp/ so lib.py finds it at the expected path
# LIBRARY = .so/.dylib on Linux/macOS; RUNTIME = .dll on Windows
install(TARGETS link
    LIBRARY DESTINATION hisss/cpp
    RUNTIME DESTINATION hisss/cpp
)
