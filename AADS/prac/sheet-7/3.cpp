// Implement sufix trie

#include <iostream>
#include <string>
#include <unordered_map>

using namespace std;

class SuffixNode {
public:
    unordered_map<char, SuffixNode*> children;
};

class SuffixTrie {
private:
    SuffixNode* root;
    char endSymbol;

    void insertSuffix(int index, const string& str) {
        SuffixNode* curr = root;
        for (int i = index; i < str.length(); i++) {
            char c = str[i];
            if (curr->children.find(c) == curr->children.end()) {
                curr->children[c] = new SuffixNode();
            }
            curr = curr->children[c];
        }
        curr->children[endSymbol] = nullptr; 
    }

public:
    SuffixTrie(const string& str) {
        root = new SuffixNode();
        endSymbol = '*';
        populateSuffixTrie(str);
    }

    void populateSuffixTrie(const string& str) {
        for (int i = 0; i < str.length(); i++) {
            insertSuffix(i, str);
        }
    }

    bool contains(const string& substring) {
        SuffixNode* curr = root;
        for (char c : substring) {
            if (curr->children.find(c) == curr->children.end()) {
                return false;
            }
            curr = curr->children[c];
        }
        return true; 
    }
};

int main() {
    string text;
    cout << "Enter the main string to build the Suffix Trie: ";
    cin >> text;

    SuffixTrie trie(text);

    int q;
    cout << "Enter number of substring queries: ";
    cin >> q;
    
    cout << "Enter queries:\n";
    for (int i = 0; i < q; i++) {
        string query;
        cin >> query;
        if (trie.contains(query)) {
            cout << "'" << query << "' is a substring.\n";
        } else {
            cout << "'" << query << "' is NOT a substring.\n";
        }
    }

    return 0;
}