// Detect and remove a cycle in a linked list

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

void detectAndRemoveCycle(Node* head) {
    if (!head || !head->next) return;

    Node* slow = head;
    Node* fast = head;
    bool hasCycle = false;

    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) {
            hasCycle = true;
            break;
        }
    }

    if (hasCycle) {
        slow = head;
        if (slow == fast) {
            while (fast->next != slow) {
                fast = fast->next;
            }
        } else {
            while (slow->next != fast->next) {
                slow = slow->next;
                fast = fast->next;
            }
        }
        fast->next = nullptr;
        std::cout << "Cycle detected and removed.\n";
    } else {
        std::cout << "No cycle detected.\n";
    }
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
    insertEnd(head, 1);
    insertEnd(head, 2);
    insertEnd(head, 3);
    insertEnd(head, 4);
    insertEnd(head, 5);

    head->next->next->next->next->next = head->next->next; 

    detectAndRemoveCycle(head);

    std::cout << "List after cycle removal: ";
    printList(head);

    return 0;
}