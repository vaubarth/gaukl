from multiprocessing import freeze_support

from gaukl.core.service import run_gaukl
import gaukl.examples.extensions.myextensions

if __name__ == '__main__':
    freeze_support()
    # Load the config file and the recipe to be used
    run_gaukl('./config.yaml')
