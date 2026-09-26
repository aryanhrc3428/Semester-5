// Primary clustering in linear probing solved using double hashing

#include <iostream>

const int TABLE_SIZE = 11;
const int PRIME = 7;

void insertLinear(int table[], int key) {
    int index = key % TABLE_SIZE;
    int i = 0;
    while (table[(index + i) % TABLE_SIZE] != -1 && i < TABLE_SIZE) i++;
    if (i < TABLE_SIZE) table[(index + i) % TABLE_SIZE] = key;
}

void insertDouble(int table[], int key) {
    int h1 = key % TABLE_SIZE;
    int h2 = PRIME - (key % PRIME);
    int i = 0;
    while (table[(h1 + i * h2) % TABLE_SIZE] != -1 && i < TABLE_SIZE) i++;
    if (i < TABLE_SIZE) table[(h1 + i * h2) % TABLE_SIZE] = key;
}

void printTable(int table[]) {
    for (int i = 0; i < TABLE_SIZE; ++i) {
        if (table[i] != -1) std::cout << table[i] << " ";
        else std::cout << "- ";
    }
    std::cout << "\n";
}

int main() {
    int linearTable[TABLE_SIZE];
    int doubleTable[TABLE_SIZE];
    
    for (int i = 0; i < TABLE_SIZE; ++i) {
        linearTable[i] = -1;
        doubleTable[i] = -1;
    }

    int keys[] = {10, 21, 32, 43, 54};
    int numKeys = sizeof(keys) / sizeof(keys[0]);

    for (int i = 0; i < numKeys; ++i) {
        insertLinear(linearTable, keys[i]);
        insertDouble(doubleTable, keys[i]);
    }

    std::cout << "Linear Probing (Primary Clustering visible around index 10-3):\n";
    printTable(linearTable);

    std::cout << "\nDouble Hashing (Keys uniformly spread):\n";
    printTable(doubleTable);

    return 0;
}