/****************************************************************************
 * papi.git/src/examples/PAPI_hw_info.c (modified by jgphpc)
 * see https://bitbucket.org/icl/papi/src/master/LICENSE.txt
 *
 * This is a simple low level example for getting information on the system *
 * hardware. This function PAPI_get_hardware_info(), returns a pointer to a *
 * structure of type PAPI_hw_info_t, which contains number of CPUs, nodes,  *
 * vendor number/name for CPU, CPU revision, clock speed.                   *
 ****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include "papi.h" /* This needs to be included every time you use PAPI */

int main()
{
   const PAPI_hw_info_t *hwinfo = NULL;
   int retval;
  
   /*************************************************************************** 
   *  This part initializes the library and compares the version number of the*
   * header file, to the version of the library, if these don't match then it *
   * is likely that PAPI won't work correctly.If there is an error, retval    *
   * keeps track of the version number.                                       *
   ***************************************************************************/


   if((retval = PAPI_library_init(PAPI_VER_CURRENT)) != PAPI_VER_CURRENT )
   {
      printf("Library initialization error! \n");
      exit(1);
   }
     
   /* Get hardware info*/      
   if ((hwinfo = PAPI_get_hardware_info()) == NULL)
   {
      printf("PAPI_get_hardware_info error! \n");
      exit(1);
   }
   /* when there is an error, PAPI_get_hardware_info returns NULL */

   /*
   # --- AMD EPYC 7742 64-Core Processor (vendor 2)
   # ------------- cnode sockets numa  physical logical
   # -------------               nodes cores    cores
   cnode           1     -       -     -        -
   sockets         2     1       -     -        -
   numa_nodes      8     4       1     -        -
   physical_cores  128   64      16    1        -
   logical_cores   256   128     32    2        1
   */
   int sockets_per_cnode = hwinfo->sockets; // 2
   int numa_regions_per_cnode = hwinfo->nnodes; // 8
   int numa_regions_per_socket = numa_regions_per_cnode / hwinfo->sockets;
   int smt_threads_per_core = hwinfo->threads; // 2
   int physical_cores_per_socket = hwinfo->cores; // 64
   int physical_cores_per_cnode = physical_cores_per_socket * sockets_per_cnode; // 128
   int physical_cores_per_numa_region = physical_cores_per_cnode / numa_regions_per_cnode; // 16
   int logical_cores_per_socket = physical_cores_per_socket * smt_threads_per_core;
   int logical_cores_per_numa_region = hwinfo->ncpu ; // 32
   int logical_cores = hwinfo->totalcpus;
   //
   printf("# --- %s (vendor %d)\n", hwinfo->model_string, hwinfo->vendor);
   printf("# ------------- cnode socket numa    physical logical\n");
   printf("# -------------              region  core     core\n");
   //
   printf("cnode           |  1| |   -| |   -|  |  -|    |  -|\n");
   // 
   printf("sockets         |%3d| |   1| |   -|  |  -|    |  -|\n", \
   sockets_per_cnode);
   //
   printf("numa_node|reg   |%3d| | %3d| |   1|  |  -|    |  -|\n", \
   numa_regions_per_cnode, \
   numa_regions_per_socket);
   //
   printf("physical_cores  |%3d| | %3d| | %3d|  |  1|    |  -|\n", \
   physical_cores_per_cnode, \
   physical_cores_per_socket, \
   physical_cores_per_numa_region);
   //
   printf("logical_cores   |%3d| | %3d| | %3d|  |%3d|    |  1|\n", \
   logical_cores, \
   logical_cores_per_socket, \
   logical_cores_per_numa_region, \
   smt_threads_per_core);
   printf("# -------------------------------------------------- \n");

   /* {{{
   // Total cores              : 256
   // SMT threads per core     : 2
   // Cores per socket         : 64
   // Sockets                  : 2
   // Cores per NUMA region    : 32
   // NUMA regions             : 8
   //
   // ncpu: 32        logical_cores_per_numa_region
   // threads: 2      smt_threads_per_core
   // cores: 64       physical_cores_per_socket
   // sockets: 2      sockets_per_cnode
   // numanodes: 8    numa_regions_per_cnode
   // totalcpus: 256  logical_cores
   printf("ncpu: %d\n", hwinfo->ncpu);
   printf("threads: %d\n", hwinfo->threads);
   printf("cores: %d\n", hwinfo->cores);
   printf("sockets: %d\n", hwinfo->sockets);
   printf("numanodes: %d\n", hwinfo->nnodes);
   printf("totalcpus: %d\n", hwinfo->totalcpus);
   printf("vendor: %d\n", hwinfo->vendor);
   printf("vendor_string: %s\n", hwinfo->vendor_string);
   printf("model: %d\n", hwinfo->model);
   printf("model_string: %s\n", hwinfo->model_string);
   printf("revision: %f\n", hwinfo->revision);
   printf("cpuid_family: %d\n", hwinfo->cpuid_family);
   printf("cpuid_model: %d\n", hwinfo->cpuid_model);
   printf("cpuid_stepping: %d\n", hwinfo->cpuid_stepping);
   printf("cpu_max_mhz: %d\n", hwinfo->cpu_max_mhz);
   printf("cpu_min_mhz: %d\n", hwinfo->cpu_min_mhz);
   // printf("mem_hierarchy: %d\n", hwinfo->mem_hierarchy); // PAPI_mh_info_t mem_hierarchy
   printf("virtualized: %d\n", hwinfo->virtualized);
   printf("virtual_vendor_string: %s\n", hwinfo->virtual_vendor_string);
   printf("virtual_vendor_version: %s\n", hwinfo->virtual_vendor_version);
   printf("mhz: %f\n", hwinfo->mhz);
   printf("clock_mhz: %d\n", hwinfo->clock_mhz);
   // printf("reserved: %d\n", hwinfo->reserved); // int reserved [8]
   }}} */ 

   /* clean up */ 
   PAPI_shutdown();

   exit(0);

}
