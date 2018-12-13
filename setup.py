# import ez_setup
# ez_setup.use_setuptools()

from setuptools import setup, find_packages
from rho_factor import __version__, __package__

setup(
    name=__package__,
    version=__version__,
    packages=find_packages(),
    package_data={
        # If any package contains *.txt files, include them:
        #'': ['*.txt'],
        #'lut': ['data/lut/*.nc'],
        'aux': ['data/aux/*']
    },
    include_package_data=True,

    url='',
    license='MIT',
    author='T. Harmel',
    author_email='tristan.harmel@ntymail.com',
    description='',

    # Dependent packages (distributions)
    install_requires=['pandas','scipy','numpy','netCDF4', 'plotly',
                      'dash','dash_core_components','dash_html_components',
                      'matplotlib','docopt'],

    entry_points={
          'console_scripts': [
              'visu_rho = rho_factor.visu_rho.visu_rho:visu'
          ]}
)
