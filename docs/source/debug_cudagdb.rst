NVIDIA CUDA GDB
===============

.. https://docs.nvidia.com/cuda/cuda-gdb/index.html

`CUDA-GDB <https://docs.nvidia.com/cuda/cuda-gdb/index.html>`__ is the NVIDIA
tool for debugging CUDA applications running on GPUs.

Running the test
----------------

The test can be run from the command-line:

.. code-block:: bash

 module load reframe
 cd hpctools.git/reframechecks/debug/

 ~/reframe.git/reframe.py \
 -C ~/reframe.git/config/cscs.py \
 --system daint:gpu \
 --prefix=$SCRATCH -r \
 -p PrgEnv-gnu \
 --keep-stage-files \
 -c ./cuda_gdb.py

A successful ReFrame output will look like the following:

.. literalinclude:: ../../reframechecks/debug/res/cuda-gdb/cuda-gdb.res
  :lines: 1-11

.. .. code-block:: bash

 Reframe version: 3.0-dev6 (rev: e0f8d969)
 Launched on host: daint101

Looking into the :class:`Class <reframechecks.debug.cuda_gdb.SphExaCudaGdbCheck>`
shows how to setup and run the code with the tool. 

Bug reporting
-------------

Running cuda-gdb in batch mode is possible with a input file
that specify the commands to execute at runtime:

.. literalinclude:: ../../reframechecks/debug/src_cuda/GDB/gdb.input
  :lines: 10-14, 20-23, 100-101, 105-107, 111-112

cuda-gdb supports user-defined functions (via the define command):

.. literalinclude:: ../../reframechecks/debug/src_cuda/GDB/gdb.input
  :lines: 124-127
  :emphasize-lines: 4

You can also extend GDB using the Python programming language. An example of 
GDB's Python API usage is:

.. literalinclude:: ../../reframechecks/debug/src_cuda/GDB/sms.py
  :lines: 4-8
  :emphasize-lines: 4

An overview of the debugging data will typically look like this:

.. literalinclude:: ../../reframechecks/debug/res/cuda-gdb/cuda-gdb.res
  :lines: 15-35
