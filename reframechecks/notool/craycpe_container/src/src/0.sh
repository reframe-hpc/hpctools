#!/bin/bash

# srun --pty -Cmc -Ausup -N1 --ntasks-per-node=1 -t10 sarus run \
# --mount=type=bind,src=/var/spool/slurmd,target=/var/spool/slurmd \
# --mount=type=bind,src=/var/lib/hugetlbfs,target=/var/lib/hugetlbfs \
# --mount=type=bind,src=/dev/infiniband,target=/dev/infiniband \
# --mount=type=bind,src=$PWD/src,target=/usr/local/games/ \
# load/cray/hpe_cpe:1.4.1

# {{{ build with sarus OK:
# srun -Cmc -Ausup -n1 -t2 \
# sarus run \
# --mount=type=bind,source="/var/spool/slurmd",destination="/var/spool/slurmd" \
# --mount=type=bind,source="/var/lib/hugetlbfs",destination="/var/lib/hugetlbfs" \
# --mount=type=bind,source="/dev/infiniband",destination="/dev/infiniband" \
# --mount=type=bind,source="$PWD",destination="/rfm_workdir" \
# --mount=type=bind,source="$PWD/src/valid/CPE-licfile.dat",destination="/opt/cray/pe/craype/2.7.9/AutoPass/Lic/CPE-licfile.dat" \
# load/cray/hpe_cpe:1.4.1 \
# bash -c "module purge;module load cpe-cray craype craype-x86-rome libfabric craype-network-ofi cray-mpich cray-libsci cce xpmem
# cray-dsmml;module rm xpmem;export PKG_CONFIG_PATH=/opt/cray/pe/dsmml/default/dsmml/lib/pkgconfig:$PKG_CONFIG_PATH;ls -la  ;CC --
# version"
# }}}

# {{{ check pe:
echo "# ---"
cd /rfm_workdir
ls -la
echo "# ---"
export TOPJG=$PWD
echo TOPJG=$TOPJG

# gnu:
# cp /usr/local/games/valid/CPE-licfile.dat /opt/cray/pe/craype/2.7.9/AutoPass/Lic/CPE-licfile.dat
## cp $TOPJG/src/valid/CPE-licfile.dat /opt/cray/pe/craype/2.7.9/AutoPass/Lic/CPE-licfile.dat

echo "# --- mo list:"
module list 2>&1
# echo "# --- purge:"
# module purge
# module load cpe-gnu craype craype-x86-rome libfabric craype-network-ofi cray-mpich cray-libsci gcc/10.2.0 xpmem cray-dsmml
# module rm xpmem
# export PKG_CONFIG_PATH=/opt/cray/pe/dsmml/default/dsmml/lib/pkgconfig:$PKG_CONFIG_PATH
# module list 2>&1
# echo "# --- CC version:"
# CC --version 2>&1
# cp -a /usr/local/games .
ls -la *
# }}}

# {{{ sed:
echo "# --- sed:"
sed -i "s@GIT_REPOSITORY@URL \"$TOPJG/src/googletest.git\"\n#@" $TOPJG/src/SPH-EXA_mini-app.git/domain/test/CMakeLists.txt.in
sed -i 's@GIT_TAG@#@' $TOPJG/src/SPH-EXA_mini-app.git/domain/test/CMakeLists.txt.in
cat $TOPJG/src/SPH-EXA_mini-app.git/domain/test/CMakeLists.txt.in
sed -i 's@(add_subdirectory(evrard))@# @' $TOPJG/src/SPH-EXA_mini-app.git/src/CMakeLists.txt
# --- remove -march=native:
sed -i 's@set(CMAKE_CXX_FLAGS_RELEASE@# @' $TOPJG/src/SPH-EXA_mini-app.git/CMakeLists.txt
 # }}}

# {{{ cmake config:
echo "# --- cmake version:"
export PATH=$TOPJG/src/cmake-3.21.3-linux-x86_64/bin:$PATH
cmake --version ; which cmake

echo "# --- cmake configure:"
mkdir -p $TOPJG/builddir
# -DCMAKE_CUDA_COMPILER=nvcc \

mpi_compiler=`which mpicxx &> /dev/null;echo $?`
if [ "$mpi_compiler" -eq 0 ] ;then
    myCC=mpicxx
else
    myCC=CC
fi

cmake -DCMAKE_CXX_COMPILER=$myCC \
-DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
-DCMAKE_EXE_LINKER_FLAGS=-lpthread \
-DCMAKE_CXX_FLAGS_RELEASE="-O2 -march=znver2 -DNDEBUG" \
-B $TOPJG/builddir \
-S $TOPJG/src/SPH-EXA_mini-app.git 2>&1
# }}}

# {{{ cmake make:
echo "# --- cmake make:"
cd builddir
make -j 21 help $*
# find . -name domain_2ranks  # ./domain/test/integration_mpi/domain_2ranks
# ldd /usr/local/games//src/sedov/sedov
# }}}
echo "# --- the end"
