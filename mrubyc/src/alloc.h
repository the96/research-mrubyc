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

struct VM;

void mrbc_init_alloc(void *ptr, unsigned int size);
void *mrbc_raw_alloc(unsigned int size);
void mrbc_raw_free(void *ptr);
void *mrbc_raw_realloc(void *ptr, unsigned int size);
void *mrbc_alloc(const struct VM *vm, unsigned int size);
void *mrbc_realloc(const struct VM *vm, void *ptr, unsigned int size);
void mrbc_free(const struct VM *vm, void *ptr);
void mrbc_free_all(const struct VM *vm);
void mrbc_set_vm_id(void *ptr, int vm_id);
int mrbc_get_vm_id(void *ptr);

// for statistics or debug. (need #define MRBC_DEBUG)
void mrbc_alloc_statistics(int *total, int *used, int *free, int *fragmentation);
int mrbc_alloc_vm_used(int vm_id);

#ifdef GC_MS_OR_BM
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
void ready_marksweep_static();
void end_marksweep_static();
void push_root_stack(mrbc_instance *obj);
mrbc_instance * pop_root_stack();
void push_mrbc_value_for_root_stack(mrbc_value *obj);
void add_vm_set(struct VM *vm);
void remove_vm_set(struct VM *vm);
#endif

#ifdef __cplusplus
}
#endif
#endif
