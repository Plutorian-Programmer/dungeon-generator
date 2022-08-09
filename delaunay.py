import numpy as np
import math

class cl_graph():
    # data structure for a undericted graph

    def __init__(self):
        self.rooms = []
        self.edges = []
    
    def add_room(self, room):
        self.rooms.append(room)
    
    def del_room(self, room):
        self.rooms.remove(room)

    def add_connection(self, room_1, room_2):
        if room_1 not in self.rooms:
            raise ValueError("error room_1 does not exist")
        if room_2 not in self.rooms:
            raise ValueError("error room_2 does not exist")
        if room_1 == room_2:    
            raise ValueError("error both rooms are the same")
        if (room_1, room_2) in self.edges or (room_2, room_1) in self.edges:
            raise ValueError("warning trying to add an already existing connection")

        self.edges.append((room_1, room_2))
        room_1.add_connection(room_2)
        room_2.add_connection(room_1)


    def del_connection(self, room_1, room_2):
        # delete a connection whatever way it may exist
        if (room_1, room_2) in self.edges:
            self.edges.remove((room_1, room_2))
        elif (room_2, room_1) in self.edges:
            self.edges.remove((room_2, room_1))
        room_1.del_connection(room_2)
        room_2.del_connection(room_1)

    # special function to connect all rooms to each other
    def connect_all_rooms(self):
        for i, room_1 in enumerate(self.rooms):
            for room_2 in self.rooms[i+1:]:
                self.add_connection(room_1, room_2)

    def add_graph(self, graph):
        for room in graph.rooms:
            self.add_room(room)
        for edge in graph.edges:
            self.edges.append((edge[0], edge[1]))
    
    def edge_exist(self, room_1, room_2):
        if (room_1, room_2) in self.edges or (room_2, room_1) in self.edges:
            return True
        else:
            return False

def sort_rooms(rooms):
    pivot = rooms[-1]
    x_cord = pivot.x_cord
    y_cord = pivot.y_cord
    left = []
    right = []
    for room in rooms[:-1]:
        if room.x_cord < x_cord:
            left.append(room)
        elif room.x_cord > x_cord:
            right.append(room)
        elif room.y_cord < y_cord:
            left.append(room)
    if len(left) > 1:
        left = sort_rooms(left)
    if len(right) > 1:
        right = sort_rooms(right)

    return left + [pivot] + right

def get_equation(edge):
    s_vector = [edge[0].x_cord, edge[0].y_cord]
    d_vector = [edge[1].x_cord - edge[0].x_cord, edge[1].y_cord - edge[0].y_cord]
    vector_size = np.sqrt((d_vector[0])**2 + (d_vector[1])**2)

    d_vector[0] = d_vector[0] / vector_size
    d_vector[1] = d_vector[1] / vector_size
    return (s_vector, d_vector)

def get_intersection(vector_1, vector_2):
    a_1, b_1 = vector_1[0]
    c_1, d_1 = vector_1[1]
    a_2, b_2 = vector_2[0]
    c_2, d_2 = vector_2[1]
    
    if vector_1[1] == vector_2[1]:
        if c_1 == 0 and a_1 == a_2:
            return np.inf, np.inf
        elif d_1 == 0 and b_1 == b_2:
            return np.inf, np.inf
        elif (a_2 - a_1) / c_1 == (b_2 - b_1) / d_1:
            return np.inf, np.inf
        else:
            return -np.inf, -np.inf
    t = ( c_2 * (b_1 - b_2) - d_2 * (a_1 - a_2) ) / ( d_2 * c_1 - c_2 * d_1 )
    if c_2 != 0 and d_2 != 0:
        u_1 = (a_1 + c_1 * t - a_2) / c_2
        u_2 = (b_1 + d_1 * t - b_2) / d_2
        if u_1 != u_2:
            # if u_1 and u_2 are not equal there is no intersection
            return None
    return (a_1 + c_1 * t), (b_1 + d_1 * t)
    
def point_on_line(edge, point):
    # if the point is on the line its x and y cord will be bigger than one cord and smaller than the other cord
    # by multplying the difference between the point the borders of the edge we have to get a -1 if it is on the line.
    cord_1 = (edge[0].x_cord, edge[0].y_cord)
    cord_2 = (edge[1].x_cord, edge[1].y_cord)
    between_x = (point[0] >= cord_1[0] and point[0] <= cord_2[0]) or (point[0] >= cord_2[0] and point[0] <= cord_1[0])
    between_y = (point[1] >= cord_1[1] and point[1] <= cord_2[1]) or (point[1] >= cord_2[1] and point[1] <= cord_1[1])

    return between_x and between_y

def does_intersect(edge_1, edge_2):
    vector_1 = get_equation(edge_1)
    vector_2 = get_equation(edge_2)
    intersect = get_intersection(vector_1, vector_2)
    if intersect == None:
        return False
    elif intersect[0] < 0 or intersect[1] < 0:
        return False
    elif intersect == (np.inf, np.inf):
        # if the lines are parellel the intersect if one the end points of a line lies on the other line
        return point_on_line(edge_1, edge_2[0]) and point_on_line(edge_1, edge_2[1])
    
    if point_on_line(edge_1, intersect) and point_on_line(edge_2, intersect):
        print(intersect)
        return True
    return False

def find_lowest_room(graph, visited = []):
    possible_rooms = [room for room in graph.rooms if room not in visited]
    if possible_rooms == []:
        return None
    lowest_room = possible_rooms[0]
    for room in possible_rooms[1:]:
        if room.y_cord > lowest_room.y_cord:
            lowest_room = room
    return lowest_room

def find_base_lr(left, right, graph):
    visited_left = []
    visited_right = []
    lowest_left = find_lowest_room(left, visited_left)
    lowest_right = find_lowest_room(right, visited_right)
    # print("lowest two room found")
    while len(visited_left) != len(left.rooms) - 1 and len(visited_right) != len(right.rooms) - 1:
        base_edge = (lowest_left, lowest_right)
        intersect = False
        for edge in graph.edges:
            if lowest_right in edge or lowest_left in edge:
                continue
            if does_intersect(base_edge, edge):
                print("intersection")
                print(base_edge[0].room_number, base_edge[1].room_number)
                print(edge[0].room_number, edge[1].room_number)
                print(get_equation(base_edge))
                print(get_equation(edge))
                intersect = True
                break
        if not intersect:
            return (lowest_left, lowest_right)
        temp_lowest_left = find_lowest_room(left, visited_left+[lowest_left])
        temp_lowest_right = find_lowest_room(right, visited_right + [lowest_right])
        if temp_lowest_left == None and temp_lowest_right == None:
            raise ValueError("No base edge can be found")
        elif temp_lowest_left == None or temp_lowest_left.y_cord < temp_lowest_right.y_cord:
            visited_right += [lowest_right]
            lowest_right = temp_lowest_right
        else:
            visited_left += [lowest_left]
            lowest_left = temp_lowest_left
    
    raise ValueError("No base lr found")

def candidate_insert(candidate_list, candidate):
    if len(candidate_list) == 0: return [candidate]
    if len(candidate_list) == 1 and candidate_list[0][1] <= candidate[1]: return candidate_list + [candidate]
    elif len(candidate_list) == 1 and candidate_list[0][1] > candidate[1]: return [candidate] + candidate_list
    middle = int(np.floor((len(candidate_list)*0.5+0.5)))
    left = candidate_list[:middle]
    right = candidate_list[middle:]
    if left == [] and right[0][1] >= candidate[1]:
        return [candidate] + right
    elif left == [] and right[0][1] < candidate[1]:
        return candidate_insert(right, candidate)

    elif right == [] and left[0][1] <= candidate[1]:
        return left + [candidate]
    elif right == [] and left[0][1] > candidate[1]:
        return candidate_insert(left,candidate)

    elif left[-1][1] > candidate[1]:
        return candidate_insert(left, candidate) + right
    elif right[0][1] < candidate[1]:
        return left + candidate_insert(right, candidate)
    else: return left + [candidate] + right

def get_angle(room_1, room_2):
    base_room = room_1
    connected_room = room_2.copy()
    connected_room.x_cord -= base_room.x_cord
    connected_room.y_cord -= base_room.y_cord
    angle = math.atan2(connected_room.y_cord, connected_room.x_cord) % (2 * math.pi)
    return angle

def find_candidates(graph, base_room, connected_room):
    candidate_list = []
    angle_base = get_angle(base_room, connected_room)

    for room in graph.rooms:
        if room == base_room: continue
        if not graph.edge_exist(room, base_room): continue
        angle_candidate = get_angle(base_room, room)
        angle_edge = (angle_base-angle_candidate)%(2*math.pi)
        candidate_list = candidate_insert(candidate_list, (room, angle_edge))
    
    return candidate_list

def get_minor(cord,temp):
    matrix = []
    for row in temp[:cord[0]]:
        matrix.append(row[:cord[1]]+row[cord[1]+1:])
    for row in temp[cord[0]+1:]:
        matrix.append(row[:cord[1]]+row[cord[1]+1:])
    return matrix

def get_determinant(matrix):
    if len(matrix) == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]    
    else:
        A = matrix[0][0] * get_determinant(get_minor((0,0),matrix.copy()))
        B = matrix[0][1] * get_determinant(get_minor((0,1),matrix.copy()))
        C = matrix[0][2] * get_determinant(get_minor((0,2),matrix.copy()))
        return A-B+C

def get_circle(room_list):
    matrix = [[0,0,0,0]] + [[room.x_cord**2 + room.y_cord**2, room.x_cord, room.y_cord, 1] for room in room_list]
    M_11 = (get_minor((0,0),matrix))
    M_12 = (get_minor((0,1),matrix))
    M_13 = (get_minor((0,2),matrix))
    M_14 = (get_minor((0,3),matrix))
    if M_11 == 0:
        raise ValueError("Points lie on a line")
    x_0 = 0.5 * (get_determinant(M_12) / get_determinant(M_11))
    y_0 = -0.5 * (get_determinant(M_13) / get_determinant(M_11))
    r_squared = (x_0)**2 + (y_0)**2 + (get_determinant(M_14) / get_determinant(M_11))
    return x_0, y_0, r_squared

def euclidean_distance(point_1, point_2):
    return (point_1[0]-point_2[0])**2 + (point_1[1]-point_2[1])**2

def point_in_circle(circle,point):
    try:
        x_c, y_c, r_squared = get_circle(circle)
    except:
        return False
    distance = euclidean_distance((x_c,y_c),(point.x_cord, point.y_cord))
    if distance < r_squared:
        return True
    else:
        return False

def merge_graph(left, right):
    output = cl_graph()
    # combine two graphs into one graph
    output.add_graph(left)
    output.add_graph(right)
    base_edge = find_base_lr(left, right, output)
    # print("base edge found")
    candites_right = find_candidates(right, base_edge[1], base_edge[0])
    candites_left = find_candidates(left, base_edge[0], base_edge[1])[::1]
    output.add_connection(base_edge[0], base_edge[1])

    while True:
        # print(f"base edge: {base_edge[0].room_number, base_edge[1].room_number}" )
        candite_right = None
        for i, candidate in enumerate(candites_right):
            # print(f"canditate right: {candidate[0].room_number, candidate[1]}")
            if candidate[1] <= math.pi:
                break
            if i+1 < len(candites_right) and point_in_circle(base_edge+(candidate,), candites_right[i+1]):
                output.del_connection(base_edge[1],candidate)
                continue
            candite_right = candidate[0]
            break
        
        candite_left = None
        for i, candidate in enumerate(candites_left):
            # print(f"candidate left {candidate[0].room_number, candidate[1]}")
            if candidate[1] >= math.pi:
                break
            if i+1 < len(candites_left) and point_in_circle(base_edge+(candidate,), candites_left[i+1]):
                output.del_connection(base_edge[0],candidate)
                continue
            candite_left = candidate[0]
            break

        if candite_right == None and candite_left == None:
            break
        elif candite_right == None:
            output.add_connection(candite_left, base_edge[1])
            base_edge = (candite_left, base_edge[1])
        elif candite_left == None:
            output.add_connection(base_edge[0], candite_right)
            base_edge = (base_edge[0], candite_right)
        else:
            if point_in_circle(base_edge+(candite_right,),candite_left):
                output.add_connection(candite_left, base_edge[1])
                base_edge = (candite_left, base_edge[1])
            else:
                output.add_connection(base_edge[0], candite_right)
                base_edge = (base_edge[0], candite_right)
        candites_right = find_candidates(right, base_edge[1], base_edge[0])
        candites_left = find_candidates(left, base_edge[0], base_edge[1])[::1]
    
    return output


def create_delaunay(rooms):
    if len(rooms) <= 3:
        output = cl_graph()
        for room in rooms:
            output.add_room(room)
        output.connect_all_rooms()
        # print(output.rooms)
        # print(output.edges)
        # print("-"*69)
        return output

    pivot = int(np.floor((len(rooms)*0.5+0.5)))
    # print(pivot)
    left = create_delaunay(rooms[:pivot])
    right = create_delaunay(rooms[pivot:])
    # print("start merge")
    return merge_graph(left, right)


