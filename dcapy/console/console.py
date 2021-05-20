from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
console = Console()


def schedule_layout():
    layout = Layout()
    
    layout.split_column(
        Layout(name='header',size=3),
        Layout(name='body'),
        Layout(name='footer',size=3)
    )
    
    layout['body'].split_row(
        Layout(name='left_body'),
        Layout(name='right_body', ratio=2),
    )
    console.print(layout)
    
if __name__ == '__main__':
    schedule_layout()