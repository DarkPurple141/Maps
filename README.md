# Maps
This is a sub-repository of some work I did on creating a map-generating framework. The code is pretty rough in parts; I was figuring it out as I went. I tried to clean it up toward the end with some success, although it's still far from optimised.

For more read this:
https://medium.com/@al_hinds/making-dem-maps-fa2187b70c8b#.744ldhpov

## Dependencies
+ Build is in Python 3
+ numpy, PIL are required for present build
  * pip3 install numpy, pillow will deliver the goods
  * pygame is only required for rendering, however this could be altered to matplot if required

## Usage
Voronoi.py is the core map generating code.
+ There's a setup() function which can take a number of different arguments based on the type of map, size, polygon count required. If you're just starting out, I'd suggest use the default setup function.

## Classes
The major classes are Corner, Point, Polygon, Triangle.
+ Polygons control terrain type and are the output from the core generation code.
+ Points/Corners hold some key pathing information, and are used for roads, rivers.
