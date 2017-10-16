====================
Fluke 28x Multimeter
====================


.. image:: https://img.shields.io/pypi/v/fluke_28x_multimeter.svg
        :target: https://pypi.python.org/pypi/fluke_28x_multimeter

.. image:: https://img.shields.io/travis/mofe23/fluke_28x_multimeter.svg
        :target: https://travis-ci.org/mofe23/fluke_28x_multimeter

.. image:: https://readthedocs.org/projects/fluke-28x-multimeter/badge/?version=latest
        :target: https://fluke-28x-multimeter.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/mofe23/fluke_28x_multimeter/shield.svg
     :target: https://pyup.io/repos/github/mofe23/fluke_28x_multimeter/
     :alt: Updates


SteadySense Fluke 28x Multimeter implementation


* Free software: GNU General Public License v3
* Documentation: https://fluke-28x-multimeter.readthedocs.io.


Features
--------

* Command Line
* ZeroRcp interface

.. code-block:: console

    $ fluke
    Usage: fluke_28x_multimeter [OPTIONS] COMMAND [ARGS]...

      Console script for fluke_28x_multimeter.

    Options:
      -v, --verbose  print more output
      --help         Show this message and exit.

    Commands:
      display   Displays all values shown on the multimeters...
      identify  Displays information about connected Device...
      primary   Displays primary measurement from Multimeter...
      serve     Starts a server to expose Multimeter on...


Commands
--------

Modes

.. code-block:: console

    V_AC, MV_AC, V_DC, MV_DC, OHMS, DIODE, MA_DC, UA_DC

QM

.. code-block:: console

    b'0\r0.0780E0,VAC,NORMAL,NONE\r'
    b'0\r+9.99999999E+37,VAC,OL,NONE\r'
    b'0\r0.0007E0,VDC,NORMAL,NONE\r'
    b'0\r0.327E-3,VDC,NORMAL,NONE\r'
    b'0\r+9.99999999E+37,OHM,OL,NONE\r'
    b'0\r+9.99999999E+37,VDC,OL,NONE\r'
    b'0\r0.000E-3,ADC,NORMAL,NONE\r'
    b'0\r0.01E-6,ADC,NORMAL,NONE\r'


QDDA

.. code-block:: console

    b'0\rV_AC,NONE,AUTO,VAC,5,0,OFF,0.000,0,2,LIVE,0.0769,VAC,0,4,5,NORMAL,NONE,1507815682.743,PRIMARY,0.0769,VAC,0,4,5,NORMAL,NONE,1507815682.743\r'
    b'0\rMV_AC,NONE,AUTO,VAC,500,-3,ON,0.000,0,2,LIVE,1e+38,VAC,-3,3,5,OL,NONE,1507815684.831,PRIMARY,1e+38,VAC,-3,3,5,OL,NONE,1507815684.831\r'
    b'0\rV_DC,NONE,AUTO,VDC,5,0,OFF,0.000,0,2,LIVE,0.0007,VDC,0,4,5,NORMAL,NONE,1507815686.917,PRIMARY,0.0007,VDC,0,4,5,NORMAL,NONE,1507815686.917\r'
    b'0\rMV_DC,NONE,AUTO,VDC,50,-3,OFF,0.000,0,2,LIVE,0.002471,VDC,-3,3,5,NORMAL,NONE,1507815689.005,PRIMARY,0.002471,VDC,-3,3,5,NORMAL,NONE,1507815689.005\r'
    b'0\rOHMS,NONE,AUTO,OHM,500,6,OFF,0.000,0,2,LIVE,1e+38,OHM,6,1,4,OL,NONE,1507815690.989,PRIMARY,1e+38,OHM,6,1,4,OL,NONE,1507815690.989\r'
    b'0\rDIODE_TEST,NONE,MANUAL,VDC,5,0,OFF,0.000,0,2,LIVE,1e+38,VDC,0,4,5,OL,NONE,1507815693.016,PRIMARY,1e+38,VDC,0,4,5,OL,NONE,1507815693.016\r'
    b'0\rMA_DC,NONE,AUTO,ADC,50,-3,OFF,0.000,0,2,LIVE,1e-06,ADC,-3,3,5,NORMAL,NONE,1507815695.114,PRIMARY,1e-06,ADC,-3,3,5,NORMAL,NONE,1507815695.114\r'
    b'0\rUA_DC,NONE,AUTO,ADC,500,-6,OFF,0.000,0,2,LIVE,2e-08,ADC,-6,2,5,NORMAL,NONE,1507822644.513,PRIMARY,2e-08,ADC,-6,2,5,NORMAL,NONE,1507822644.513\r'


QDDA Query Display Data

.. code-block:: console

    b'0\rV_AC,NONE,AUTO,VAC,5,0,OFF,1507815846.491,1,MIN_MAX_AVG,5,LIVE,0.0789,VAC,0,4,5,NORMAL,NONE,1507815852.225,PRIMARY,0.0789,VAC,0,4,5,NORMAL,NONE,1507815852.225,MINIMUM,0.0784,VAC,0,4,5,NORMAL,NONE,1507815850.213,MAXIMUM,0.0832,VAC,0,4,5,NORMAL,NONE,1507815848.201,AVERAGE,0.0802,VAC,0,4,5,NORMAL,NONE,1507815852.225\r'
    b'0\rMV_AC,NONE,AUTO,VAC,50,-3,OFF,1507822661.921,1,MIN_MAX_AVG,5,LIVE,0.01304,VAC,-3,3,5,NORMAL,NONE,1507822668.459,PRIMARY,0.01304,VAC,-3,3,5,NORMAL,NONE,1507822668.459,MINIMUM,0.012975,VAC,-3,3,5,NORMAL,NONE,1507822661.921,MAXIMUM,0.013086,VAC,-3,3,5,NORMAL,NONE,1507822667.056,AVERAGE,0.01305,VAC,-3,3,5,NORMAL,NONE,1507822668.459\r'
    b'0\rV_DC,NONE,AUTO,VDC,5,0,OFF,1507822673.907,1,MIN_MAX_AVG,5,LIVE,0.0002,VDC,0,4,5,NORMAL,NONE,1507822676.623,PRIMARY,0.0002,VDC,0,4,5,NORMAL,NONE,1507822676.623,MINIMUM,-0.0054,VDC,0,4,5,NORMAL,NONE,1507822674.209,MAXIMUM,0.0032,VDC,0,4,5,NORMAL,NONE,1507822674.611,AVERAGE,0.0002,VDC,0,4,5,NORMAL,NONE,1507822676.623\r'
    b'0\rMV_DC,NONE,AUTO,VDC,50,-3,OFF,0.000,1,MIN_MAX_AVG,5,LIVE,1e+38,VDC,-3,3,5,INVALID,NONE,1507822680.232,PRIMARY,1e+38,VDC,-3,3,5,INVALID,NONE,1507822680.232,MINIMUM,1e+38,NONE,0,0,5,INVALID,NONE,0.000,MAXIMUM,1e+38,NONE,0,0,5,INVALID,NONE,0.000,AVERAGE,1e+38,NONE,0,0,5,INVALID,NONE,0.000\r'
    b'0\rOHMS,NONE,AUTO,OHM,500,6,OFF,1507822752.018,1,MIN_MAX_AVG,5,LIVE,1e+38,OHM,6,1,4,OL,NONE,1507822760.769,PRIMARY,1e+38,OHM,6,1,4,OL,NONE,1507822760.769,MINIMUM,1e+38,OHM,6,1,4,OL,NONE,1507822752.018,MAXIMUM,1e+38,OHM,6,1,4,OL,NONE,1507822752.018,AVERAGE,1e+38,NONE,0,0,5,INVALID,NONE,1507822760.769\r'
    b'0\rDIODE_TEST,NONE,MANUAL,VDC,5,0,OFF,0.000,0,2,LIVE,1e+38,VDC,0,4,5,OL,NONE,1507815862.459,PRIMARY,1e+38,VDC,0,4,5,OL,NONE,1507815862.459\r'
    b'0\rMA_DC,NONE,AUTO,ADC,50,-3,OFF,0.000,0,2,LIVE,1e-06,ADC,-3,3,5,NORMAL,NONE,1507815864.446,PRIMARY,1e-06,ADC,-3,3,5,NORMAL,NONE,1507815864.446\r'
    b'0\rUA_DC,NONE,AUTO,ADC,500,-6,OFF,0.000,0,2,LIVE,3e-08,ADC,-6,2,5,NORMAL,NONE,1507822580.765,PRIMARY,3e-08,ADC,-6,2,5,NORMAL,NONE,1507822580.765\r'


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

