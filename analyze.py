from Cube import Cube
from Edge import Edge

cube=Cube(100)
remaining_vertices=set(range(len(cube.v)))

def branchpoint(p,vleft):
    newedges=set()
    if p in vleft:
        for e in cube.edges.neighbors(p):
            for n in cube.edges.neighbors(e):
                if n!=p and n in vleft:
                    newedges.add((p,n,e))
        vleft.remove(p)
    return newedges

print('initial remaining_vertices',remaining_vertices)
p=0
edges=branchpoint(p,remaining_vertices)
print('branch from',p,'->',edges)
print('remaining_vertices now',remaining_vertices)
print('total links',cube.edges.lastlink)

print('neighbors for each vertex:')
for i in range(len(cube.v)):
    print(i, cube.edges.neighbors(i))
