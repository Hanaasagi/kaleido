cmake_minimum_required(VERSION 3.28)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(HashMap C CXX)

include_directories(include)

add_library(hashmap src/hashmap.c)

find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

enable_testing()

set(TEST_OUTPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/tests/build")
file(MAKE_DIRECTORY ${TEST_OUTPUT_DIR})

add_executable(test_hashmap tests/test_hashmap.cpp)

set_target_properties(test_hashmap PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${TEST_OUTPUT_DIR}
)

target_link_libraries(test_hashmap hashmap ${GTEST_LIBRARIES} pthread)

add_test(NAME test_hashmap COMMAND test_hashmap)

add_custom_target(format
    COMMAND find ${CMAKE_SOURCE_DIR} -name '*.c' -o -name '*.h' | xargs clang-format -i --style=WebKit
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Formatting C and H files with clang-format"
)

# clangd
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
