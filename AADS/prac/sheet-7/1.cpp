// Implement standard trie

#include <iostream>
#include <string>
#include <vector>

using namespace std;

class TrieNode {
public:
    TrieNode* children[26];
    bool isTerminal;

    TrieNode() {
        isTerminal = false;
        for (int i = 0; i < 26; i++) {
            children[i] = nullptr;
        }
    }
};

class Trie {
private:
    TrieNode* root;

public:
    Trie() {
        root = new TrieNode();
    }

    void insert(const string& word) {
        TrieNode* curr = root;
        for (char c : word) {
            int index = c - 'a';
            if (!curr->children[index]) {
                curr->children[index] = new TrieNode();
            }
            curr = curr->children[index];
        }
        curr->isTerminal = true;
    }

    bool search(const string& word) {
        TrieNode* curr = root;
        for (char c : word) {
            int index = c - 'a';
            if (!curr->children[index]) {
                return false;
            }
            curr = curr->children[index];
        }
        return curr->isTerminal;
    }
};

int main() {
    Trie trie;
    int n, q;
    
    cout << "Enter the number of words to insert: ";
    cin >> n;
    cout << "Enter " << n << " words:\n";
    for (int i = 0; i < n; i++) {
        string word;
        cin >> word;
        trie.insert(word);
    }

    cout << "Enter the number of search queries: ";
    cin >> q;
    cout << "Enter " << q << " queries:\n";
    for (int i = 0; i < q; i++) {
        string word;
        cin >> word;
        if (trie.search(word)) {
            cout << word << " found in Trie.\n";
        } else {
            cout << word << " not found in Trie.\n";
        }
    }

    return 0;
}