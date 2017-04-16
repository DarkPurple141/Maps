#!/usr/bin/env python3

import random

"""
    Map generating code using voronoi polygons.

    Copyright (C) 2017 Alexander Walker Hinds

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 """

class Point:
    """docstring for Point."""
    def __init__(self,x,y,ide=-1):
        self.x = x
        self.y = y
        self.id = ide

    def midpoint(self,b):
        return Point(
        (self.x+b.x)//2,
        (self.y+b.y)//2)

    def get_cords(self):
        return (self.x,self.y)

    def distance(self,point):
        return ((self.y-point.y)**2+(self.x-point.x)**2)

    def __lt__(self, other):
        selfPriority = self.id
        otherPriority = self.id
        return selfPriority < otherPriority

class Corner(Point):
    def __init__(self,point):
        Point.__init__(self,point.x,point.y)
        self.elevation = None
        self.neighbours = set()
        self.v_neighbours = set()
        self.river = False
        self.city = False
        self.coast = False
        self.road = False

class Triangle:
    def __init__(self,a,b,c):
        self.a = a
        self.b = b
        self.c = c
        self.pts = [a,b,c]

    def centre(self):
        ab = self.a.midpoint(self.b)

        centx = int(self.c.x + 2*(ab.x-self.c.x)/3)
        centy = int(self.c.y + 2*(ab.y-self.c.y)/3)

        return Point(centx,centy)

def main():
    xp = []
    yp = []
    for i in range(3):
        xp.append(random.randrange(15))
        yp.append(random.randrange(15))

    points = []

    for i in range(3):
        points.append(Point(xp.pop(),yp.pop()))

    print([i.get_cords() for i in points])

    tri = Triangle(points.pop(),points.pop(),points.pop())

    mid = tri.centre()

    for y in range(15):
        for x in range(15):
            if (tri.a.x == x and tri.a.y == y):
                print('A',end="")
            elif (tri.b.x == x and tri.b.y == y):
                print('B',end="")
            elif (tri.c.x == x and tri.c.y == y):
                print('C',end="")
            elif (mid.x == x and mid.y == y):
                print(" .",end="")
            else:
                print(" ",end="")
        print("")

if __name__ == '__main__':
    main()
