#!/usr/local/bin/python3.5

import pygame, os, random, numpy, math, color_palettes, queue, name_gen, triangle
from pygame.locals import *
from geom import *
from PIL import ImageFilter, Image

class City:
    """docstring for City."""
    def __init__(self, location, name="default"):
        self.name = name
        self.location = location
        self.owner = random.randrange(10)

def __centre_dist_inc(origin,dest,centre):

    x1,y1 = origin.get_cords()
    x2,y2 = dest.get_cords()

    dista = (y1 -centre[1])**2+(x1-centre[0])**2
    distb = (y2 -centre[1])**2+(x2-centre[0])**2

    if distb > dista:
        return True
    else:
        return False

def _make_roads(city_sites):
    road_list = []
    candidates = {}
    count = 0

#for _ in range(3):
    for c in city_sites:
        ## find best candidate
        least = 1000000

        for a in city_sites:
            if c == a:
                continue
            try:
                if candidates[(c,a)]:
                    continue
            except KeyError:
                if c.distance(a) < least:
                    next_item = a
                    least = c.distance(a)
                    origin = c
                    re = True
                    for duplicate in city_sites:
                        if duplicate == c or duplicate == a:
                            continue
                        if (duplicate,c) in candidates:
                            if (duplicate.distance(a) + 10000) < least:
                                least = duplicate.distance(a)
                                next_item = a
                                origin = duplicate

        candidates[(c,next_item)] = 1
        candidates[(next_item,c)] = 1
        candidates[(origin,next_item)] = 1
        candidates[(next_item,origin)] = 1

        road_list.append(_best_road_route(origin,next_item))
        count+=1

    return road_list

def _best_road_route(origin,dest):

    pt_list = []
    q = queue.PriorityQueue()
    q.put((0,origin))
    came_from = {}
    cost_so_far = {}
    cost_so_far[origin] = 0
    came_from[origin] = None
    found = False

    while not q.empty():
        curr = q.get()[1]
        if curr == dest:
            found = True
            break

        for next_item in curr.v_neighbours:
            river_cost = alt_cost = 0
            if next_item.elevation < -0.8 or next_item.elevation > 6:
                continue
            elif came_from[curr] and next_item.river:
                if came_from[curr].river and curr.river:
                    continue
                else:
                    river_cost = 10
            elif next_item.elevation > curr.elevation:
                alt_cost = 5
            dist = next_item.distance(curr) + cost_so_far[curr] + river_cost + alt_cost
            if (next_item not in cost_so_far) or (dist < cost_so_far[next_item]):
                cost_so_far[next_item] = dist
                priority = dist + next_item.distance(dest)
                q.put((priority,next_item))
                came_from[next_item] = curr
    if found:
        curr = dest
        while curr != origin:
            pt_list.append(curr)
            curr = came_from[curr]
        pt_list.append(origin)

    return pt_list

def render_roads(road_list):
    for i in road_list:
        ptlist = [j.get_cords() for j in i]
        if len(ptlist) > 1:
            pygame.draw.lines(pygame.display.get_surface(), (120,88,20), False, ptlist, 2)

def _determine_terrain(count,poly_site,polygons,centre,max_dist):

    rivers = 2*count
    centrex,centrey = centre[0],centre[1]

    for p in polygons:
        p._add_neighbours(poly_site) # populates vertices with neighbour data
        if p.terrain == -2: # water terrain
            p.fresh_or_salt(poly_site)
            if p.terrain == 0: #lake terrain
                a = [i for i in p.get_neighbours(poly_site) if i.terrain <= 0]
                if not a:
                    p.terrain = 2
                    p.color = (50,150,0)
                elif len(a) > 2:
                    for i in p.get_neighbours(poly_site):
                        if i.terrain > 0 and not [j for j in i.get_neighbours(poly_site) if j.terrain < 0]:
                            i.terrain = 0
                            i.color = color_palettes.shallows[2]
    mountains = []
    for p in polygons:
        if (abs((p.centre.x-centrex)/max_dist) < .6 and abs((p.centre.y-centrey)/max_dist) < .5) or (
        (p.centre.x < (centrex - (5/8)*max_dist)) and (p.centre.y < (centrey - (5/8)*max_dist))
        ): #0.1
            if p.terrain == 2 and (len([i for i in p.get_neighbours(poly_site) if i.terrain <= 0]) == 0 and count > 0):
                mountains.append(p)
                p.make_mountain(poly_site)
                count -= 1

    # mountains
    for m in mountains:
        s = set()
        s.add(m)
        q = queue.Queue()
        q.put(m)

        while not q.empty():
            curr = q.get()
            fringe = [i for i in curr.get_neighbours(poly_site) if i.terrain > 1 and i not in s]
            while fringe:
                new = fringe.pop()
                if new.terrain >= 2 and new.terrain <= 11:
                    q.put(new)
                    s.add(new)
                    if new.terrain < 11 and curr.terrain > 2 and (new.terrain < curr.terrain):
                        new.terrain = curr.terrain-1
                        new.color = random.choice(color_palettes.terrain[10-new.terrain])

    # rivers
    river_sources = set()
    river_mouth = set()
    for p in polygons:
        if (p.terrain > 3 and p.terrain < 9) or p.terrain == 0:
            river_sources.add(p)
        for v in p.vertices:
            v.elevation = sum([i.terrain for i in v.neighbours])/len(v.neighbours)

    river_sources = list(river_sources)
    land = [p for p in polygons if p.terrain > 1]
    regions = []

    for i in range(4):
        while True:
            found = True
            candidate = random.choice(land).centre

            if ((candidate.x-centrex)**2 + (candidate.y-centrey)**2) < 100000:
                for r in regions:
                    if candidate.distance(r.location) < 70000:
                        found = False
                        break
            else:
                found = False

            if found:
                regions.append(name_gen.Region(location=candidate))
                break

    if river_sources:
        while rivers > 0:
            temp = random.choice(river_sources)
            if temp in river_mouth:
                continue
            else:
                river_mouth.add(temp)
                rivers-=1

        river_point_list = []
        while len(river_mouth):
            temp = river_mouth.pop()
            newriver = _make_river(temp,centre)
            if newriver:
                river_point_list.append(newriver)
            else:
                river_mouth.add(random.choice(river_sources))
        #return river_point_list

    else:
        return []

    city_count = 22
    potential_city = [i for river in river_point_list for i in river if i.elevation < 7]
    coast = [j for p in polygons for j in p.vertices if p.terrain >= 2 if j.elevation < 2]
    potential_city += coast

    city_sites = set()
    while potential_city and city_count > 0:
        temp = random.choice(potential_city)
        if temp not in city_sites:
            approved = True
            for i in city_sites:
                if temp.distance(i) < 8000: # NB distance isn't squarerooted for speed
                    approved = False
                    break

            if approved:
                least = regions[0].location.distance(temp)
                region = regions[0]
                for i in regions:
                    holding = i.location.distance(temp)
                    if holding < least:
                        least = holding
                        region = i
                temp.city = City(location=temp,name=region.regional_name())
                city_count -=1
                region.cities.append(temp)
                city_sites.add(temp)

    for i in coast:
        for j in i.neighbours:
            if j.terrain == -2:
                i.coast = True

    return river_point_list,city_sites,regions

def render_coast(coast_lines):
    ptlist = [j.get_cords() for j in coast_lines]
    pygame.draw.lines(pygame.display.get_surface(), color_palettes.sand[2], False, ptlist, 4)

def render_cities(city_sites,font):
    for i in city_sites:
        city = i.city
        x,y = i.get_cords()
        screen = pygame.display.get_surface()
        pygame.draw.rect(screen,(0,0,0),(x-8,y-8,16,16))
        toWrite = font.render(city.name, True, (30,30,30))
        w,h = toWrite.get_size()
        s = pygame.Surface((w,h ), pygame.SRCALPHA)   # per-pixel alpha
        s.fill((255,255,255,128))
        screen.blit(s,(x-28,y+12))
        screen.blit(toWrite,(x-28,y+12))

def render_regions(regions,font):
    for r in regions:
        x,y = r.location.get_cords()
        screen = pygame.display.get_surface()
        screen.blit((font.render(r.name, True, (30,30,30))),(x-16,y+8))

def _make_river(river_source,centre):
    seen = set()
    start = random.choice(river_source.vertices)
    seen.add(start)
    start.river = True
    river_list = []
    river_list.append(start)
    q = queue.Queue()
    q.put(start)

    exceptions = []

    while not q.empty():
        curr = q.get()
        next_item = None
        for v in curr.v_neighbours:
            if v in seen:
                continue
            seen.add(v)
            if v and ((v.elevation <= curr.elevation or ((curr.elevation<2) and v.elevation>4)) and __centre_dist_inc(curr,v,centre)) and (v.elevation >= 0):
                next_item = v

        if next_item:
            if len([i.terrain for i in next_item.neighbours if i.terrain <0]) > 1:
                break
            else:
                q.put(next_item)
                if next_item.river:
                    exceptions.append(next_item)
                next_item.river = True
                river_list.append(next_item)

    if len(river_list) < 11:
        for i in river_list:
            if i not in exceptions:
                i.river = False
        return


    return river_list

def render_rivers(river_list):
    for i in river_list:
        if len([j for j in i[0].neighbours if j.terrain == 0]) > 0:
            size = 6
        else:
            size = 4
        ptlist = [j.get_cords() for j in i]
        pygame.draw.lines(pygame.display.get_surface(), color_palettes.shallows[2], False, ptlist, size)

class Polygon:
    def __init__(self,vertices,site,neighbours):
        self.centre = site
        self.color = (site.x%256,site.y%256,(site.x*site.y)%256)
        self.neighbours = neighbours
        self.vertices = sorted(vertices,key=self.vertex_sort) # needs to be sorted
        self.terrain = None

    def draw (self):
        if len(self.vertices) <= 2:
            print("===============")
        else:
            pygame.draw.polygon(pygame.display.get_surface(),self.color,[i.get_cords() for i in self.vertices])
            #if self.terrain > 0:
            #    pygame.draw.polygon(pygame.display.get_surface(),color_palettes.simple_colours[11-self.terrain],[i.get_cords() for i in self.vertices])
            #else:
            #    pygame.draw.polygon(pygame.display.get_surface(),self.color,[i.get_cords() for i in self.vertices])

    def vertex_sort(self,b):
        x,y = self.centre.get_cords()
        px, py = b.get_cords()

        y = py-y
        x = px-x
        theta = numpy.arctan2(y, x)

        return theta

    def sea_or_land(self,centre,max_dist,island):

        x, y = self.centre.get_cords()
        point = (x - centre[0])/max_dist,(y - centre[1])/max_dist

        land = island.inside(point)

        if not land:
            self.terrain = -2
            self.color = random.choice(color_palettes.ocean)
        else:
            self.terrain = 2
            self.color = (50,150,0)

    def get_neighbours(self,PolygonList):
        return [PolygonList[i.get_cords()] for i in self.neighbours]

    def render(self,PolygonList):
        a = self.get_neighbours(PolygonList)
        land = [i.terrain for i in a if i.terrain >= 0]
        salt = [i for i in self.get_neighbours(PolygonList) if i.terrain < 0]

        if len([i for i in self.vertices if i.river == True])/len(self.vertices) > 0.88:
            if not salt:
                self.terrain = 0
                self.color = color_palettes.shallows[2]
        if self.terrain < 0 and land:
            self.terrain = -1
            #self.color = color_palettes.shallows[0]
        elif self.terrain > 0 and len(land) != len(a):
            #coast = [i for i in self.vertices if i.coast]
            #if len(coast) > 1:
            #    render_coast(coast)
            if self.terrain > 2:
                self.color = random.choice(color_palettes.cliff)
            else:
                self.terrain = 1
                #self.color = random.choice(color_palettes.sand)

    def inside_polygon(self, x, y):
        """
        Return True if a coordinate (x, y) is inside a polygon defined by
        a list of verticies [(x1, y1), (x2, x2), ... , (xN, yN)].

        Reference: http://www.ariel.com.au/a/python-point-int-poly.html
        """
        n = len(self.vertices)
        inside = False
        p1x, p1y = self.vertices[0].get_cords()
        for i in range(1, n + 1):
            p2x, p2y = self.vertices[i % n].get_cords()
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def fresh_or_salt(self,PolygonList):
        l = self.get_neighbours(PolygonList)
        sea_neighbours = [i for i in l if i.terrain < 0]

        lake_neighbours = [i for i in l if i.terrain == 0]

        if lake_neighbours:
            self.terrain = 0
            self.color = color_palettes.shallows[2]

        elif len(sea_neighbours) == len(l):
            self.terrain = -2
        else:
            count = 0
            seen = set()
            while True:
                temp = []
                for i in sea_neighbours:
                    if i in seen:
                        continue
                    if i.centre == self.centre:
                        continue
                    temp+=i.get_neighbours(PolygonList)
                    seen.add(i)

                temp = [i for i in temp if i.terrain < 0]

                if len(temp) == 0:
                    self.terrain = 0
                    self.color = color_palettes.shallows[2]
                    break
                else:
                    sea_neighbours+=temp
                count+=1
                if count > 7:
                    break

    def make_mountain(self,polyList):
        self.terrain = min(self.terrain+5, 11)
        self.color = random.choice(color_palettes.terrain[11-self.terrain])
        n = self.get_neighbours(polyList)
        for i in n:
            i.terrain = min(i.terrain+4,11)
            i.color = random.choice(color_palettes.terrain[11-i.terrain])

    def _add_neighbours(self,poly_site):
        for i in self.get_neighbours(poly_site):
            for a,v in enumerate(self.vertices):
                v.v_neighbours.add(self.__add_v_neighbour(a-1))
                v.v_neighbours.add(self.__add_v_neighbour(a+1))
                for b,c in enumerate(i.vertices):
                    if v == c:
                        v.neighbours.add(i)
                        c.neighbours.add(self)
                        v.v_neighbours.add(i.__add_v_neighbour(b-1))
                        v.v_neighbours.add(i.__add_v_neighbour(b+1))

    def __add_v_neighbour(self,a):
        try:
            return self.vertices[a]
        except IndexError:
            return self.vertices[0]

    def centroid(self):
        num = len(self.vertices)
        totalx = 0
        totaly = 0

        for v in self.vertices:
            totalx+=v.x
            totaly+=v.y

        return totalx//num,totaly//num


class Polygon_Dict:
    """docstring for Polygon Dict."""
    def __init__(self,PolygonList,PointRange):
        self.values = dict()
        self.max_x, self.max_y = PointRange
        self.__populate_dict(PolygonList)

    def __populate_dict(self,PolygonList):
        a=0
        for y in range(self.max_y):
            for x in range(self.max_x):
                if x > 0:
                    if self.get_polygon(x-1,y):
                        if self.get_polygon(x-1,y).inside_polygon(x,y):
                            self.values[x,y] = self.values[x-1,y]
                            continue

                if y > 0:
                    if self.get_polygon(x,y-1):
                        if self.get_polygon(x,y-1).inside_polygon(x,y):
                            self.values[x,y] = self.values[x,y-1]
                            continue

                for p in PolygonList:
                    if p.inside_polygon(x,y):
                        self.values[x,y] = p
                        break

                if '{},{}'.format(x,y) not in self.values:
                    a+=1
        print(a/(self.max_x*self.max_y))


    def get_polygon(self,x,y):
        try:
            return self.values[x,y]
        except KeyError:
            return False

class Floating:
    """docstring for Floating."""
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def update_state(self,newx,newy):
        self.x = newx
        self.y = newy
        pygame.draw.rect(pygame.display.get_surface(),(255,0,0),[newx,newy,32,32],0)

class Island:
    """docstring for Island."""
    def __init__(self,seed):
        random.seed(seed)
        self.ISLAND_FACTOR = 1.13 # 1.0 means no small islands; 2.0 leads to a lot
        self.bumps = random.randrange(1,7)
        self.startAngle = random.uniform(0,2*math.pi)
        self.dipAngle = random.uniform(0,2*math.pi)
        self.dipWidth = random.uniform(0.2,0.7)

    def inside(self,point):
        x, y = point # has to be 'relative' to centre not absolute point position
        point_length = (y**2+x**2)**.5 # from '0,0'
        angle = math.atan2(x,y) # from '0,0'
        length = 0.5* (max(abs(x)-.35,abs(y)) + point_length) #.5

        r1 = 0.5 + .4*math.sin(self.startAngle + self.bumps*angle + math.cos((self.bumps+3)*angle))
        r2  = 0.7 - .2*math.sin(self.startAngle + self.bumps*angle - math.sin((self.bumps+2)*angle))

        if (abs(angle - self.dipAngle) < self.dipWidth
            or abs(angle - self.dipAngle + 2*math.pi) < self.dipWidth
            or abs(angle - self.dipAngle - 2*math.pi) < self.dipWidth):
            r1 = r2 = .6 # 0.2 #0.9

        return (length < r1 or (length > r1*self.ISLAND_FACTOR and length < r2))

def setup(POLYGON_COUNT=4096,SCREEN_WIDTH=1152,SCREEN_HEIGHT=900,HUD_SIZE=32*9,
    main_island_shape_seed=800,small_island_shape_seed=300,improve_points=False,triangles=False):
    OFFSETX = int(0.04*SCREEN_WIDTH)
    OFFSETY = int(0.05*SCREEN_HEIGHT)
    polygons = []
    SECTION_SIZE = POLYGON_COUNT//80

    # this is for game use
    display_size = (SCREEN_WIDTH+HUD_SIZE, SCREEN_HEIGHT)

    # centre of the effective screen for map generation/display
    centre = tuple(map(int,((SCREEN_WIDTH+0.4*OFFSETX)/2,(SCREEN_HEIGHT+0.5*OFFSETY)/2)))

    # euclidean distance from diagonal map corner with a slight offset
    # larger max_dist will affect the size of the main island
    max_dist = int((centre[0]**2+centre[1]**2)**.5)-int(6.6*OFFSETX)

    # these are the polygon centres
    generator_sites = []
    for i in range(POLYGON_COUNT):
        while True:
            p = Point(
                random.randrange(-OFFSETX,SCREEN_WIDTH+OFFSETX),
                random.randrange(-OFFSETY,SCREEN_HEIGHT+OFFSETY),
                i)
            if not [i for i in generator_sites if i.x == p.x and i.y == p.y]:
                break
        generator_sites.append(
            p
        )

    # delaunay triangles provide co-ordinates of polygon vertices
    print("Generating delaunay triangles...")
    tris = triangle.delaunay([poly_centre.get_cords() for poly_centre in generator_sites])
    Triangles = [Triangle(generator_sites[i[0]],generator_sites[i[1]],generator_sites[i[2]]) for i in tris]

    # these are class based functions to retain a random seed. Useful for map generation
    # look at the Island Class for more information
    print("Generating island shapes...")
    island_shape = Island(main_island_shape_seed)
    smaller_island = Island(small_island_shape_seed)

    # polygons are the polygon objects, poly_sites is a useful look-up dict
    # for x,y co-ordinates matching a polygon
    print("Generating polygons...")
    if triangles:
        polygons, poly_sites = __alt_polygon_generator(Triangles,centre,max_dist,island_shape,smaller_island)
    else:
        polygons, poly_sites = __polygon_generator(generator_sites,Triangles,centre,max_dist,island_shape,smaller_island)

    if improve_points:
        generator_sites = []
        print("Improving points...")
        for counter,p in enumerate(polygons):
            x,y = p.centroid()
            generator_sites.append(
                Point(x,y,counter)
            )

        tris = triangle.delaunay([poly_centre.get_cords() for poly_centre in generator_sites])
        Triangles = [Triangle(generator_sites[i[0]],generator_sites[i[1]],generator_sites[i[2]]) for i in tris]
        if triangles:
            polygons, poly_sites = __alt_polygon_generator(Triangles,centre,max_dist,island_shape,smaller_island)
        else:
            polygons, poly_sites = __polygon_generator(generator_sites,Triangles,centre,max_dist,island_shape,smaller_island)
    ## this is arbitrary and can be changed however it appeared to work reasonably well
    # I've tried higher and lower.
    mount_count = POLYGON_COUNT//200

    # this is the main generator function and will determine most of the map terrain
    # see relevant function for more details
    print("Generating mountains, rivers and city locations...")
    river_list,city_sites,regions = _determine_terrain(mount_count,poly_sites,polygons,centre,max_dist)

    print("Generating roads...")
    road_list = _make_roads(city_sites)

    print("")
    print("Map created...")
    print("Key data:")
    print("mountains = ",mount_count)
    print("rivers = ",len(river_list))
    print("cities = ",len(city_sites))
    print("roads = ",len(road_list))

    # return data and render objects
    return display_size,polygons,poly_sites,river_list,city_sites,road_list,regions

def __alt_polygon_generator(triangles,centre,max_dist,island_shape,smaller_island):

    poly_vertex_dict = {}
    poly_site = {}
    polygons = []

    for a,t in enumerate(triangles):
        if a % 100 == 0:
            print(a)
        neighbours = []
        vertices = []
        mid = t.centre()
        for neighbour in triangles:
            if neighbour == t:
                continue
            for pt in neighbour.pts:
                if pt in t.pts:
                    if pt not in neighbours:
                        neighbours.append(neighbour.centre())

        for v in t.pts:
            x,y = v.get_cords()
            if (x,y) in poly_vertex_dict:
                newVert = poly_vertex_dict[(x,y)]
            else:
                newVert = Corner(v)
                poly_vertex_dict[(x,y)] = newVert

            vertices.append(newVert)
        if not vertices:
            continue

        p = Polygon(
            vertices,
            mid,
            neighbours
            )
        if (p.centre.x < centre[0]-(5/8)*max_dist) and (p.centre.y < centre[1]-(5/9)*max_dist):
            p.sea_or_land(
            (centre[0]-(5/9)*max_dist,centre[1]-(3/4)*max_dist),
            max_dist//(3.5),
            smaller_island
            )
        else:
            p.sea_or_land(centre,max_dist,island_shape)
        polygons.append(p)
        poly_site[mid.get_cords()]= p

    return polygons,poly_site

def __polygon_generator(sites,Triangles,centre,max_dist,island_shape,smaller_island):

    poly_vertex_dict = {}
    poly_site = {}
    polygons = []

    for site in sites:
        vertices = []
        neighbours = []
        for tri in Triangles:
            if site in tri.pts:
                x,y = tri.centre().get_cords()
                if (x,y) in poly_vertex_dict:
                    newVert = poly_vertex_dict[(x,y)]
                else:
                    newVert = Corner(tri.centre())
                    poly_vertex_dict[(x,y)] = newVert
                # poly vertex dict
                # if already exists
                vertices.append(newVert)
                [neighbours.append(i) for i in tri.pts if i is not site if i not in neighbours]

        if not vertices:
            continue

        p = Polygon(
            vertices,
            site,
            neighbours
            )
        if (p.centre.x < centre[0]-(5/8)*max_dist) and (p.centre.y < centre[1]-(5/9)*max_dist):
            p.sea_or_land(
            (centre[0]-(5/9)*max_dist,centre[1]-(3/4)*max_dist),
            max_dist//(3.5),
            smaller_island
            )
        else:
            p.sea_or_land(centre,max_dist,island_shape)
        polygons.append(p)
        poly_site[site.get_cords()]= p

    return polygons,poly_site

def simple_render(polygons,poly_sites,rivers,cities,roads,regions,font1,font2,flag=False):
    for p in polygons:
        if flag:
            p.render(poly_sites)
        p.draw()

    render_rivers(rivers)
    render_roads(roads)
    render_cities(cities,font1)
    render_regions(regions,font2)

def pre_render(polygons,poly_sites):
    for p in polygons:
        p.render(poly_sites)
        p.draw()

def v_fx(screen):
    dims = screen.get_size()
    im1 = pygame.image.tostring(screen,'RGB')
    im = Image.frombytes('RGB',(dims),im1)
    im1 = im.filter(ImageFilter.BLUR)
    im1.save('test.png','PNG')
    return pygame.image.load('test.png')

def pygame_demo_image():

    # this function is for demoing a default output
    size,polygons,poly_sites,rivers,cities,roads,regions = setup()
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode(size,pygame.RESIZABLE)
    pygame.display.set_caption('Map')
    city_font = pygame.font.SysFont('arial', 20)
    region_font = pygame.font.SysFont('arial', 30)

    simple_render(polygons,poly_sites,rivers,cities,roads,regions,city_font,region_font,flag=True)
    pygame.image.save(screen,'test.png')

    pygame.quit()


def testVoronoi():

    size,polygons,poly_site,river_list,city_sites,road_list,regions = setup(main_island_shape_seed=None)

    pygame.init()
    pygame.font.init()
    city_font = pygame.font.SysFont('cardinal', 20) #cardinal
    region_font = pygame.font.SysFont('cardinal', 30)

    GAMEOVER = False
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode(size,pygame.RESIZABLE)
    screen.fill((255,255,255))
    pygame.display.set_caption('Voronoi')
    pygame.draw.rect(screen,(255,0,0),[384,320,32,32],0)
    curr = Floating(384,320)

    poly = polyDict = False
    count = 0
    first = False
    pre_render(polygons,poly_site)
    render_rivers(river_list)
    render_roads(road_list)
    bg = v_fx(screen)
    while not GAMEOVER:
        # --- Main event loop for event handling
        action = False
        for e in pygame.event.get(): # User did something
            action = True
            if e.type == pygame.QUIT: # If user clicked close
                GAMEOVER = True
            elif e.type == pygame.MOUSEBUTTONUP:
                x,y = pygame.mouse.get_pos()
                found = False
                """
                for p in polygons:
                    if p.inside_polygon(x,y) and not found:
                        pts = [i.get_cords() for i in p.vertices]
                        pygame.draw.polygon(screen,(40,40,40),pts)
                        found = True
                    else:
                        p.draw()
                """
        if action:
            for p in polygons:
                p.draw()
            render_rivers(river_list)
            render_roads(road_list)
            render_cities(city_sites,city_font)
            render_regions(regions,region_font)

        pygame.display.update()
        #print(pygame.image.tostring(screen,"RGB"))
        # --- Limit to 5 frames per second
        clock.tick(5)

        if not polyDict:
            polyDict = not polyDict

    pygame.quit()

if __name__ == '__main__':
    #testVoronoi()
    pygame_demo_image()
