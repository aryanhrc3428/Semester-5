// Concatenate two linked lists

#include <iostream>

struct Node {
    int data;
    Node* next;
};

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

Node* concatenate(Node* head1, Node* head2) {
    if (!head1) return head2;
    Node* temp = head1;
    while (temp->next) {
        temp = temp->next;
    }
    temp->next = head2;
    return head1;
}

void printList(Node* head) {
    while (head) {
        std::cout << head->data << " -> ";
        head = head->next;
    }
    std::cout << "NULL\n";
}

int main() {
    Node* list1 = nullptr;
    Node* list2 = nullptr;

    insertEnd(list1, 1);
    insertEnd(list1, 2);
    
    insertEnd(list2, 3);
    insertEnd(list2, 4);

    Node* result = concatenate(list1, list2);

    std::cout << "Concatenated List: ";
    printList(result);

    return 0;
}