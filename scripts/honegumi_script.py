from pprint import pprint

import honegumi
from honegumi.ax._ax import option_rows
from honegumi.ax.utils import constants as cst
from honegumi.core._honegumi import Honegumi

# Set up template paths
script_template_dir = honegumi.ax.__path__[0]
core_template_dir = honegumi.core.__path__[0]
script_template_name = "main.py.jinja"
core_template_name = "honegumi.html.jinja"

# Initialize Honegumi
hg = Honegumi(
    cst,
    option_rows,
    script_template_dir=script_template_dir,
    core_template_dir=core_template_dir,
    script_template_name=script_template_name,
    core_template_name=core_template_name,
)

# Configure for OER catalyst optimization
options_model = hg.OptionsModel(
    objective="multi",
    model="Default",
    task="Single",
    categorical=False,
    sum_constraint=False,
    order_constraint=False,
    linear_constraint=False,
    composition_constraint=True,
    custom_threshold=True,
    existing_data=False,
    synchrony="Single",
    visualize=True,
)

# Print the configured options for review
pprint(options_model.model_dump())

# Generate the optimization script
result = hg.generate(options_model)

# Save to file
script_name = "scripts/ll_extraction.py"
with open(script_name, "w") as f:
    f.write(result)

print(f"\nGenerated optimization script saved to {script_name}")
