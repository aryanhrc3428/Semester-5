// Doubly Linked List (Insert, Delete, Traverse)

#include <iostream>

struct DNode {
    int data;
    DNode* prev;
    DNode* next;
};

void insertEnd(DNode*& head, int val) {
    DNode* newNode = new DNode{val, nullptr, nullptr};
    if (!head) {
        head = newNode;
        return;
    }
    DNode* temp = head;
    while (temp->next) temp = temp->next;
    temp->next = newNode;
    newNode->prev = temp;
}

void deleteNode(DNode*& head, int val) {
    if (!head) return;
    DNode* temp = head;
    
    while (temp && temp->data != val) {
        temp = temp->next;
    }
    
    if (!temp) return; 

    if (temp->prev) temp->prev->next = temp->next;
    else head = temp->next; 

    if (temp->next) temp->next->prev = temp->prev;

    delete temp;
}

void printList(DNode* head) {
    while (head) {
        std::cout << head->data << " <-> ";
        head = head->next;
    }
    std::cout << "NULL\n";
}

int main() {
    DNode* head = nullptr;
    insertEnd(head, 10);
    insertEnd(head, 20);
    insertEnd(head, 30);
    
    std::cout << "Doubly Linked List: ";
    printList(head);
    
    deleteNode(head, 20);
    
    std::cout << "After deleting 20: ";
    printList(head);

    return 0;
}