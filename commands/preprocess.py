import marimo

__generated_with = "0.11.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    from tqdm import tqdm
    import os
    import mistune
    from dotwiz import DotWiz

    markdown = mistune.create_markdown(renderer=None)
    return DotWiz, json, markdown, mistune, os, tqdm


@app.cell
def _(DotWiz, json, markdown):
    def process(file,output_dir):
        with open(file, encoding="utf8") as f:
            text = f.read()
        text = "\n".join([line for line in text.split("\n") if line.strip() != ""])
        content = DotWiz({"content":markdown(text)})
        heading = content.content[0].children[0].raw
    
        with open(f'{output_dir}/{heading}.json', 'w') as f:
            json.dump(content, f)

    return (process,)


@app.cell
def _(os, process, tqdm):
    for file in tqdm(os.listdir('pages/windows')):
        process(f'pages/windows/{file}','inputs_windows')

    for file in tqdm(os.listdir('pages/linux')):
        process(f'pages/linux/{file}','inputs_linux')

    for file in tqdm(os.listdir('pages/common')):
        process(f'pages/common/{file}','inputs_common')
    return (file,)


@app.cell
def _():
    from typing import Dict, List, Any

    def extract_text_from_children(children: List[Dict[str, Any]]) -> str:
        """Extract raw text from nested children structure."""
        text = []
        for child in children:
            if child['type'] == 'text':
                text.append(child.get('raw', ''))
            elif child['type'] == 'codespan':
                text.append(child.get('raw', ''))
            elif child['type'] == 'softbreak':
                text.append(' ')
            elif 'children' in child:
                text.append(extract_text_from_children(child['children']))
        return ''.join(text)
    return Any, Dict, List, extract_text_from_children


@app.cell
def _(Any, Dict, List, extract_text_from_children):
    def process_use_cases(list_items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Process list items into use cases with description and syntax."""
        use_cases = []
        for item in list_items:
            if 'children' in item:
                block_text = next((child for child in item['children'] 
                                 if child['type'] == 'block_text'), None)
                if block_text and 'children' in block_text:
                    # Split the text by softbreak to separate description and syntax
                    children = block_text['children']
                    description = ''
                    syntax = ''
                
                    # Find description (first part) and syntax (after softbreak)
                    for i, child in enumerate(children):
                        if child['type'] == 'softbreak':
                            description = extract_text_from_children(children[:i])
                            syntax = extract_text_from_children(children[i+1:])
                            break
                
                    if description and syntax:
                        use_cases.append({
                            "description": description.strip(),
                            "syntax": syntax.strip()
                        })
        return use_cases
    return (process_use_cases,)


@app.cell
def _(Any, Dict, extract_text_from_children, process_use_cases):
    def simplify_json_doc(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert complex JSON documentation into simplified format."""
        content = input_data.get('content', [])
    
        # Initialize result structure
        result = {
            "command": "",
            "description": "",
            "useCases": []
        }
    
        for item in content:
            # Extract command name from heading
            if item['type'] == 'heading' and item.get('attrs', {}).get('level') == 1:
                result['command'] = extract_text_from_children(item['children'])
        
            # Extract description from blockquote
            elif item['type'] == 'block_quote':
                result['description'] = extract_text_from_children(item['children'])
        
            # Extract use cases from list
            elif item['type'] == 'list':
                result['useCases'] = process_use_cases(item['children'])
    
        return result
    return (simplify_json_doc,)


@app.cell
def _(json, os, simplify_json_doc, tqdm):
    def process_directory(input_dir: str, output_dir: str):
        """Process all JSON files in a directory."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
        # Process each JSON file in the input directory
        for filename in tqdm(os.listdir(input_dir)):
            if filename.endswith('.json'):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, f'simplified_{filename}')
            
       
                # Read input file
                with open(input_path, 'r', encoding='utf-8') as f:
                    input_data = json.load(f)
            
                    # Process the file
                simplified_data = simplify_json_doc(input_data)
                
                # Write output file
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(simplified_data, f, indent=2, ensure_ascii=False)
                

    return (process_directory,)


@app.cell
def _(process_directory):
    process_directory('inputs_windows', 'windows')
    process_directory('inputs_linux', 'linux')
    process_directory('inputs_common', 'common')
    return


@app.cell
def _():
    import shutil

    shutil.rmtree('inputs_windows')
    shutil.rmtree('inputs_linux')
    shutil.rmtree('inputs_common')
    return (shutil,)


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
