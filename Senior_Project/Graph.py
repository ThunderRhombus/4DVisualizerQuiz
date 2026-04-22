class Graph:
    def __init__(self):
        self.adj = {}
        self.lastlink = 0

    def add_vertex(self, v):
        if v not in self.adj:
            self.adj[v] = set()

    def add_link(self, vertices):
        self.lastlink += 1
        self.add_vertex(-self.lastlink)
        for v in vertices:
            self.add_vertex(v)
            self.adj[v].add(-self.lastlink)
            self.adj[-self.lastlink].add(v)

    def remove_link(self, link):
        for v in self.adj[link]:
            if link in self.adj[v]:
                self.adj[link].remove(v)
                self.adj[v].remove(link)
                return

    def neighbors(self, v):
        return self.adj[v].copy()