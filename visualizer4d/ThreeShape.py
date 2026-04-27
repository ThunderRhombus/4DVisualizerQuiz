import math as m
from Graph import Graph

class ThreeShape:
    @staticmethod
    def _identity_matrix(size):
        matrix = [[0.0] * size for _ in range(size)]
        for i in range(size):
            matrix[i][i] = 1.0
        return matrix

    @staticmethod
    def _multiply_matrices(A, B):
        rows_A, cols_A = len(A), len(A[0])
        rows_B, cols_B = len(B), len(B[0])
        if cols_A != rows_B:
            raise ValueError("Incompatible dimensions")
        C = [[0.0] * cols_B for _ in range(rows_A)]
        for i in range(rows_A):
            for j in range(cols_B):
                for k in range(cols_A):
                    C[i][j] += A[i][k] * B[k][j]
        return C

    @staticmethod
    def _multiply_matrix_vector(A, v):
        return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]

    def __init__(self, size):
        self.size = size
        self.v = [list()]    
        self.edges = Graph()
        self.faces = Graph()
        self.rv = []
    
    def rotate(self, yaw, pitch, roll):
        yaw = m.radians(yaw)
        pitch = m.radians(pitch)
        roll = m.radians(roll)
        cp, sp = m.cos(pitch), m.sin(pitch)
        cy, sy = m.cos(yaw), m.sin(yaw)
        cr, sr = m.cos(roll), m.sin(roll)

        Rx = self._identity_matrix(3)
        Rx[1][1], Rx[1][2], Rx[2][1], Rx[2][2] = cr, -sr, sr, cr

        Ry = self._identity_matrix(3)
        Ry[0][0], Ry[0][2], Ry[2][0], Ry[2][2] = cp, sp, -sp, cp

        Rz = self._identity_matrix(3)
        Rz[0][0], Rz[0][1], Rz[1][0], Rz[1][1] = cy, -sy, sy, cy
        
        A = self._multiply_matrices(self._multiply_matrices(Rz, Ry), Rx)
        self.rv = []
        for p in self.v:
            self.rv.append(self._multiply_matrix_vector(A, list(p)))
    
    def get_hind_most(self):
        h = 0
        for i in range(1, len(self.rv)):
            if(self.rv[i][2] < self.rv[h][2]):
                h = i
        return h

    def get_next_targets(self, vfrom, vat):
        next_targets = []
        for vto in self.g.neighbors(vat):
            if(vto != vfrom):
                next_targets.append(vto)
        return next_targets
    
    


        
        
        
