from dcapy.schedule import WellsGroup
import yaml
from rich.console import Console
console = Console(record=True)
with open('YML_example1.yml','r') as file:
	case_dict = yaml.load(file)

case = WellsGroup(**case_dict)
console.print(case.tree())
console.print(case.wells['well-2'].layout())
console.save_html('test_export.html')
