##
# Mouse Locomotion Simulation
#
# Human Brain Project SP10
#
# This project provides the user with a framework based on 3D simulators allowing:
#  - Edition of a 3D model
#  - Edition of a physical controller model (torque-based or muscle-based)
#  - Edition of a brain controller model (oscillator-based or neural network-based)
#  - Simulation of the model
#  - Optimization and Meta-optimization of the parameters in distributed cloud simulations
#
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# February 2016
##

from distutils.core import setup
import pip
from pip.req import parse_requirements
from optparse import Option
import src

options = Option("--workaround")
options.skip_requirements_regex = None

reqs_file = './requirements.txt'

# Hack for old pip versions
# Versions greater than 1.x have a required parameter "session" in parse_requirements
if pip.__version__.startswith('1.'):
    requirements = parse_requirements(reqs_file, options=options)
else:
    from pip.download import PipSession

    options.isolated_mode = False
    requirements = parse_requirements(
        reqs_file,
        session=PipSession,
        options=options
    )
reqs = [str(ir.req) for ir in requirements]

config = {
    'description': 'Mouse Locomotion Simulation',
    'author': 'HBP Neurorobotics',
    'url': 'http://neurorobotics.net',
    'author_email': 'neurorobotics@humanbrainproject.eu',
    'version': src.__version__,
    'install_requires': reqs,
    'packages': ['src',
                 'src.musculoskeletals', 'src.musculoskeletals.muscles', 'src.musculoskeletals.sensors',
                 'src.musculoskeletals.sensors.muscleReceptors', 'src.optimizations', 'src.optimizations.pyevolve',
                 'src.oscillators', 'src.simulations', 'src.simulations.clients', 'src.simulations.servers',
                 'src.simulators', 'src.simulators.blender', 'src.utils', 'src.utils.observers'
                 ],
    'package_data': {
        'defaults': ['config.ini']
    },
    'scripts': [],
    'name': 'mouse_locomotion',
    'include_package_data': True,
}

setup(**config)
