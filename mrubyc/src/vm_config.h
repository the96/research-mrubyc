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
#define BENCHMARK_MODE

/* GC_MODE */
#define REFERENCE_COUNT 0
#define MARKSWEEP 1
#define BITMAP_MARKING 2
#define MARKSWEEP_DEBUG 3
#define BITMAP_MARKING_DEBUG 4

#ifndef GC_MODE
#define GC_MODE (MARKSWEEP_DEBUG)
#endif

/* *************************** */

#ifdef HEAP_EXPAND

#define MRBC_ALLOC_FLI_BIT_WIDTH 24
#define MRBC_ALLOC_SLI_BIT_WIDTH 4
#define MRBC_ALLOC_IGNORE_LSBS	 4
#define MRBC_ALLOC_MEMSIZE_T     uint32_t

#define MAX_REGS_SIZE 1000
#define MAX_CALLINFO_SIZE 500
#define MAX_OBJECT_COUNT 2000
#endif

/* GC_MODE DETAIL */

#if (GC_MODE == REFERENCE_COUNT)
#define GC_RC
#endif

#if (GC_MODE == MARKSWEEP)
#define GC_MS
#define GC_COUNT
#define GC_MS_OR_BM
// sweep method
#define REGENERATE_FREELIST
#endif

#if (GC_MODE == BITMAP_MARKING)
#define GC_BM
#define GC_COUNT
#define GC_MS_OR_BM
// sweep method
#define REGENERATE_FREELIST
#endif

#if (GC_MODE == MARKSWEEP_DEBUG)
#define GC_MS
#define GC_RC
#define GC_COUNT
#define RC_OPERATION_ONLY
#define GC_MS_OR_BM
#define GC_MS_DEBUG
#define GC_DEBUG
// sweep method
#define REGENERATE_FREELIST

#endif

#if (GC_MODE == BITMAP_MARKING_DEBUG)
#define GC_BM
#define GC_RC
#define GC_MS
#define GC_COUNT
#define RC_OPERATION_ONLY
#define GC_MS_OR_BM
#define GC_BM_DEBUG
#define GC_DEBUG
// markbit validity check
#define CHECK_MARK
#endif

// measure vm loop time
// #define MEASURE_VMLOOP
// measure gc time
// #define MEASURE_GC
#if defined(MEASURE_GC) && defined(GC_RC)
// count recursive release object
// #define COUNT_RECURSIVE
#endif /* MEASURE_GC && GC_RC */

#ifdef GC_MS_OR_BM
#define MARK_STACK_SIZE 500000
// #define GC_PROF
// #define ORIGINAL_OBJECT_HEADER

#ifndef ORIGINAL_OBJECT_HEADER
// #define MARKBIT_IN_OBJECT_HEADER
#endif /* ORIGINAL OBJECT_HEADER */
#endif

#ifndef BENCHMARK_MODE
#define MRBC_DEBUG
#define PRINT_OBJ_SIZE
#endif

#ifdef GC_DEBUG
// #define HEAP_DUMP
#endif
/* custom config for research */



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
