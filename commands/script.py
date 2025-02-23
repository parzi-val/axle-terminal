import json

import mistune
from dotwiz import DotWiz

with open("commands/pages/windows/cd.md", "r") as f:
    text = f.read()
text = "\n".join([line for line in text.split("\n") if line.strip() != ""])


markdown = mistune.create_markdown(renderer=None)

# with open('output.json', 'w') as f:
#     json.dump({"content": markdown(text)}, f)

content = DotWiz({"base":markdown(text)})

#heading
heading = content.base[0].children[0].raw
print(heading)