"""
"""

import sys
import argparse
import logging
import yaml
import json

from graphviz import Digraph

DOT_FILE_FORMAT = 'dot'
JSON_FILE_FORMAT = 'json'
PNG_FILE_FORMAT = 'png'
ACTION_COLOR = {'look': 'beige', 'pick': 'plum', 'combine': 'green',
                'default': 'azure', 'interact': 'lightblue', 'go': 'azure'}


def init_logging():
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        filename='auric.log', level=logging.DEBUG)


def init_parser():
    parser = argparse.ArgumentParser(description='Auric renders puzzle dependency charts in\
                                    different formats from a YAML input.')
    parser.add_argument('-y', '--yml',
                        help='Path to input YAML file')
    parser.add_argument('-f', '--format',
                        help='Output format extension. Supported formats are png, json and dot')
    parser.add_argument('-o', '--output',
                        help='Name of the output file without extension (e.g. my_pdc)')
    return parser


def export_pdc_to_json(pdc, out_file):
    fh = open(out_file + '.json', 'w')
    fh.write(json.dumps(pdc, indent=4))
    fh.close()


def export_pdc_to_dot(pdc, out_file):
    """
    Translates YAML input into a dot file
    """
    fh = open(out_file + '.dot', 'w')
    fh.write('digraph {\n\tratio = fill;\n')
    nodes = []
    for event in pdc['events']:
        if event['action'] is None:
            color = ACTION_COLOR['default']
        else:
            color = ACTION_COLOR[event["action"]]

        nodes.append(f'\tev_{event["name"]} [style=filled shape=record '
                     f'label=\"{{{{{event["name"]}|{event["action"]}}}'
                     f'|{event["location"]}}}\" fillcolor={color}];')
        if event['dependency']:
            for dep in event['dependency']:
                fh.write(f'\tev_{dep} -> ev_{event["name"]}\n')

    fh.write('\n\n')
    for node in nodes:
        fh.write(f'{node}\n')
    fh.write('}')
    fh.close()


def export_pdc_count(pdc, field, out_file):
    """
    Testing the graphviz lib to tarnslate the YAML input into a dot file.
    ToDo: Clean up out_file name.
    """
    dot = Digraph(comment='Adventure game', format="png")
    location_count = {}
    for event in pdc['events']:
        if location_count.get(event[field]):
            location_count[event[field]] += 1
        else:
            location_count[event[field]] = 1

    for k, v in location_count.items():
        dot.node(f'{k}',
                 f'{k}-{v}',
                 shape='record',
                 style='filled')            
    dot.render(f'{field + "_" + out_file}', view=False, cleanup=True)


def export_pdc_to_png(pdc, out_file):
    """
    Testing the graphviz lib to tarnslate the YAML input into a dot file.
    ToDo: Clean up out_file name.
    """
    dot = Digraph(comment='Adventure game', format="png")

    for event in pdc['events']:
        if event['action'] is None:
            color = ACTION_COLOR['default']
        else:
            color = ACTION_COLOR[event["action"]]
        dot.node(f'{event["name"]}',
                 f'{{{{{event["name"]}|{event["action"]}}}|{event["location"]}}}',
                 shape='record',
                 style='filled',
                 fillcolor=color)
        if event['dependency']:
            for dep in event['dependency']:
                dot.edge(f'{dep}', f'{event["name"]}')
    dot.render(out_file, view=False, cleanup=True)
    export_pdc_count(pdc, 'location', out_file)
    export_pdc_count(pdc, 'action', out_file)

def export_pdc(pdc, out_format, out_file):
    if out_format == DOT_FILE_FORMAT:
        export_pdc_to_dot(pdc, out_file)
    if out_format == JSON_FILE_FORMAT:
        export_pdc_to_json(pdc, out_file)
    if out_format == PNG_FILE_FORMAT or not out_format:
        export_pdc_to_png(pdc, out_file)
    else:
        logging.error('Unsupported file format provided')


def main():
    init_logging()
    parser = init_parser()
    args = parser.parse_args()

    if args.yml is None:
        logging.error('Missing YAML input. Run auric with -h for usage help')
        parser.print_help()
        sys.exit()

    pdc = yaml.load(open(args.yml, 'r'))
    export_pdc(pdc, args.format, args.output)

if __name__ == "__main__":
    main()
