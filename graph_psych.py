import csv
import igraph as ig
import pickle
import random
import math
import colorsys
import os
import sys
import leidenalg as la
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def read_dois_from_file(filepath='./data/dois.txt') -> set[str]:
    with open(filepath, 'r', encoding='utf-8') as file:
        dois = {line.strip() for line in file} 
    return dois

def filter_edges_and_save(valid_dois: list[str], input_filepath: str ='./data/edges.csv', output_filepath:str ='./data/edges_filtered.csv'):
    with open(input_filepath, 'r', encoding='utf-8') as infile, \
         open(output_filepath, 'w', encoding='utf-8', newline='') as outfile:
      
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            if len(row) >= 2 and row[1] in valid_dois:  
                writer.writerow(row)


def get_node_ids() -> dict[str, int|int, str]:
    node_count = 0
    node_ids = {}
    with open('./data/edges.csv', encoding="utf-8") as links_file:
        reader = csv.reader(links_file)


        for row in reader:
            if row[0] not in node_ids:
                node_ids[row[0]] = node_count
                node_ids[node_count] = row[0]
                node_count += 1
            if row[1] not in node_ids:
                node_ids[row[1]] = node_count
                node_ids[node_count] = row[1]
                node_count += 1

    with open('./data/node_ids.pkl', 'wb') as node_file:
        pickle.dump(node_ids, node_file)
    return node_ids

def get_edges(node_ids: dict) -> list[tuple[int, int]]:
    edges = []

    with open('./data/edges.csv', encoding="utf-8") as links_file:
        reader = csv.reader(links_file)
        next(reader, None)

        link_count = 0
        for row in reader:                    
            edges.append((node_ids[row[0]], node_ids[row[1]]))
    return edges

def create_graph(node_ids: dict, edges: list[tuple[int, int]]) -> ig.Graph:
    node_count = int(len(node_ids)/2)
    graph = ig.Graph(node_count, edges=edges, directed=True)

    with open('./data/graph.pkl', 'wb') as graph_file:
        pickle.dump(graph, graph_file)
    return graph

def get_layout(graph: ig.Graph) -> ig.layout:
    print("Generating layout... This may take a few hours to days, depending on the number of edges")
    #Note: It took me 130 minutes for 7.7 million edges
    layout = graph.layout('drl')

    with open('./data/layout.pkl', 'wb') as layout_file:
        pickle.dump(layout, layout_file)
    return layout


def get_partition(graph: ig.Graph):
    partition = la.find_partition(graph, la.RBConfigurationVertexPartition, resolution_parameter = 1)

    partition_list = []
    for p in partition:
        partition_list.append(p)

    partition_dict = {}
    for i in range(len(partition)):
        for j in partition[i]:
            partition_dict[j] = i
    print(f"Number of partitions: {len(partition_list)}")

    return partition, partition_list, partition_dict

def find_factors(num_vertices: int) -> tuple[int, int]:
    for i in range(int(math.sqrt(num_vertices)), 0, -1):
        if num_vertices % i == 0:  
            return (num_vertices // i, i)
    return (num_vertices, 1)

def generate_colors_exact(num_partitions: int, overwrite_top_ten: bool = True):
    num_hues, num_saturations = find_factors(num_partitions)
    v = 0.8
    node_colors = []
    edge_colors = []
    
    saturation_start = 0.5
    saturation_increment = (1 - saturation_start) / num_saturations

    hue_increment = 1 / num_hues

    for i in range(num_hues):
        hue = i * hue_increment
        for j in range(num_saturations):
            saturation = saturation_start + j * saturation_increment
            rgb_color = colorsys.hsv_to_rgb(hue, saturation, v)
            rgba_node = 'rgba({},{},{},0.8)'.format(int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255))
            rgba_edge = 'rgba({},{},{},0.05)'.format(int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255))
            node_colors.append(rgba_node)
            edge_colors.append(rgba_edge)
    
    #randomly shuffle colors so that hue is not correlated with partition order
    color_pairs = list(zip(node_colors, edge_colors))
    random.shuffle(color_pairs)
    node_colors, edge_colors = zip(*color_pairs)
    node_colors = list(node_colors)
    edge_colors = list(edge_colors)

    if overwrite_top_ten:
        new_node_colors = [
            'rgba(255,87,51,0.8)',  # Red
            'rgba(51,255,87,0.8)',  # Lime
            'rgba(51,87,255,0.8)',  # Blue
            'rgba(249,51,255,0.8)', # Magenta
            'rgba(51,255,249,0.8)', # Cyan
            'rgba(249,255,51,0.8)', # Yellow
            'rgba(255,131,51,0.8)', # Orange
            'rgba(131,51,255,0.8)', # Purple
            'rgba(51,255,131,0.8)', # Green
            'rgba(255,51,51,0.8)',  # Bright Red
        ]

        new_edge_colors = [
            'rgba(255,87,51,0.05)',  # Red
            'rgba(51,255,87,0.05)',  # Lime
            'rgba(51,87,255,0.05)',  # Blue
            'rgba(249,51,255,0.05)', # Magenta
            'rgba(51,255,249,0.05)', # Cyan
            'rgba(249,255,51,0.05)', # Yellow
            'rgba(255,131,51,0.05)', # Orange
            'rgba(131,51,255,0.05)', # Purple
            'rgba(51,255,131,0.05)', # Green
            'rgba(255,51,51,0.05)',  # Bright Red
        ]

        # Overwrite the first 10 entries with the new bright colors for better visibility
        node_colors[:10] = new_node_colors
        edge_colors[:10] = new_edge_colors

    with open('./data/colors.txt', 'w') as color_file:
        for i in range(len(node_colors)):
            color_file.write(f'{node_colors[i]}\n')
    
    return node_colors, edge_colors


def truncate_graph(graph: ig.Graph, partition_dict: dict[int, str], node_ids, included_partitions) -> ig.Graph:
    graph.delete_edges()

    edges = []

    with open('./data/links.csv', encoding="utf-8") as links_file:
        reader = csv.reader(links_file)
        next(reader, None)

        link_count = 0
        for row in reader:
            source_partition = partition_dict[node_ids[row[0]]]
            target_partition = partition_dict[node_ids[row[1]]]

            # Only add edge if it starts and ends in the same partition and the partition is included
            if source_partition == target_partition and source_partition in included_partitions:
                    edges.append((node_ids[row[0]], node_ids[row[1]]))
    graph.add_edges(edges)
    return graph


def set_colors(graph, partition, partition_dict, node_colors, edge_colors) -> ig.Graph:
    for i in range(len(partition)):
        for node in partition[i]:
            graph.vs[node]['color'] = node_colors[i]
            graph.vs[node]['frame_color'] = 'rgba(0, 0, 0, 0.5)'
            
            size = 168 * math.log10(0.00005 * graph.vs[node].indegree() + 1) + 3
            graph.vs[node]['size'] = size
            frame_size = 0.1 + (6.56/197) * (size-3)
            graph.vs[node]['frame_width'] = frame_size
    for edge in range(graph.ecount()):
        source_partition = partition_dict[graph.es[edge].source]
        target_partition = partition_dict[graph.es[edge].target]
        if source_partition == target_partition:
            graph.es[edge]['color'] = edge_colors[source_partition]
    
    with open('./data/graph_styled.pkl', 'wb') as graph_file:
        pickle.dump(graph, graph_file)
    return graph

def plot_graph(graph, layout, width = 19200, height = 10800) -> None:
    visual_style = {}

    visual_style["bbox"] = (height, width) # Dimension of the image (has to be rotated after creation)
    visual_style["margin"] = 50 # Margin of pixels from the borders
    visual_style["layout"] = layout
    visual_style["background"] = 'rgba(0, 0, 0, 0)' # Transparent background
    visual_style["edge_arrow_size"] = 0
    visual_style["edge_width"] = 0.25
    visual_style["node_order_by"] = 'size' # Draw nodes in order of their size, larger nodes will be drawn last

    image_path = "./data/graph.png"

    plot = ig.plot(graph, image_path, **visual_style)

    # Rotate the image
    img = Image.open(image_path)
    img = img.rotate(90, expand=True)
    img.save(image_path)
    print(f"Graph saved to {image_path}")


# I apologize for the messiness of this main function, some steps take very long, and this was a convenient way to avoid them
def main():
    redo_everything = bool(sys.argv[1])
    if not redo_everything:
        print("Running in normal mode, skipping already generated files. Use 'python graph_psych.py True' to redo everything.")
    valid_dois = read_dois_from_file()

    if not os.path.exists('./data/edges_filtered.csv') and not redo_everything:
        print("Filtering edges file...")
        filter_edges_and_save(valid_dois)
    else:
        print("Filtered edges file already exists, skipping edge filtering.")

    if (not os.path.exists('./data/links.csv') or not os.path.exists('./data/deadends.txt')) and not redo_everything:
        print("Generating links file...")
        remove_disguised_deadends()
    else:
        print("Link file already exists, skipping link generation.")

    if not os.path.exists('./data/node_ids.pkl') and not redo_everything:
        print("Generating node IDs file...")
        node_ids = get_node_ids()
    else:
        print("Loading existing node IDs file...")
        with open('./data/node_ids.pkl', 'rb') as file:
            node_ids = pickle.load(file)

    if not os.path.exists('./data/graph.pkl') and not redo_everything:
        print("Generating graph object file...")
        if 'node_ids' not in locals():
            with open('./data/node_ids.pkl', 'rb') as file:
                node_ids = pickle.load(file)
        edges = get_edges(node_ids)
        graph = create_graph(node_ids, edges)
    else:
        print("Loading existing graph object...")
        with open('./data/graph.pkl', 'rb') as file:
            graph = pickle.load(file)

    if not os.path.exists('./data/layout.pkl') and not redo_everything:
        print("Generating layout file...")
        layout = get_layout(graph)
    else:
        print("Loading existing layout...")
        with open('./data/layout.pkl', 'rb') as file:
            layout = pickle.load(file)


    print("Generating partition files...")
    partition, partition_list, partition_dict = get_partition(graph)
    with open('./data/partition_list.pkl', 'wb') as file:
        pickle.dump(partition_list, file)
    with open('./data/partition_dict.pkl', 'wb') as file:
        pickle.dump(partition_dict, file)


    print("Generating colors file...")
    node_colors, edge_colors = generate_colors_exact(len(partition_list))

    print("Removing edges from graph...")
    graph = truncate_graph(graph, partition_dict, node_ids, included_partitions=list(range(10)))

    print("Generating styled graph...")
    graph = set_colors(graph, partition, partition_dict, node_colors, edge_colors)


    print("Generating graph image, this might take a few minutes to hours...")
    plot_graph(graph, layout)

if __name__ == "__main__":
    main()




