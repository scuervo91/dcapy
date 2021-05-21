from dcapy.dca import Arps , Wor
from rich.console import Console
from rich.layout import Layout
console = Console()

layout = Layout()

layout.split_column(
	Layout(name='header'),
	Layout(name='body'),
	Layout(name='footer')
)

layout['body'].split_row(
	Layout(name='left'),
	Layout(name='right',ratio=2)
)


a1 = Arps(qi=500,ti='2021-01-01',b=0,di=0.1)
w1 = Wor(bsw=.5,ti='2021-01-01',slope=3e-5,fluid_rate=1000)

j = a1.get_layout()
k = w1.get_layout()

layout['body']['left'].update(j)
layout['body']['right'].update(k)


console.print(layout)
