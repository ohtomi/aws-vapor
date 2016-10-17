****************************************
aws-vapor
****************************************

Description
========================================

This tool generates AWS CloudFormation template from python object.

Requirements
========================================

- Python v2.7.x, v3.4.x, v3.5.x

How to install
========================================

.. code-block:: bash

   $ pip install aws-vapor

How to use
========================================

.. code-block:: bash

   $ aws-vapor --help
   usage: aws-vapor [--version] [-v | -q] [--log-file LOG_FILE] [-h] [--debug]

   AWS CloudFormation Template Generator

   optional arguments:
     --version            show program's version number and exit
     -v, --verbose        Increase verbosity of output. Can be repeated.
     -q, --quiet          Suppress output except warnings and errors.
     --log-file LOG_FILE  Specify a file to log output. Disabled by default.
     -h, --help           Show help message and exit.
     --debug              Show tracebacks on errors.

   Commands:
     complete       print bash completion command
     config         show current configuration or set new configuration
     generate       generate AWS CloudFormation template from python object
     get            download contributed recipe from url
     help           print detailed help for another command

generates AWS CloudFormation template
----------------------------------------

.. code-block:: bash

   $ aws-vapor config set defaults contrib '/path/to/template-dir'
   $ aws-vapor config list
   [defaults]
   contrib = /path/to/template-dir
   $ aws-vapor generate 'template-file' --output '/path/to/json-file'

Examples
========================================

See https://github.com/ohtomi/aws-vapor/tree/master/examples/

Contributing
========================================

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

License
========================================

MIT
