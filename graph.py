import json
import networkx as nx


def get_metro_graph(stations, connections, outfile):

    with open(f'data/{stations}', 'r', encoding='utf-8') as file1:
        stations = json.load(file1)
        stations_dict = dict()
        stations_labels = dict()
        line_labels = dict()
        for line in stations:
            stations_dict.update({x['id']: {'name': x['name'], 'line': line['name'], 'color': line['color']} for x in line['stations']})
            stations_labels.update({line['name']: {x['name']: x['id'] for x in line['stations']}})
            line_labels[line['id']] = line['name']

    with open(f'data/{connections}', 'r', encoding='utf-8') as file2:
        connections = json.load(file2)
        edge_list = []
        for link in connections:
            edge_list.append(tuple(link['stations'] + [link['time']]))

    Metro_Graph = nx.Graph()
    Metro_Graph.add_weighted_edges_from(edge_list)
    nx.set_node_attributes(Metro_Graph, stations_dict)
    nx.write_gexf(Metro_Graph, f'data/{outfile}')

    with open('data/labels.json', mode='w', encoding='utf-8') as file3:
        json.dump(stations_labels, file3, ensure_ascii=False, indent=4)

    with open('data/line_labels.json', mode='w', encoding='utf-8') as file4:
        json.dump(line_labels, file4, ensure_ascii=False, indent=4)

    return Metro_Graph, stations_labels, line_labels


def station_input(labels=dict, start=bool):

    if start:
        prompt = 'начальную'
    else:
        prompt = 'конечную'

    enum_lines = [(x[0] + 1, x[1]) for x in enumerate(list(labels.keys()))]
    print(f'Выберите {prompt} линию метро:\n')
    for line in enum_lines:
        print(f'{line[0]} - {line[1]}')

    line = enum_lines[int(input()) - 1][1]

    enum_stations = [(x[0] + 1, x[1]) for x in enumerate(list(labels[line].keys()))]

    print(f'Выберите {prompt} станцию:\n')
    for station in enum_stations:
        print(f'{station[0]} - {station[1]}')

    station = enum_stations[int(input()) - 1][1]

    node = labels[line][station]
    return node


def find_shortest_path(graph, labels=dict, line_labels=dict, start_node=str, end_node=str):
    stations_labels = {}
    for line in labels.values():
        stations_labels.update({line[x]: x for x in line})

    path = nx.dijkstra_path(graph, start_node, end_node, 'weight')
    time = nx.path_weight(graph, path, 'weight')

    to_remove = []
    for i in range(1, len(path)-1):
        if path[i][:path[i].rfind('_')] == path[i-1][:path[i-1].rfind('_')] and path[i][:path[i].rfind('_')] == path[i+1][:path[i+1].rfind('_')]:
            to_remove.append(path[i])

    path_dict = dict()
    for elem in [x for x in path if x not in to_remove]:
        if line_labels[elem[:elem.rfind('_')]] not in path_dict:
            path_dict[line_labels[elem[:elem.rfind('_')]]] = [stations_labels[elem]]
        else:
            path_dict[line_labels[elem[:elem.rfind('_')]]].append(stations_labels[elem])

    it = list(path_dict.items())
    i = 0

    output = str()

    while True:
        try:
            line, station = it[i]
            if i == 0:
                output += f'{line}:\n'
            else:
                output += line.replace('ая ', 'ую ').replace('линия', 'линию') + ':\n'
            output += ' -> '.join(station) + '\n\n'
            next = it[i+1]
        except IndexError:
            output += 'Вы прибыли на место назначения!\n'
            break
        output += 'Перейдите на '
        i += 1

    output += f'Дорога займёт {round(time / 60, 0)} минут(ы)'

    return output


def init_graph():
    try:

        MetroGraph = nx.read_gexf('data/metrograph.gexf')
        with open('data/labels.json', mode='r', encoding='utf-8') as file5:
            stations_labels = json.load(file5)
        with open('data/line_labels.json', mode='r', encoding='utf-8') as file6:
            line_labels = json.load(file6)

    except FileNotFoundError:

        MetroGraph, stations_labels, line_labels = get_metro_graph('metro.json', 'connections.json', 'metrograph.gexf')

    return MetroGraph, stations_labels, line_labels
