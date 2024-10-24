#include <gtest/gtest.h>
extern "C" {
#include "hashmap.h"
}

// Test insertion operation
TEST(HashMapTest, InsertOperation)
{
    HashMap* map = (HashMap*)calloc(1, sizeof(HashMap));

    // Insert a key-value pair
    hashmap_put(map, "key1", (void*)1);
    EXPECT_EQ((size_t)hashmap_get(map, "key1"), 1);

    // Insert another key-value pair
    hashmap_put(map, "key2", (void*)2);
    EXPECT_EQ((size_t)hashmap_get(map, "key2"), 2);

    // Check if the inserted keys exist
    EXPECT_EQ((size_t)hashmap_get(map, "key1"), 1);
    EXPECT_EQ((size_t)hashmap_get(map, "key2"), 2);

    free(map);
}

// Test inserting a duplicate key
TEST(HashMapTest, InsertDuplicateKey)
{
    HashMap* map = (HashMap*)calloc(1, sizeof(HashMap));

    // Insert a key-value pair
    hashmap_put(map, "key", (void*)1);
    EXPECT_EQ((size_t)hashmap_get(map, "key"), 1);

    // Insert the same key again, the value should be updated
    hashmap_put(map, "key", (void*)2);
    EXPECT_EQ((size_t)hashmap_get(map, "key"), 2);

    free(map);
}

// Test deletion operation
TEST(HashMapTest, DeleteOperation)
{
    HashMap* map = (HashMap*)calloc(1, sizeof(HashMap));

    // Insert a key-value pair
    hashmap_put(map, "key", (void*)1);
    EXPECT_EQ((size_t)hashmap_get(map, "key"), 1);

    // Delete the key
    hashmap_delete(map, "key");
    EXPECT_EQ(hashmap_get(map, "key"), nullptr); // Should return nullptr after deletion

    free(map);
}

// Test deletion of a non-existent key
TEST(HashMapTest, DeleteNonExistentKey)
{
    HashMap* map = (HashMap*)calloc(1, sizeof(HashMap));

    // Try to delete a non-existent key
    hashmap_delete(map, "no_such_key"); // Should not crash or produce an error
    EXPECT_EQ(hashmap_get(map, "no_such_key"), nullptr); // Should still return nullptr

    free(map);
}

// Test get operation
TEST(HashMapTest, GetOperation)
{
    HashMap* map = (HashMap*)calloc(1, sizeof(HashMap));

    // Insert a key-value pair
    hashmap_put(map, "key", (void*)1);
    EXPECT_EQ((size_t)hashmap_get(map, "key"), 1); // Check if it can be retrieved correctly

    // Delete the key
    hashmap_delete(map, "key");
    EXPECT_EQ(hashmap_get(map, "key"), nullptr); // Should return nullptr after deletion

    free(map);
}

// Test getting a non-existent key
TEST(HashMapTest, GetNonExistentKey)
{
    HashMap* map = (HashMap*)calloc(1, sizeof(HashMap));

    // Try to get a non-existent key
    EXPECT_EQ(hashmap_get(map, "no_such_key"), nullptr); // Should return nullptr

    free(map);
}

// Test boundary case: inserting a null key
// TEST(HashMapTest, InsertNullKey) {
//     HashMap *map = (HashMap *)calloc(1, sizeof(HashMap));

//     // Insert a null key
//     hashmap_put(map, nullptr, (void *)1);
//     EXPECT_EQ(hashmap_get(map, nullptr), (void *)1); // Should be able to retrieve the null key

//     // Delete the null key
//     hashmap_delete(map, nullptr);
//     EXPECT_EQ(hashmap_get(map, nullptr), nullptr); // Should return nullptr after deletion

//     free(map);
// }

// Test boundary case: very large key
TEST(HashMapTest, LargeKey)
{
    HashMap* map = (HashMap*)calloc(1, sizeof(HashMap));

    const char* largeKey = "a very large key that exceeds typical lengths for a hash map key...";
    hashmap_put(map, largeKey, (void*)1);
    EXPECT_EQ((size_t)hashmap_get(map, largeKey), 1);

    free(map);
}

// Test the limits of the hash table: continuous insertion
TEST(HashMapTest, LimitTest)
{
    HashMap* map = (HashMap*)calloc(1, sizeof(HashMap));

    for (int i = 0; i < 10000; i++) {
        hashmap_put(map, format("key %d", i), (void*)(size_t)i);
    }

    for (int i = 0; i < 10000; i++) {
        EXPECT_EQ((size_t)hashmap_get(map, format("key %d", i)), (size_t)i);
    }

    free(map);
}

// Run all tests
int main(int argc, char** argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
