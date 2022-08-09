import numpy as np
import random
from delaunay import create_delaunay, get_angle, sort_rooms
from minimal_graph import create_minimal_graph
import math

class cl_corridor():

    def __init__(self,start,end):
        self.start_cord = start
        self.end_cord = end
        self.dir = "N"
        if start[0] == end[0]:
            if start[1] > end[1]:
                self.dir = "N"
            else:
                self.dir = "S"
        else:
            if start[0] > end[0]:
                self.dir = "W"
            else:
                self.dir = "E"
class cl_room:

    def __init__(self,x_cord,y_cord,width,height):
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.width = width
        self.height = height
        self.room_number = 0
        self.connections = []

    def add_connection(self,room):
        if room not in self.connections:
            self.connections.append(room)
        else:
            raise ValueError("Connection already exists")
    
    def del_connection(self,room):
        if room in self.connections:
            self.connections.remove(room)

    def copy(self):
        copy_room = cl_room(self.x_cord, self.y_cord, self.width,self.height)
        copy_room.room_number = self.room_number
        copy_room.connections = self.connections
        return copy_room

class cl_dungeon:
    
    def __init__(self, width, height):
        # self.map = np.zeros(shape=(height,width))
        self.height = height
        self.width = width
        self.rooms = []
        self.corridors = []
    
    def add_room(self,new_room):
        for room in self.rooms:
            dis_x = abs(room.x_cord - new_room.x_cord)
            dis_y = abs(room.y_cord - new_room.y_cord)
            if dis_x <= (room.width + new_room.width) and dis_y <= (room.height + new_room.height):
                return
        if new_room.x_cord - new_room.width < 0 or new_room.x_cord + new_room.width >= self.width:
            return
        if new_room.y_cord - new_room.height < 0 or new_room.y_cord + new_room.height >= self.height:
            return
        new_room.room_number = len(self.rooms)
        self.rooms.append(new_room)
    
    def add_corridor(self, corridor):
        self.corridors.append(corridor)
    
    def room_to_str(self, map_array):
        for room in self.rooms:
            if room.room_number < 10:
                map_array[room.y_cord][room.x_cord] = f"{room.room_number}"
            else:
                map_array[room.y_cord][room.x_cord] = f"{int(room.room_number/10)}"
                map_array[room.y_cord][room.x_cord+1] = f"{room.room_number%10}"
            left = room.x_cord - room.width
            right = room.x_cord + room.width
            up = room.y_cord - room.height
            down = room.y_cord + room.height
            for i in range(left,right+1):
                map_array[up][i] = "#"
                map_array[down][i] = "#"
            for i in range(up,down+1):
                map_array[i][left] = "#"
                map_array[i][right] = "#"
        
    
    def corridor_to_str(self, map_array):
        for corridor in self.corridors:
            # print(corridor.dir)
            begin = corridor.start_cord
            end = corridor.end_cord
            x_cord_b = begin[0]
            y_cord_b = begin[1]
            x_cord_e = end[0]
            y_cord_e = end[1]
            map_array[y_cord_b][x_cord_b] = "B"
            map_array[y_cord_e][x_cord_e] = "E"
            if corridor.dir == "N": 
                for i in range(y_cord_e+1, y_cord_b-1):
                    map_array[i][x_cord_b] = "|"            
            elif corridor.dir == "S":
                # print(end_cord)
                # print(y_cord)
                for i in range(y_cord_b+1, y_cord_e-1):
                    map_array[i][x_cord_b] = "|"
            elif corridor.dir == "E": 
                for i in range(x_cord_b+1,x_cord_e-1):
                    map_array[y_cord_b][i] = "-"
            elif corridor.dir == "W":
                # print(end_cord)
                # print(x_cord)
                for i in range(x_cord_e+1,x_cord_b-1):
                    map_array[y_cord_b][i] = "-"

    def map_to_str(self):
        map_array = [["." for i in range(self.width)] for j in range(self.height)]
        # map_array += [[f"{i}" for i in range(self.width)]]
        self.room_to_str(map_array)
        self.corridor_to_str(map_array)
        map_string = ""
        for i, item in enumerate(map_array):
            map_string += "".join(item)
            map_string += f"{i}"
            map_string += "\n"
        return map_string

    def print_dungeon(self):
        print(self.map_to_str(), end="")
    
    def save_map(self, file_name = "temp_file.txt"):
        with open(file_name, "w") as f:
            f.write(self.map_to_str()[:-1])

class cl_dungeon_generator():
    def __init__(self, d_size):
        self.dungeon = cl_dungeon(d_size[0],d_size[1])
    def generate_rooms(self,n_rooms = 5, min_size = 1, max_size = 10, max_tries = 1000):
        i = 0
        while len(self.dungeon.rooms) < n_rooms and i <= max_tries:
            i += 1
            room_xcord = random.randint(0, self.dungeon.width)
            room_ycord = random.randint(0, self.dungeon.height)
            room_width = random.randint(min_size,max_size)
            room_height = random.randint(min_size,max_size)
            new_room = cl_room(room_xcord, room_ycord, room_width, room_height)
            self.dungeon.add_room(new_room)
    
    def find_middle(self, cord_1, cord_2, size_1, size_2):
        if cord_1 == cord_2:
            return cord_1
        if cord_1 < cord_2:
            border_1 = cord_1 + size_1
            border_2 = cord_2 - size_2
        else:
            border_1 = cord_1 - size_1
            border_2 = cord_2 + size_2
        
        return int((border_1 + border_2) / 2)

    def create_corridors(self):
        delaunay_edges = self.graph.edges
        for edge in delaunay_edges:
            room_1 = edge[0]
            room_2 = edge[1]
            x_distance = abs(room_1.x_cord - room_2.x_cord)
            y_distance = abs(room_1.y_cord - room_2.y_cord)
            if x_distance < room_1.width + room_2.width - 2:
                x = self.find_middle(room_1.x_cord, room_2.x_cord, room_1.width, room_2.width)
                if room_1.y_cord < room_2.y_cord:    
                    start = (x, room_1.y_cord + room_1.height)
                    end = (x, room_2.y_cord - room_2.height)
                else:
                    start = (x, room_1.y_cord - room_1.height)
                    end = (x, room_2.y_cord + room_2.height)
                

                corridor = cl_corridor(start, end)
                self.dungeon.add_corridor(corridor)
            elif y_distance < room_1.width + room_2.width - 2:
                y = self.find_middle(room_1.y_cord, room_2.y_cord, room_1.height, room_2.height)
                
                if room_1.x_cord < room_2.x_cord:
                    start = (room_1.x_cord + room_1.width, y)
                    end = (room_2.x_cord - room_2.width, y)
                else:
                    start = (room_1.x_cord - room_1.width, y)
                    end = (room_2.x_cord + room_2.width, y)

                corridor = cl_corridor(start, end)
                self.dungeon.add_corridor(corridor)
            else:
                start_x = room_1.x_cord
                start_y = room_1.y_cord
                
                end_x = room_2.x_cord
                end_y = room_2.y_cord

                

                angle = get_angle(room_1, room_2)
                if angle <= 0.5*math.pi: 
                    middle = (room_2.x_cord, room_1.y_cord)        
                elif angle > 0.5 * math.pi and angle <= math.pi: 
                    middle = (room_1.x_cord, room_2.y_cord)
                elif angle > math.pi and angle <= 1.5 * math.pi:
                    middle = (room_2.x_cord, room_1.y_cord)
                elif angle > 1.5 * math.pi and angle <= 2 * math.pi:
                    middle = (room_1.x_cord, room_2.y_cord)
                
                if middle[0] == room_1.x_cord:
                    if middle[1] > room_1.y_cord:
                        start_y += room_1.height
                    else:
                        start_y -= room_1.height
                    
                    if middle[0] > room_2.x_cord:
                        end_x += room_2.width
                    else:
                        end_x -= room_2.width
                
                else:
                    if middle[0] > room_1.x_cord:
                        start_x += room_1.width
                    else:
                        start_x -= room_1.width
                    
                    if middle[1] > room_2.y_cord:
                        end_y += room_2.height
                    else:
                        end_y -= room_2.height

                start = (start_x, start_y)
                end = (end_x, end_y)
                
                corridor_1 = cl_corridor(start,middle)
                corridor_2 = cl_corridor(middle, end)
                self.dungeon.add_corridor(corridor_1)
                self.dungeon.add_corridor(corridor_2)

    def create_graph(self):
        sorted_rooms = sort_rooms(self.dungeon.rooms)
        self.graph = create_delaunay(sorted_rooms)
        print("delaunay created")
        self.create_corridors()
        self.dungeon.save_map("temp_file_2.txt")
        self.dungeon.corridors = []
        create_minimal_graph(self.graph)
        print("minimal connections")



tries = 1
errors = 0
for i in range(tries):
    print(i)  
    # try: 
    test = cl_dungeon_generator((250,100))
    test.generate_rooms(25,3,10)
    print("rooms generated")
    test.dungeon.save_map("temp_file_1.txt")
    # print(test.dungeon.rooms)
    test.create_graph()
    print("graph created")
    test.create_corridors()
    test.dungeon.save_map("temp_file_3.txt")
    # except:
    #     errors += 1
    print("-"*69)
print(errors)
# sort_rooms(test.dungeon.rooms)



# test = dungeon(49,49)
# # test.print_dungeon()
# print("-"*69)
# # test.set_cell(3,3,1)
# # room(2,2,1,1)
# test.add_room(room(5,5,4,3))
# test.add_room(room(5,20,5,4))
# test.add_room(room(20,10,2,2))
# test.add_corridor(corridor((5,5),(5,20)))
# test.add_corridor(corridor((20,10),(5,10)))
# # test.print_dungeon()
# test.save_map()