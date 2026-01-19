import sys
from fhrcc_mechanismkg.io import graph_from_json

def main():
    if len(sys.argv) != 2:
        print('Usage: python validate_graph.py <graph.json>')
        sys.exit(1)

    path = sys.argv[1]
    graph_from_json(path)
    print(f'OK: graph validated successfully -> {path}')

if __name__ == '__main__':
    main()
