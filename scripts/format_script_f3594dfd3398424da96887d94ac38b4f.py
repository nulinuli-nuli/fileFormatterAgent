import json

def convert_text(input_file: str, output_file: str):
    try:
        with open(input_file, 'r') as infile:
            lines = infile.readlines()
        data = [line.strip() for line in lines if line.strip()]
        with open(output_file, 'w') as outfile:
            json.dump(data, outfile)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    convert_text(sys.argv[1], sys.argv[2])