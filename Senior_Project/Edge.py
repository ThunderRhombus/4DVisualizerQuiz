class Edge:
    def __init__(self, v1, i1, v2, i2, link):
        self.source = v1.copy()
        self.source_index = i1
        self.target = v2.copy()
        self.target_index = i2
        self.link_index = link
        if v2[2] == v1[2]:
            self.dxdz = 0
            self.dydz = 0
            self.dwdz = 0
        else:
            self.dxdz = (v2[0] - v1[0]) / (v2[2] - v1[2])
            self.dydz = (v2[1] - v1[1]) / (v2[2] - v1[2])
            if len(v1) > 3 and len(v2) > 3:
                self.dwdz = (v2[3] - v1[3]) / (v2[2] - v1[2])
            else:
                self.dwdz = 0
        self.at = v1.copy()

    def moveto(self, z):
        if(z >= self.target[2]):
            self.at = self.target.copy()
            return self.at
        self.at[0] = self.at[0] + self.dxdz * (z - self.at[2])
        self.at[1] = self.at[1] + self.dydz * (z - self.at[2])
        if len(self.at) > 3:
            self.at[3] = self.at[3] + self.dwdz * (z - self.at[2])
        self.at[2] = z
        return self.at