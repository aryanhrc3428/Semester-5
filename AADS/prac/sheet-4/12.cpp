// Hash table with quadratic probing

#include <iostream>

const int TABLE_SIZE = 11;

void insert(int table[], int key) {
    int index = key % TABLE_SIZE;
    int i = 0;
    
    while (table[(index + i * i) % TABLE_SIZE] != -1 && i < TABLE_SIZE) {
        i++;
    }
    
    if (i == TABLE_SIZE) {
        std::cout << "Cannot insert, table full or probing failed.\n";
        return;
    }
    
    table[(index + i * i) % TABLE_SIZE] = key;
}

void printTable(int table[]) {
    for (int i = 0; i < TABLE_SIZE; ++i) {
        if (table[i] != -1) {
            std::cout << "Index " << i << ": " << table[i] << "\n";
        } else {
            std::cout << "Index " << i << ": Empty\n";
        }
    }
}

int main() {
    int table[TABLE_SIZE];
    for (int i = 0; i < TABLE_SIZE; ++i) {
        table[i] = -1;
    }

    insert(table, 10);
    insert(table, 21);
    insert(table, 32);
    insert(table, 43);
    
    printTable(table);

    return 0;
}