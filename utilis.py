import json

def pretty_print_chain(chain):
    for block in chain:
        print(json.dumps(block.__dict__, indent=2))
