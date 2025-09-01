import argparse
import json
import importlib.util
from multiprocessing import context
import sys
from pathlib import Path

def import_module(filepath: Path):
    spec = importlib.util.spec_from_file_location("lambda_handler", str(filepath))
    module = importlib.util.module_from_spec(spec)
    sys.modules["lambda_handler"] = module
    spec.loader.exec_module(module)
    return module

def load_input_data(input_file: Path):
    if not input_file.exists():
        print(f"Input file '{input_file}' does not exist.")
        sys.exit(1)
    return json.loads(input_file.read_text())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path", "-p", dest="path", type=str, required=False, default=None
    )
    args = parser.parse_args()
    if args.path is None:
        path = [handler_path.parent for handler_path in Path(__file__).parent.rglob("lambda_function.py")]
    else:
        path = [Path(args.path)]

    for p in path:

        handler_file = p / "lambda_function.py"
        input_file = p / "input.json"
        if not input_file.exists():
            print(f"Input file '{input_file}' does not exist.")
            continue
        event = load_input_data(input_file)
        context = None
        module = import_module(handler_file)
        handler = getattr(module, "lambda_handler", None)
        if not callable(handler):
            print(f"No lambda_handler in {p.name}")
            continue

        print(f"--- Running benchmark: {p.name} ---")
        try:
            result = handler(event, context)
            print(f" Result: {result}\n")
        except Exception as e:
            print(f" Error running {p.name}: {e}\n")

if __name__ == "__main__":
    main()