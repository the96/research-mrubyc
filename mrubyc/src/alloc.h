/*! @file
  @brief
  mrubyc memory management.

  <pre>
  Copyright (C) 2015-2018 Kyushu Institute of Technology.
  Copyright (C) 2015-2018 Shimane IT Open-Innovation Center.

  This file is distributed under BSD 3-Clause License.

  Memory management for objects in mruby/c.

  </pre>
*/

#ifndef MRBC_SRC_ALLOC_H_
#define MRBC_SRC_ALLOC_H_

#ifdef __cplusplus
extern "C" {
#endif


#ifdef GC_MS_OR_BM
#include "class.h"
typedef enum {
  BT_OBJECT = 0,
  BT_CALLINFO,
  BT_CLASS,
  BT_INSTANCE,
  BT_PROC,
  BT_ARRAY,
  BT_STRING,
  BT_RANGE,
  BT_HASH,
  BT_ARRAY_DATA,
  BT_STRING_DATA,
  BT_HASH_DATA,
  BT_KV_DATA,
  BT_KV_HANDLE,
  BT_NAME,
  BT_SYMBOL,
  BT_IREP,
  BT_POOLS,
  BT_TCB,
  BT_MUTEX,
  BT_VM,
  BT_PATTERN,
  BT_OTHER,
} block_type;
#endif /* GC_MS_OR_BM */

struct VM;
// memory block header
typedef struct USED_BLOCK {
  unsigned int         t : 1;       //!< FLAG_TAIL_BLOCK or FLAG_NOT_TAIL_BLOCK
  unsigned int         f : 1;       //!< FLAG_FREE_BLOCK or BLOCK_IS_NOT_FREE
#ifdef GC_MS
  unsigned int         m : 1;       //!< mark bit
#endif /* GC_MS */
#ifdef GC_MS_OR_BM
  block_type           bt: 5;       //!< type of object in block
#endif /* GC_MS_OR_BM */
  uint8_t              vm_id;       //!< mruby/c VM ID

  MRBC_ALLOC_MEMSIZE_T size;        //!< block size, header included
  MRBC_ALLOC_MEMSIZE_T prev_offset; //!< offset of previous physical block
} USED_BLOCK;

typedef struct FREE_BLOCK {
  unsigned int         t : 1;       //!< FLAG_TAIL_BLOCK or FLAG_NOT_TAIL_BLOCK
  unsigned int         f : 1;       //!< FLAG_FREE_BLOCK or BLOCK_IS_NOT_FREE
#ifdef GC_MS
  unsigned int         m : 1;       //!< mark bit
#endif /* GC_MS */
#ifdef GC_MS_OR_BM
  block_type           bt: 5;       //!< type of object in block
#endif /* GC_MS_OR_BM */
  uint8_t              vm_id;       //!< dummy

  MRBC_ALLOC_MEMSIZE_T size;        //!< block size, header included
  MRBC_ALLOC_MEMSIZE_T prev_offset; //!< offset of previous physical block

  struct FREE_BLOCK *next_free;
  struct FREE_BLOCK *prev_free;
} FREE_BLOCK;


void mrbc_init_alloc(void *ptr, unsigned int size);
void *mrbc_raw_alloc(unsigned int size);
void mrbc_raw_free(void *ptr);
void *mrbc_raw_realloc(void *ptr, unsigned int size);
#if defined(GC_RC) && !defined(RC_OPERATION_ONLY)
void *mrbc_alloc(const struct VM *vm, unsigned int size);
#endif /* #if GC_RC and !RC_OPERATION_ONLY */
#ifdef GC_MS_OR_BM
void * mrbc_alloc(const struct VM *vm, unsigned int size, unsigned int block_type);
#endif /* GC_MS_OR_BM */
void *mrbc_realloc(void *ptr, unsigned int size);
void mrbc_free(const struct VM *vm, void *ptr);
void mrbc_free_all(const struct VM *vm);
void mrbc_set_vm_id(void *ptr, int vm_id);
int mrbc_get_vm_id(void *ptr);

// for statistics or debug. (need #define MRBC_DEBUG)
void mrbc_alloc_statistics(int *total, int *used, int *free, int *fragmentation);
int mrbc_alloc_vm_used(int vm_id);

#ifdef GC_MS_OR_BM
void ready_marksweep_static();
void end_marksweep_static();
void push_root_stack(mrbc_instance *obj);
mrbc_instance * pop_root_stack();
void push_mrbc_value_for_root_stack(mrbc_value *obj);
void add_vm_set(struct VM *vm);
void remove_vm_set(struct VM *vm);
void mrbc_mark_sweep();
void mrbc_mark();
void mrbc_sweep();
void print_heap_summary();
#endif

#if defined(GC_MS_DEBUG) || defined (GC_BM_DEBUG)
void heap_dump();
#endif /* GC_MS_DEBUG or GC_BM_DEBUG */

#ifdef __cplusplus
}
#endif
#endif
