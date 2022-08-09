from ast import Continue
from multiprocessing import connection
import queue
import numpy as np

def find_connected_rooms(current_room, start_room):
    # find all rooms connected to the current room when ignoring all edges to the start room
    
    visited_rooms = [start_room, current_room]
    queue = [con for con in current_room.connections if con != start_room]
    while len(queue) != 0:
        current_room = queue.pop(0)
        visited_rooms.append(current_room)
        connections = current_room.connections
        for room in connections:
            if room not in visited_rooms:
                queue.append(room)
    return visited_rooms[1:]

def find_critical(room, prev_room):
    critical_connections = []
    non_critical_connections = []
    critical_pairs = []
    for connection in room.connections:
        if connection in non_critical_connections:
            # if a room was detected to be an edge of another room it can't be a critical connection
            continue
        if connection in critical_connections:
            # if in a previous itteration a room was already marked as a critical connection it will now also be a critical connection
            continue
        if connection == prev_room:
            # connection to previous room is always a crticial connection
            critical_connections.append(connection)
            continue
        
        # find all rooms connected to the current connection when ignoring the previous room
        # all rooms connected to the current connection which are also directly connected to the previous room
        # are non critical connections
        connected_rooms = find_connected_rooms(connection, prev_room)
        pair = [room for room in room.connections if room in connected_rooms]
        
        # if pair only exists of 1 item that means it is a critical connection
        if len(pair) != 1:
            critical_pairs.append(pair)
            non_critical_connections += pair
        else:
            critical_pairs.append(pair)
        
    return critical_connections, critical_pairs

            


def create_minimal_graph(graph):
    current_room = graph.rooms[0]
    queue = [(current_room.connections[0], current_room)]
    connections = current_room.connections
    visited_rooms = [current_room]
    for room in connections[1:]:
        graph.del_connection(current_room, room)
    
    # deleted_connections = []
    while len(queue) != 0:
        # print(f"queue 0: {queue[0]}")
        current_room, prev_room = queue.pop(0)
        visited_rooms.append(current_room)
        crit, crit_pairs = find_critical(current_room, prev_room)
        
        # add all critical connection
        for crit_con in crit:
            if crit_con not in visited_rooms:
                queue.append((crit_con, current_room))
        
        # every pair is critical as in if every connection in a pair are deleted 
        # the graph is not connected any more thus by deleting all but one connection from each pair
        # you get a critical connection
        for pair in crit_pairs:
            # print(pair)
            queue.append((pair[0], current_room))
            for con in pair[1:]:
                graph.del_connection(con, current_room)
    return 
        