"""Simple Vehicles Routing Problem."""

from importlib.resources import path
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np

'''
# This is a test matrix, do not use with the real case example
pyMatriz = [
        [0, 55, 33],
        [55, 0, 44],
        [33, 44, 0]]
'''

def pathfinding(pyMatriz):

    pyMatriz = np.int64(pyMatriz)

    #print('  Matriz: \n', pyMatriz, "\n")

    def create_data_model(pyMatriz):
        """Stores the data for the problem."""
        data = {}
        data['distance_matrix'] = pyMatriz
        data['num_vehicles'] = 1
        data['starts'] = [0]
        data['ends'] = [1]
        return data


    def print_solution(data, manager, routing, solution):
        """Prints solution on console."""
        #max_route_distance = 0
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            plan_output = []
            route_distance = 0
            while not routing.IsEnd(index):
                plan_output.append(manager.IndexToNode(index))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            plan_output.append(manager.IndexToNode(index))
            # plan_output.append(route_distance)
            # print(plan_output)
            return plan_output
    
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(pyMatriz)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['starts'], data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        10**10,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    '''search_parameters.time_limit.seconds = 5
    search_parameters.lns_time_limit.seconds = 1'''

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        result = print_solution(data, manager, routing, solution)
    
    #print("  Solución: \n", result, "\n")

    return result
 