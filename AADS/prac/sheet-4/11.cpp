// Hash table using division method and linear probing

#include <iostream>

const int TABLE_SIZE = 10;

void insert(int table[], int key) {
    int index = key % TABLE_SIZE;
    int i = 0;
    
    while (table[(index + i) % TABLE_SIZE] != -1 && i < TABLE_SIZE) {
        i++;
    }
    
    if (i == TABLE_SIZE) {
        std::cout << "Table is full.\n";
        return;
    }
    
    table[(index + i) % TABLE_SIZE] = key;
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

    insert(table, 15);
    insert(table, 25);
    insert(table, 35);
    insert(table, 12);
    insert(table, 22);

    printTable(table);

    return 0;
}