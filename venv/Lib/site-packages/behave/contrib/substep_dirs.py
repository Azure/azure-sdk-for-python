# -*- coding: UTF-8 -*-
"""
Recipe for loading additional step definitions from sub-directories
in the "features/steps" directory.

.. code-block::

    # -- FILE: features/steps/use_substep_dirs.py
    # REQUIRES: path.py
    from behave.runner_util import load_step_modules 
    from path import Path
    
    HERE = Path(__file__).dirname
    SUBSTEP_DIRS = list(HERE.walkdirs())
    load_step_modules(SUBSTEP_DIRS)
"""
