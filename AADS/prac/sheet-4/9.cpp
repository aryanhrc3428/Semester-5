// Split a circular linked list into two halves

#include <iostream>

struct Node {
    int data;
    Node* next;
};

void insertEnd(Node*& head, int val) {
    Node* newNode = new Node{val, nullptr};
    if (!head) {
        head = newNode;
        newNode->next = head;
        return;
    }
    Node* temp = head;
    while (temp->next != head) {
        temp = temp->next;
    }
    temp->next = newNode;
    newNode->next = head;
}

void splitCircularList(Node* head, Node*& head1, Node*& head2) {
    if (!head) return;

    Node* slow = head;
    Node* fast = head;

    while (fast->next != head && fast->next->next != head) {
        fast = fast->next->next;
        slow = slow->next;
    }

    if (fast->next->next == head) {
        fast = fast->next;
    }

    head1 = head;
    if (head->next != head) {
        head2 = slow->next;
    } else {
        head2 = nullptr;
    }

    fast->next = head2;
    slow->next = head1;
}

void printCircularList(Node* head) {
    if (!head) return;
    Node* temp = head;
    do {
        std::cout << temp->data << " -> ";
        temp = temp->next;
    } while (temp != head);
    std::cout << "(HEAD: " << head->data << ")\n";
}

int main() {
    Node* head = nullptr;
    Node *head1 = nullptr, *head2 = nullptr;

    insertEnd(head, 1);
    insertEnd(head, 2);
    insertEnd(head, 3);
    insertEnd(head, 4);
    insertEnd(head, 5);

    std::cout << "Original Circular List: ";
    printCircularList(head);

    splitCircularList(head, head1, head2);

    std::cout << "First Half: ";
    printCircularList(head1);
    
    std::cout << "Second Half: ";
    printCircularList(head2);

    return 0;
}