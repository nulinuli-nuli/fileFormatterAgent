import re
import sys

def convert_text(input_file: str, output_file: str):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove excessive empty lines
        content = re.sub(r'\n\s*\n{3,}', '\n\n\n', content)

        # Split sections based on the pattern 【X、...】
        sections = re.split(r'(\【\d+、[^】]+】)', content)
        markdown_content = []

        for i in range(0, len(sections) - 1, 2):
            section_title = sections[i + 1].strip()
            section_body = sections[i + 2].strip()

            if section_title and section_body:
                # Format title
                formatted_title = f"### {section_title}\n\n"
                markdown_content.append(formatted_title)

                # Format body
                body_lines = section_body.split('\n')
                formatted_body = []
                for line in body_lines:
                    line = line.rstrip()
                    if line.startswith('[') or line.startswith('见') or line.startswith('http'):
                        formatted_body.append(f"> {line}\n")
                    elif line.strip().startswith('1.') or line.strip().startswith('2.'):
                        formatted_body.append(f"- {line.strip()}\n")
                    else:
                        formatted_body.append(f"{line}\n")

                markdown_content.append(''.join(formatted_body))
                markdown_content.append("\n")

        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(markdown_content)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    convert_text(sys.argv[1], sys.argv[2])