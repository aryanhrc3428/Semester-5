// Singly Linked List (Insert, Delete, Traverse)

#include <iostream>

struct Node {
    int data;
    Node* next;
};

void insertFront(Node*& head, int val) {
    Node* newNode = new Node{val, head};
    head = newNode;
}

void insertEnd(Node*& head, int val) {
    Node* newNode = new Node{val, nullptr};
    if (!head) {
        head = newNode;
        return;
    }
    Node* temp = head;
    while (temp->next) temp = temp->next;
    temp->next = newNode;
}

void insertPos(Node*& head, int val, int pos) {
    if (pos == 0) {
        insertFront(head, val);
        return;
    }
    Node* temp = head;
    for (int i = 0; i < pos - 1 && temp; ++i) {
        temp = temp->next;
    }
    if (!temp) return;
    Node* newNode = new Node{val, temp->next};
    temp->next = newNode;
}

void deleteFront(Node*& head) {
    if (!head) return;
    Node* temp = head;
    head = head->next;
    delete temp;
}

void deleteEnd(Node*& head) {
    if (!head) return;
    if (!head->next) {
        delete head;
        head = nullptr;
        return;
    }
    Node* temp = head;
    while (temp->next->next) temp = temp->next;
    delete temp->next;
    temp->next = nullptr;
}

void deletePos(Node*& head, int pos) {
    if (pos == 0) {
        deleteFront(head);
        return;
    }
    Node* temp = head;
    for (int i = 0; i < pos - 1 && temp && temp->next; ++i) {
        temp = temp->next;
    }
    if (!temp || !temp->next) return;
    Node* toDelete = temp->next;
    temp->next = temp->next->next;
    delete toDelete;
}

void printList(Node* head) {
    while (head) {
        std::cout << head->data << " -> ";
        head = head->next;
    }
    std::cout << "NULL\n";
}

int main() {
    Node* head = nullptr;
    insertEnd(head, 10);
    insertFront(head, 5);
    insertEnd(head, 30);
    insertPos(head, 20, 2); 
    
    std::cout << "After Insertions: ";
    printList(head);

    deleteFront(head);
    deleteEnd(head);
    deletePos(head, 0); 
    
    std::cout << "After Deletions: ";
    printList(head);

    return 0;
}