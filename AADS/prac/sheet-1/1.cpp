#include <iostream>
#include <vector>
using namespace std;

/* 1. Write a program to implement following vector operations: at(i), insert (i,e), erase(i,e), set(i,e), push_back(), pop_back(). */

void printVector(const string& operation, const vector<int>& vec) {
    cout << operation << ": [ ";
    for (int val : vec) {
        cout << val << " ";
    }
    cout << "]\n\n";
}

int main() {
    vector<int> v;
    cout << "=== Vector Operations Demonstration ===\n\n";

    // 1. push_back(e) - Adds an element to the end
    v.push_back(10);
    v.push_back(20);
    v.push_back(30);
    v.push_back(40);
    v.push_back(50);
    printVector("1. After push_back (added 10, 20, 30, 40, 50)", v);

    // 2. pop_back() - Removes the last element
    v.pop_back();
    printVector("2. After pop_back (removed last element)", v);

    // 3. at(i) - Accesses the element at index i (throws an error if out of bounds)
    cout << "3. Using at(i): Element at index 2 is " << v.at(2) << "\n\n";

    // 4. set(i, e) - C++ uses assignment to set a new value at an index
    // Setting element at index 1 to 99
    v.at(1) = 99; // Alternately, you can use: v[1] = 99;
    printVector("4. After 'set(1, 99)' via v.at(1) = 99", v);

    // 5. insert(i, e) - Inserts element 'e' at index 'i'
    // C++ requires an iterator (v.begin() + i) rather than just an integer
    int insertIndex = 2;
    int insertValue = 100;
    v.insert(v.begin() + insertIndex, insertValue);
    printVector("5. After 'insert(2, 100)'", v);

    // 6. erase(i) - Erases an element at a specific index
    int eraseIndex = 3;
    v.erase(v.begin() + eraseIndex);
    printVector("6a. After 'erase(3)' (removed element at index 3)", v);

    // 6b. erase(start, end) - Erases a range of elements from start to end (exclusive)
    // erasing from index 1 up to index 3 (erases index 1 and 2)
    int start = 1;
    int end = 3;
    v.erase(v.begin() + start, v.begin() + end);
    printVector("6b. After 'erase(1, 3)' (removed range from index 1 up to 3)", v);

    return 0;
}