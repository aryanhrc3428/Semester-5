// Hash function for student records (Insert, Search, Delete)

#include <iostream>
#include <string>

const int TABLE_SIZE = 10;

enum Status { EMPTY, OCCUPIED, DELETED };

struct Student {
    int roll;
    std::string name;
    Status status;
};

int hashFunc(int roll) {
    return roll % TABLE_SIZE;
}

void insert(Student table[], int roll, const std::string& name) {
    int index = hashFunc(roll);
    int i = 0;
    
    while (table[(index + i) % TABLE_SIZE].status == OCCUPIED && i < TABLE_SIZE) {
        if (table[(index + i) % TABLE_SIZE].roll == roll) {
            std::cout << "Roll number already exists.\n";
            return;
        }
        i++;
    }
    
    if (i == TABLE_SIZE) {
        std::cout << "Hash table is full.\n";
        return;
    }
    
    int finalIndex = (index + i) % TABLE_SIZE;
    table[finalIndex].roll = roll;
    table[finalIndex].name = name;
    table[finalIndex].status = OCCUPIED;
}

int search(Student table[], int roll) {
    int index = hashFunc(roll);
    int i = 0;
    
    while (table[(index + i) % TABLE_SIZE].status != EMPTY && i < TABLE_SIZE) {
        if (table[(index + i) % TABLE_SIZE].status == OCCUPIED && table[(index + i) % TABLE_SIZE].roll == roll) {
            return (index + i) % TABLE_SIZE;
        }
        i++;
    }
    return -1;
}

void deleteStudent(Student table[], int roll) {
    int index = search(table, roll);
    if (index != -1) {
        table[index].status = DELETED;
        std::cout << "Student with roll " << roll << " deleted.\n";
    } else {
        std::cout << "Student not found.\n";
    }
}

int main() {
    Student table[TABLE_SIZE];
    for (int i = 0; i < TABLE_SIZE; ++i) {
        table[i].status = EMPTY;
    }

    insert(table, 101, "Alice");
    insert(table, 111, "Bob");
    insert(table, 121, "Charlie");

    int idx = search(table, 111);
    if (idx != -1) std::cout << "Found: " << table[idx].name << "\n";
    else std::cout << "Not found\n";

    deleteStudent(table, 111);
    
    idx = search(table, 111);
    if (idx != -1) std::cout << "Found: " << table[idx].name << "\n";
    else std::cout << "Not found\n";

    return 0;
}