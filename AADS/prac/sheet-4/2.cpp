// Implement a sequence using a linked list

#include <iostream>

struct Node {
    int data;
    Node* next;
};

void insertFront(Node*& head, int val) {
    Node* newNode = new Node;
    newNode->data = val;
    newNode->next = head;
    head = newNode;
}

void insertEnd(Node*& head, int val) {
    Node* newNode = new Node;
    newNode->data = val;
    newNode->next = nullptr;
    
    if (head == nullptr) {
        head = newNode;
        return;
    }
    
    Node* temp = head;
    while (temp->next != nullptr) {
        temp = temp->next;
    }
    temp->next = newNode;
}

void reverseList(Node*& head) {
    Node* prev = nullptr;
    Node* current = head;
    Node* next = nullptr;
    
    while (current != nullptr) {
        next = current->next;
        current->next = prev;
        prev = current;
        current = next;
    }
    head = prev;
}

void printList(Node* head) {
    while (head != nullptr) {
        std::cout << head->data << " -> ";
        head = head->next;
    }
    std::cout << "NULL\n";
}

int main() {
    Node* head = nullptr;

    insertEnd(head, 10);
    insertEnd(head, 20);
    insertFront(head, 5);
    insertEnd(head, 30);

    std::cout << "Original List: ";
    printList(head);

    reverseList(head);

    std::cout << "Reversed List: ";
    printList(head);

    return 0;
}