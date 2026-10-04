// Implement complex trie

#include <iostream>
#include <string>
#include <unordered_map>

using namespace std;

class ComplexNode {
public:
    unordered_map<char, ComplexNode*> children;
    int wordsEndingHere = 0;
    int prefixesThroughHere = 0;
};

class ComplexTrie {
private:
    ComplexNode* root;

public:
    ComplexTrie() {
        root = new ComplexNode();
    }

    void insert(const string& word) {
        ComplexNode* curr = root;
        for (char c : word) {
            if (curr->children.find(c) == curr->children.end()) {
                curr->children[c] = new ComplexNode();
            }
            curr = curr->children[c];
            curr->prefixesThroughHere++;
        }
        curr->wordsEndingHere++;
    }

    int countWordsEqualTo(const string& word) {
        ComplexNode* curr = root;
        for (char c : word) {
            if (curr->children.find(c) == curr->children.end()) return 0;
            curr = curr->children[c];
        }
        return curr->wordsEndingHere;
    }

    void erase(const string& word) {
        if (countWordsEqualTo(word) == 0) return;
        
        ComplexNode* curr = root;
        for (char c : word) {
            curr = curr->children[c];
            curr->prefixesThroughHere--;
        }
        curr->wordsEndingHere--;
    }
};

int main() {
    ComplexTrie trie;
    int choice;
    string word;

    cout << "1. Insert\n2. Count Words\n3. Erase\n4. Exit\n";
    while (true) {
        cout << "Enter choice: ";
        cin >> choice;

        if (choice == 1) {
            cin >> word;
            trie.insert(word);
        } else if (choice == 2) {
            cin >> word;
            cout << "Count: " << trie.countWordsEqualTo(word) << "\n";
        } else if (choice == 3) {
            cin >> word;
            trie.erase(word);
        } else {
            break;
        }
    }

    return 0;
}