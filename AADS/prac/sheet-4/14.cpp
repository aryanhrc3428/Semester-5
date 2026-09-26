// Hash table for strings with search function

#include <iostream>
#include <string>

const int TABLE_SIZE = 10;

struct StringNode {
    std::string key;
    StringNode* next;
};

int hashFunction(const std::string& str) {
    int hash = 0;
    for (int i = 0; i < str.length(); ++i) {
        hash = (hash * 31 + str[i]) % TABLE_SIZE;
    }
    return hash;
}

void insert(StringNode* table[], const std::string& key) {
    int index = hashFunction(key);
    StringNode* newNode = new StringNode{key, table[index]};
    table[index] = newNode;
}

bool search(StringNode* table[], const std::string& key) {
    int index = hashFunction(key);
    StringNode* temp = table[index];
    while (temp) {
        if (temp->key == key) {
            return true;
        }
        temp = temp->next;
    }
    return false;
}

int main() {
    StringNode* table[TABLE_SIZE] = {nullptr};

    insert(table, "apple");
    insert(table, "banana");
    insert(table, "orange");
    insert(table, "grape");

    std::string searchKey = "banana";
    if (search(table, searchKey)) {
        std::cout << searchKey << " found in the hash table.\n";
    } else {
        std::cout << searchKey << " not found.\n";
    }

    searchKey = "mango";
    if (search(table, searchKey)) {
        std::cout << searchKey << " found in the hash table.\n";
    } else {
        std::cout << searchKey << " not found.\n";
    }

    return 0;
}