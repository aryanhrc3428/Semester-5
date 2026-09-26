// Hash table using chaining with linked lists

#include <iostream>

const int TABLE_SIZE = 7;

struct Node {
    int data;
    Node* next;
};

void insert(Node* table[], int key) {
    int index = key % TABLE_SIZE;
    Node* newNode = new Node{key, table[index]};
    table[index] = newNode;
}

void printTable(Node* table[]) {
    for (int i = 0; i < TABLE_SIZE; ++i) {
        std::cout << "Index " << i << ": ";
        Node* temp = table[i];
        while (temp) {
            std::cout << temp->data << " -> ";
            temp = temp->next;
        }
        std::cout << "NULL\n";
    }
}

int main() {
    Node* table[TABLE_SIZE] = {nullptr};

    insert(table, 10);
    insert(table, 17);
    insert(table, 24);
    insert(table, 5);
    insert(table, 12);

    printTable(table);

    return 0;
}