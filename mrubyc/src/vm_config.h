/*! @file
  @brief
  Global configration of mruby/c VM's

  <pre>
  Copyright (C) 2015 Kyushu Institute of Technology.
  Copyright (C) 2015 Shimane IT Open-Innovation Center.

  This file is distributed under BSD 3-Clause License.


  </pre>
*/

/* custom config for research */
#define HEAP_EXPAND
#ifdef HEAP_EXPAND

#define MRBC_ALLOC_FLI_BIT_WIDTH 25
#define MRBC_ALLOC_SLI_BIT_WIDTH 3
#define MRBC_ALLOC_IGNORE_LSBS	  4
#define MRBC_ALLOC_MEMSIZE_T     uint32_t

#define MAX_REGS_SIZE 2000
#define MAX_CALLINFO_SIZE 500
#define MAX_OBJECT_COUNT 2000
#endif


/* GC_MODE */
#define REFERENCE_COUNT 0
#define MARKSWEEP 1
#define BITMAP_MARKING 2
#define MARKSWEEP_DEBUG 3
#define BITMAP_MARKING_DEBUG 4

#define GC_MODE (MARKSWEEP)

#if (GC_MODE == REFERENCE_COUNT)
#define GC_RC
#endif

#if (GC_MODE == MARKSWEEP)
#define GC_MS
#define GC_MS_OR_BM
#endif

#if (GC_MODE == BITMAP_MARKING)
#define GC_BM
#define GC_MS_OR_BM
#endif

#if (GC_MODE == MARKSWEEP_DEBUG)
#define GC_MS
#define GC_RC
#define RC_REF_STOP
#define GC_MS_OR_BM
#define GC_MS_DEBUG
#endif

#if (GC_MODE == BITMAP_MARKING_DEBUG)
#define GC_BM
#define GC_RC
#define RC_REF_STOP
#define GC_MS_OR_BM
#define GC_BM_DEBUG
#endif

#ifdef GC_MS_OR_BM
#define MARK_STACK_SIZE 500000
#endif

/* custom config for research */

#define BENCHMARK_MODE

#ifndef BENCHMARK_MODE
#define MRBC_DEBUG
#endif


#ifndef MRBC_SRC_VM_CONFIG_H_
#define MRBC_SRC_VM_CONFIG_H_

/* maximum number of VMs */
#ifndef MAX_VM_COUNT
#define MAX_VM_COUNT 5
#endif

/* maximum size of registers */
#ifndef MAX_REGS_SIZE
#define MAX_REGS_SIZE 100
#endif

/* maximum size of callinfo (callstack) */
#ifndef MAX_CALLINFO_SIZE
#define MAX_CALLINFO_SIZE 100
#endif

/* maximum number of objects */
#ifndef MAX_OBJECT_COUNT
#define MAX_OBJECT_COUNT 400
#endif

/* maximum number of classes */
#ifndef MAX_CLASS_COUNT
#define MAX_CLASS_COUNT 20
#endif

/* maximum number of symbols */
#ifndef MAX_SYMBOLS_COUNT
#define MAX_SYMBOLS_COUNT 300
#endif

/* maximum size of global objects */
#ifndef MAX_GLOBAL_OBJECT_SIZE
#define MAX_GLOBAL_OBJECT_SIZE 50
#endif

/* maximum size of consts */
#ifndef MAX_CONST_COUNT
#define MAX_CONST_COUNT 20
#endif


/* Configure environment */
/* 0: NOT USE */
/* 1: USE */

/* USE Float. Support Float class */
#define MRBC_USE_FLOAT 1

/* USE Math class */
#define MRBC_USE_MATH 1

/* USE String. Support String class */
#define MRBC_USE_STRING 1



/* Hardware dependent flags */

/* Endian
   Define either MRBC_BIG_ENDIAN or MRBC_LITTLE_ENDIAN.
*/
#if !defined(MRBC_BIG_ENDIAN) && !defined(MRBC_LITTLE_ENDIAN)
# define MRBC_LITTLE_ENDIAN
#endif

/* 32it alignment
   If 32-bit alignment is required, enable the following line.
 */
// #define MRBC_REQUIRE_32BIT_ALIGNMENT

#endif
