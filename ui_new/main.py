from nicegui import ui
from nicegui.elements import markdown

ui.label(f'Markdown content cache size is {markdown.prepare_content.cache_info().maxsize}')

ui.run(port=8080)