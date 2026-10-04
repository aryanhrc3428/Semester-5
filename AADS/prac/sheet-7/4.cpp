// Implement bellman ford

#include <iostream>
#include <vector>

using namespace std;

struct Edge {
    int src, dest, weight;
};

void bellmanFord(int V, int E, int source, const vector<Edge>& edges) {
    vector<int> dist(V, 1e9);
    dist[source] = 0;

    for (int i = 1; i <= V - 1; i++) {
        for (int j = 0; j < E; j++) {
            int u = edges[j].src;
            int v = edges[j].dest;
            int weight = edges[j].weight;

            if (dist[u] != 1e9 && dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
            }
        }
    }

    for (int j = 0; j < E; j++) {
        int u = edges[j].src;
        int v = edges[j].dest;
        int weight = edges[j].weight;
        if (dist[u] != 1e9 && dist[u] + weight < dist[v]) {
            cout << "Graph contains a negative weight cycle\n";
            return;
        }
    }

    cout << "Vertex\tDistance from Source\n";
    for (int i = 0; i < V; i++) {
        if (dist[i] == 1e9) cout << i << "\tINF\n";
        else cout << i << "\t" << dist[i] << "\n";
    }
}

int main() {
    int V, E;
    cout << "Enter number of vertices and edges: ";
    cin >> V >> E;

    vector<Edge> edges(E);
    cout << "Enter " << E << " edges (source destination weight):\n";
    for (int i = 0; i < E; i++) {
        cin >> edges[i].src >> edges[i].dest >> edges[i].weight;
    }

    int source;
    cout << "Enter the source vertex: ";
    cin >> source;

    bellmanFord(V, E, source, edges);

    return 0;
}