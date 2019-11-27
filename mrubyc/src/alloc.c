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

#include "vm_config.h"
#include <stddef.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>
#include "vm.h"
#include "alloc.h"
#include "console.h"

#ifdef GC_MS_OR_BM
#include "global.h"
#include "keyvalue.h"
#include "c_array.h"
#include "c_hash.h"
#include "c_range.h"
#include "c_string.h"
#include "class.h"
#endif /* GC_MS_OR_BM */

#include <stdio.h>
#ifdef GC_DEBUG
#endif /* GC_DEBUG */

// Layer 1st(f) and 2nd(s) model
// last 4bit is ignored
// f : size
// 0 : 0000-007f
// 1 : 0080-00ff
// 2 : 0100-01ff
// 3 : 0200-03ff
// 4 : 0400-07ff
// 5 : 0800-0fff
// 6 : 1000-1fff
// 7 : 2000-3fff
// 8 : 4000-7fff
// 9 : 8000-ffff

#ifndef HEAP_EXPAND
#ifndef MRBC_ALLOC_FLI_BIT_WIDTH	// 0000 0000 0000 0000
# define MRBC_ALLOC_FLI_BIT_WIDTH 25	// ~~~~~~~~~~~
#endif
#ifndef MRBC_ALLOC_SLI_BIT_WIDTH	// 0000 0000 0000 0000
# define MRBC_ALLOC_SLI_BIT_WIDTH 3	//            ~~~
#endif
#ifndef MRBC_ALLOC_IGNORE_LSBS		// 0000 0000 0000 0000
# define MRBC_ALLOC_IGNORE_LSBS	  4	//                ~~~~
#endif
#ifndef MRBC_ALLOC_MEMSIZE_T
# define MRBC_ALLOC_MEMSIZE_T     uint16_t
#endif
#endif /* HEAP_EXPAND */

#define FLI(x) (((x) >> MRBC_ALLOC_SLI_BIT_WIDTH) & ((1 << MRBC_ALLOC_FLI_BIT_WIDTH) - 1))
#define SLI(x) ((x) & ((1 << MRBC_ALLOC_SLI_BIT_WIDTH) - 1))


// define flags
#define FLAG_TAIL_BLOCK     1
#define FLAG_NOT_TAIL_BLOCK 0
#define FLAG_FREE_BLOCK     1
#define FLAG_USED_BLOCK     0


#define PHYS_NEXT(p) ((uint8_t *)(p) + (p)->size)
#define PHYS_PREV(p) ((uint8_t *)(p) - (p)->prev_offset)
#define SET_PHYS_PREV(p1,p2)				\
  ((p2)->prev_offset = (uint8_t *)(p2)-(uint8_t *)(p1))

#define SET_VM_ID(p,id)							\
  (((USED_BLOCK *)((uint8_t *)(p) - sizeof(USED_BLOCK)))->vm_id = (id))
#define GET_VM_ID(p)							\
  (((USED_BLOCK *)((uint8_t *)(p) - sizeof(USED_BLOCK)))->vm_id)


// memory pool
static unsigned int memory_pool_size;
static uint8_t     *memory_pool;

// free memory block index
#define SIZE_FREE_BLOCKS \
  ((MRBC_ALLOC_FLI_BIT_WIDTH + 1) * (1 << MRBC_ALLOC_SLI_BIT_WIDTH))
static FREE_BLOCK *free_blocks[SIZE_FREE_BLOCKS + 1];

// free memory bitmap
#define MSB_BIT16 0x8000
#ifdef HEAP_EXPAND
#define MSB_BIT32 0x80000000
#endif
static uint32_t free_fli_bitmap;
static uint16_t free_sli_bitmap[MRBC_ALLOC_FLI_BIT_WIDTH + 2]; // + sentinel

#ifdef GC_MS_OR_BM
uint8_t marked_flag;
mrbc_instance **mark_stack;
mrbc_instance **root_stack;
int mark_stack_top;
int root_stack_top;
struct VM **vms;
int vm_count;
#endif /* GC_MS_OR_BM */

#ifdef GC_COUNT
int gc_count;
#endif

//================================================================
/*! Number of leading zeros.

  @param  x	target (16bit unsined)
  @retval int	nlz value
*/
static inline int nlz16(uint16_t x)
{
  if( x == 0 ) return 16;

  int n = 1;
  if((x >>  8) == 0 ) { n += 8; x <<= 8; }
  if((x >> 12) == 0 ) { n += 4; x <<= 4; }
  if((x >> 14) == 0 ) { n += 2; x <<= 2; }
  return n - (x >> 15);
}

#ifdef HEAP_EXPAND
static inline int nlz32(uint32_t x)
{
    if (x == 0) return 32;

    int n = 1;
    if ((x >> 16) == 0) { n += 16; x <<= 16; }
    if ((x >> 24) == 0) { n += 8; x <<= 8;   }
    if ((x >> 28) == 0) { n += 4; x <<= 4;   }
    if ((x >> 30) == 0) { n += 2; x <<= 2;   }
    return n - (x >> 31);
}
#endif /* HEAP_EXPAND */


//================================================================
/*! calc f and s, and returns fli,sli of free_blocks

  @param  alloc_size	alloc size
  @retval int		index of free_blocks
*/
static int calc_index(unsigned int alloc_size)
{
#ifndef HEAP_EXPAND
  // check overflow
  if( (alloc_size >> (MRBC_ALLOC_FLI_BIT_WIDTH
                      + MRBC_ALLOC_SLI_BIT_WIDTH
                      + MRBC_ALLOC_IGNORE_LSBS)) != 0) {
    return SIZE_FREE_BLOCKS;
  }
#endif /* HEAP_EXPAND */

#ifdef HEAP_EXPAND
  // calculate First Level Index.
  int fli = 32 -
    nlz32( alloc_size >> (MRBC_ALLOC_SLI_BIT_WIDTH + MRBC_ALLOC_IGNORE_LSBS) );
#else
  int fli = 16 -
    nlz16( alloc_size >> (MRBC_ALLOC_SLI_BIT_WIDTH + MRBC_ALLOC_IGNORE_LSBS) );
#endif /* HEAP_EXPAND */

  // calculate Second Level Index.
  int shift = (fli == 0) ? (fli + MRBC_ALLOC_IGNORE_LSBS) :
			   (fli + MRBC_ALLOC_IGNORE_LSBS - 1);

  int sli   = (alloc_size >> shift) & ((1 << MRBC_ALLOC_SLI_BIT_WIDTH) - 1);
  int index = (fli << MRBC_ALLOC_SLI_BIT_WIDTH) + sli;

  assert(fli >= 0);
  assert(fli <= MRBC_ALLOC_FLI_BIT_WIDTH);
  assert(sli >= 0);
  assert(sli <= (1 << MRBC_ALLOC_SLI_BIT_WIDTH) - 1);

  return index;
}


//================================================================
/*! Mark that block free and register it in the free index table.

  @param  target	Pointer to target block.
*/
static void add_free_block(FREE_BLOCK *target)
{
  target->f = FLAG_FREE_BLOCK;

  int index = calc_index(target->size) - 1;
  int fli   = FLI(index);
  int sli   = SLI(index);

#ifdef HEAP_EXPAND
  free_fli_bitmap      |= (MSB_BIT32 >> fli);
#else
  free_fli_bitmap      |= (MSB_BIT16 >> fli);
#endif /* HEAP_EXPAND */
  free_sli_bitmap[fli] |= (MSB_BIT16 >> sli);

  target->prev_free = NULL;
  target->next_free = free_blocks[index];
  if( target->next_free != NULL ) {
    target->next_free->prev_free = target;
  }
  free_blocks[index] = target;

#ifdef MRBC_DEBUG
  target->vm_id = UINT8_MAX;
  memset( (uint8_t *)target + sizeof(FREE_BLOCK), 0xff,
          target->size - sizeof(FREE_BLOCK) );
#endif

}


//================================================================
/*! just remove the free_block *target from index

  @param  target	pointer to target block.
*/
static void remove_index(FREE_BLOCK *target)
{
  // top of linked list?
  if( target->prev_free == NULL ) {
    int index = calc_index(target->size) - 1;
    free_blocks[index] = target->next_free;

    if( free_blocks[index] == NULL ) {
      int fli = FLI(index);
      int sli = SLI(index);
      free_sli_bitmap[fli] &= ~(MSB_BIT16 >> sli);
#ifdef HEAP_EXPAND
      if( free_sli_bitmap[fli] == 0 ) free_fli_bitmap &= ~(MSB_BIT32 >> fli);
#else
      if( free_sli_bitmap[fli] == 0 ) free_fli_bitmap &= ~(MSB_BIT16 >> fli);
#endif /* HEAP_EXPAND */
    }
  }
  else {
    target->prev_free->next_free = target->next_free;
  }

  if( target->next_free != NULL ) {
    target->next_free->prev_free = target->prev_free;
  }
}


//================================================================
/*! Split block by size

  @param  target	pointer to target block
  @param  size	size
  @retval NULL	no split.
  @retval FREE_BLOCK *	pointer to splitted free block.
*/
static inline FREE_BLOCK* split_block(FREE_BLOCK *target, unsigned int size)
{
  if( target->size < (size + sizeof(FREE_BLOCK)
                      + (1 << MRBC_ALLOC_IGNORE_LSBS)) ) return NULL;

  // split block, free
  FREE_BLOCK *split = (FREE_BLOCK *)((uint8_t *)target + size);
  FREE_BLOCK *next  = (FREE_BLOCK *)PHYS_NEXT(target);

  split->size  = target->size - size;
  SET_PHYS_PREV(target, split);
  split->t     = target->t;
  target->size = size;
  target->t    = FLAG_NOT_TAIL_BLOCK;
  if( split->t == FLAG_NOT_TAIL_BLOCK ) {
    SET_PHYS_PREV(split, next);
  }

  return split;
}


//================================================================
/*! merge ptr1 and ptr2 block.
    ptr2 will disappear

  @param  ptr1	pointer to free block 1
  @param  ptr2	pointer to free block 2
*/
static void merge_block(FREE_BLOCK *ptr1, FREE_BLOCK *ptr2)
{
  assert(ptr1 < ptr2);

  // merge ptr1 and ptr2
  ptr1->t     = ptr2->t;
  ptr1->size += ptr2->size;

  // update block info
  if( ptr1->t == FLAG_NOT_TAIL_BLOCK ) {
    FREE_BLOCK *next = (FREE_BLOCK *)PHYS_NEXT(ptr1);
    SET_PHYS_PREV(ptr1, next);
  }
}


//================================================================
/*! initialize

  @param  ptr	pointer to free memory block.
  @param  size	size. (max 64KB. see MRBC_ALLOC_MEMSIZE_T)
*/
void mrbc_init_alloc(void *ptr, unsigned int size)
{
  assert( size != 0 );
  assert( size <= (MRBC_ALLOC_MEMSIZE_T)(~0) );

  memory_pool      = ptr;
  memory_pool_size = size;

  // initialize memory pool
  FREE_BLOCK *block = (FREE_BLOCK *)memory_pool;
  block->t           = FLAG_TAIL_BLOCK;
  block->f           = FLAG_FREE_BLOCK;
  block->size        = memory_pool_size;
  block->prev_offset = 0;

  add_free_block(block);
}


//================================================================
/*! allocate memory

  @param  size	request size.
  @return void * pointer to allocated memory.
  @retval NULL	error.
*/
void * mrbc_raw_alloc(unsigned int size)
{
  // TODO: maximum alloc size
  //  (1 << (FLI_BIT_WIDTH + SLI_BIT_WIDTH + IGNORE_LSBS)) - alpha

  unsigned int alloc_size = size + sizeof(FREE_BLOCK);

  // align 4 byte
  alloc_size += ((4 - alloc_size) & 3);

  // check minimum alloc size. if need.
#if 0
  if( alloc_size < (1 << MRBC_ALLOC_IGNORE_LSBS) ) {
    alloc_size = (1 << MRBC_ALLOC_IGNORE_LSBS);
  }
#else
  assert( alloc_size >= (1 << MRBC_ALLOC_IGNORE_LSBS) );
#endif

  // find free memory block.
  int index = calc_index(alloc_size);
  int fli   = FLI(index);
  int sli   = SLI(index);

  FREE_BLOCK *target = free_blocks[index];

  if( target == NULL ) {
    // uses free_fli/sli_bitmap table.
    uint16_t masked = free_sli_bitmap[fli] & ((MSB_BIT16 >> sli) - 1);
    if( masked != 0 ) {
      sli = nlz16(masked);
    }
    else {
#ifdef HEAP_EXPAND
      uint32_t masked = free_fli_bitmap & ((MSB_BIT32 >> fli) - 1);
      if( masked != 0 ) {
        fli = nlz32(masked);
        sli = nlz16(free_sli_bitmap[fli]);
      }
#else
      masked = free_fli_bitmap & ((MSB_BIT16 >> fli) - 1);
      if( masked != 0 ) {
        fli = nlz16(masked);
        sli = nlz16(free_sli_bitmap[fli]);
      }
#endif /* HEAP_EXPAND */
      else {
        // out of memory
        // console_print("Fatal error: Out of memory.\n");
        return NULL;  // ENOMEM
      }
    }
    assert(fli >= 0);
    assert(fli <= MRBC_ALLOC_FLI_BIT_WIDTH);
    assert(sli >= 0);
    assert(sli <= (1 << MRBC_ALLOC_SLI_BIT_WIDTH) - 1);

    index = (fli << MRBC_ALLOC_SLI_BIT_WIDTH) + sli;
    target = free_blocks[index];
    assert( target != NULL );
  }
  assert(target->size >= alloc_size);

  // remove free_blocks index
  target->f          = FLAG_USED_BLOCK;
  free_blocks[index] = target->next_free;

  if( target->next_free == NULL ) {
    free_sli_bitmap[fli] &= ~(MSB_BIT16 >> sli);
#ifdef HEAP_EXPAND
    if( free_sli_bitmap[fli] == 0 ) free_fli_bitmap &= ~(MSB_BIT32 >> fli);
#else
    if( free_sli_bitmap[fli] == 0 ) free_fli_bitmap &= ~(MSB_BIT16 >> fli);
#endif
  }
  else {
    target->next_free->prev_free = NULL;
  }

  // split a block
  FREE_BLOCK *release = split_block(target, alloc_size);
  if( release != NULL ) {
    add_free_block(release);
  }

#ifdef MRBC_DEBUG
  memset( (uint8_t *)target + sizeof(USED_BLOCK), 0xaa,
          target->size - sizeof(USED_BLOCK) );
#endif
  target->vm_id = 0;

  return (uint8_t *)target + sizeof(USED_BLOCK);
}


//================================================================
/*! release memory

  @param  ptr	Return value of mrbc_raw_alloc()
*/
void mrbc_raw_free(void *ptr)
{
  // get target block
  FREE_BLOCK *target = (FREE_BLOCK *)((uint8_t *)ptr - sizeof(USED_BLOCK));

  // check next block, merge?
  FREE_BLOCK *next = (FREE_BLOCK *)PHYS_NEXT(target);

  if((target->t == FLAG_NOT_TAIL_BLOCK) && (next->f == FLAG_FREE_BLOCK)) {
    remove_index(next);
    merge_block(target, next);
  }

  // check previous block, merge?
  FREE_BLOCK *prev = (FREE_BLOCK *)PHYS_PREV(target);

  if((prev != NULL) && (prev->f == FLAG_FREE_BLOCK)) {
    remove_index(prev);
    merge_block(prev, target);
    target = prev;
  }

  // target, add to index
  add_free_block(target);
}



//================================================================
/*! re-allocate memory

  @param  ptr	Return value of mrbc_raw_alloc()
  @param  size	request size
  @return void * pointer to allocated memory.
  @retval NULL	error.
*/
void * mrbc_raw_realloc(void *ptr, unsigned int size)
{
  USED_BLOCK  *target     = (USED_BLOCK *)((uint8_t *)ptr - sizeof(USED_BLOCK));
  unsigned int alloc_size = size + sizeof(FREE_BLOCK);

  // align 4 byte
  alloc_size += ((4 - alloc_size) & 3);

  // expand? part1.
  // next phys block is free and enough size?
  if( alloc_size > target->size ) {
    FREE_BLOCK *next = (FREE_BLOCK *)PHYS_NEXT(target);
    if((target->t == FLAG_NOT_TAIL_BLOCK) &&
       (next->f == FLAG_FREE_BLOCK) &&
       ((target->size + next->size) >= alloc_size)) {
      remove_index(next);
      merge_block((FREE_BLOCK *)target, next);

      // and fall through.
    }
  }

  // same size?
  if( alloc_size == target->size ) {
    return (uint8_t *)ptr;
  }

  // shrink?
  if( alloc_size < target->size ) {
    FREE_BLOCK *release = split_block((FREE_BLOCK *)target, alloc_size);
    if( release != NULL ) {
      // check next block, merge?
      FREE_BLOCK *next = (FREE_BLOCK *)PHYS_NEXT(release);
      if((release->t == FLAG_NOT_TAIL_BLOCK) && (next->f == FLAG_FREE_BLOCK)) {
        remove_index(next);
        merge_block(release, next);
      }
      add_free_block(release);
    }

    return (uint8_t *)ptr;
  }

  // expand part2.
  // new alloc and copy
  uint8_t *new_ptr = mrbc_raw_alloc(size);
  if( new_ptr == NULL ) return NULL;  // ENOMEM

  memcpy(new_ptr, ptr, target->size - sizeof(USED_BLOCK));
  SET_VM_ID(new_ptr, target->vm_id);

  mrbc_raw_free(ptr);

  return new_ptr;
}



//// for mruby/c
#if defined(GC_RC) && !defined(RC_OPERATION_ONLY)
//================================================================
/*! allocate memory

  @param  vm	pointer to VM.
  @param  size	request size.
  @return void * pointer to allocated memory.
  @retval NULL	error.
*/
void * mrbc_alloc(const struct VM *vm, unsigned int size)
{
  uint8_t *ptr = mrbc_raw_alloc(size);
  if( ptr == NULL ) {
    console_printf("Fatal error: Out of memory.\n");
    exit(1);	// ENOMEM
  }
  if( vm ) SET_VM_ID(ptr, vm->vm_id);

  return ptr;
}

//================================================================
/*! re-allocate memory

  @param  vm	pointer to VM.
  @param  ptr	Return value of mrbc_alloc()
  @param  size	request size.
  @return void * pointer to allocated memory.
  @retval NULL	error.
*/
void * mrbc_realloc(void *ptr, unsigned int size)
{
  uint8_t *new_ptr = mrbc_raw_realloc(ptr, size);
  if (new_ptr == NULL) {
    console_printf("Fatal error: Out of memory.\n");
    exit(1);	// ENOMEM
  }

  return new_ptr;
}
#endif /* GC_RC and !RC_OPERATION_ONLY */

#ifdef GC_MS_OR_BM
//================================================================
/*! allocate memory

  @param  vm	pointer to VM.
  @param  size	request size.
  @return void * pointer to allocated memory.
  @retval NULL	error.
*/
void * mrbc_alloc(const struct VM *vm, unsigned int size, unsigned int block_type)
{
  uint8_t *ptr = mrbc_raw_alloc(size);
  if( ptr == NULL ) {
#ifdef GC_COUNT
    gc_count++;
#endif /* GC_COUNT */
#ifdef GC_DEBUG
    printf("Triggered GC count %d\n", gc_count);
#ifdef HEAP_DUMP
    printf("allocation size: %d\n", size);
    heap_dump();
#endif /* HEAP_DUMP */
#endif /* GC_DEBUG */
    mrbc_mark();
    mrbc_sweep();
    ptr = mrbc_raw_alloc(size);
    if (ptr == NULL) {
      print_heap_summary();
      printf("allocation size: %d gc_count %d\n", size, gc_count);
      console_printf("Fatal error: Out of memory.\n");
      exit(1);	// ENOMEM
    }
  }
  USED_BLOCK *block = (USED_BLOCK *)(ptr - sizeof(USED_BLOCK));
  block->bt = block_type;
  if( vm ) block->vm_id = vm->vm_id;

  return ptr;
}
//================================================================
/*! re-allocate memory

  @param  vm	pointer to VM.
  @param  ptr	Return value of mrbc_alloc()
  @param  size	request size.
  @return void * pointer to allocated memory.
  @retval NULL	error.
*/
void * mrbc_realloc(void *ptr, unsigned int size)
{
  USED_BLOCK *header = (USED_BLOCK *)((uint8_t *)ptr - sizeof(USED_BLOCK));
  int block_type = header->bt;
  uint8_t *new_ptr = mrbc_raw_realloc(ptr, size);
  if (new_ptr == NULL) {
#ifdef GC_COUNT
    gc_count++;
#endif /* GC_COUNT */
#ifdef GC_DEBUG
    printf("Triggered GC count %d\n", gc_count);
#ifdef HEAP_DUMP
    heap_dump();
#endif /* HEAP_DUMP */
#endif /* GC_DEBUG */
    mrbc_mark();
    mrbc_sweep();
    new_ptr = mrbc_raw_realloc(ptr, size);
    if (new_ptr == NULL) {
      print_heap_summary();
      printf("allocation size: %d\n", size);
      console_printf("Fatal error: Out of memory.\n");
      exit(1);	// ENOMEM
    }
  }
  ((USED_BLOCK *)((uint8_t *)new_ptr - sizeof(USED_BLOCK)))->bt = block_type;
  return new_ptr;
}
#endif /* GC_MS_OR_BM */


//================================================================
/*! release memory

  @param  vm	pointer to VM.
  @param  ptr	Return value of mrbc_alloc()
*/
void mrbc_free(const struct VM *vm, void *ptr)
{
  mrbc_raw_free(ptr);
}


//================================================================
/*! release memory, vm used.

  @param  vm	pointer to VM.
*/
void mrbc_free_all(const struct VM *vm)
{
  USED_BLOCK *ptr = (USED_BLOCK *)memory_pool;
  void *free_target = NULL;
  int flag_loop = 1;
  int vm_id = vm->vm_id;

  while( flag_loop ) {
    if( ptr->t == FLAG_TAIL_BLOCK ) flag_loop = 0;
    if( ptr->f == FLAG_USED_BLOCK && ptr->vm_id == vm_id ) {
      if( free_target ) {
	      mrbc_raw_free(free_target);
      }
      free_target = (char *)ptr + sizeof(USED_BLOCK);
    }
    ptr = (USED_BLOCK *)PHYS_NEXT(ptr);
  }
  if( free_target ) {
    mrbc_raw_free(free_target);
  }
}


//================================================================
/*! set vm id

  @param  ptr	Return value of mrbc_alloc()
  @param  vm_id	vm id
*/
void mrbc_set_vm_id(void *ptr, int vm_id)
{
  SET_VM_ID(ptr, vm_id);
}


//================================================================
/*! get vm id

  @param  ptr	Return value of mrbc_alloc()
  @return int	vm id
*/
int mrbc_get_vm_id(void *ptr)
{
  return GET_VM_ID(ptr);
}



#ifdef MRBC_DEBUG
//================================================================
/*! statistics

  @param  *total	returns total memory.
  @param  *used		returns used memory.
  @param  *free		returns free memory.
  @param  *fragment	returns memory fragmentation
*/
void mrbc_alloc_statistics(int *total, int *used, int *free, int *fragmentation)
{
  *total = memory_pool_size;
  *used = 0;
  *free = 0;
  *fragmentation = 0;

  USED_BLOCK *ptr = (USED_BLOCK *)memory_pool;
  int flag_used_free = ptr->f;
  while( 1 ) {
    if( ptr->f ) {
      *free += ptr->size;
    } else {
      *used += ptr->size;
    }
    if( flag_used_free != ptr->f ) {
      (*fragmentation)++;
      flag_used_free = ptr->f;
    }

    if( ptr->t == FLAG_TAIL_BLOCK ) break;

    ptr = (USED_BLOCK *)PHYS_NEXT(ptr);
  }
}



//================================================================
/*! statistics

  @param  vm_id		vm_id
  @return int		total used memory size
*/
int mrbc_alloc_vm_used( int vm_id )
{
  USED_BLOCK *ptr = (USED_BLOCK *)memory_pool;
  int total = 0;

  while( 1 ) {
    if( ptr->vm_id == vm_id && !ptr->f ) {
      total += ptr->size;
    }
    if( ptr->t == FLAG_TAIL_BLOCK ) break;

    ptr = (USED_BLOCK *)PHYS_NEXT(ptr);
  }

  return total;
}

#endif


#ifdef GC_MS_OR_BM
void ready_marksweep_static()
{
  mark_stack = (mrbc_instance **) malloc(sizeof(mrbc_instance *) * MARK_STACK_SIZE);
  root_stack = (mrbc_instance **) malloc(sizeof(mrbc_instance *) * MARK_STACK_SIZE);
  if (mark_stack == 0 || root_stack == 0) {
    console_print("Fatal error: initialize allocation error\n");
    exit(1);
  }
  mark_stack_top = 0;
  root_stack_top = 0;
  vms = (struct VM **) malloc(sizeof(struct VM *) * MAX_VM_COUNT);
  vm_count = 0;
  marked_flag = 1;
#ifdef GC_COUNT
  gc_count = 0;
#endif /* GC_COUNT */
}

void end_marksweep_static()
{
#ifdef GC_COUNT
  console_printf("gc_count %d\n", gc_count);
#endif /* GC_COUNT */
  free(vms);
  free(mark_stack);
  free(root_stack);
}

void init_mark_stack()
{
  if (mark_stack_top != 0)
    console_printf("Warning: mark_stack_top is nonzero. %d\n", mark_stack_top);
  memcpy(mark_stack, root_stack, sizeof(mrbc_instance *) * root_stack_top);
  mark_stack_top = root_stack_top;
}

void push_root_stack(mrbc_instance *obj)
{
  if ((uint8_t *) obj < memory_pool || (uint8_t *) obj >= memory_pool + memory_pool_size) {
    printf("[push_root_stack] obj->tt %d\n", obj->tt);
  }
  if (root_stack_top < MARK_STACK_SIZE) {
    root_stack[root_stack_top++] = obj;
  } else {
    console_printf("Error: StackOverFlow at root_stack\n");
    exit(1);
  }
}

mrbc_instance * pop_root_stack()
{
  if (root_stack_top > 0) {
    return root_stack[--root_stack_top];
  } else {
    console_print("Error: Stack Item Exhaust at root_stack");
    exit(1);
  }
}

void push_mrbc_value_for_root_stack(mrbc_value *obj)
{
  if ((obj->tt >= MRBC_TT_OBJECT && obj->tt <= MRBC_TT_HASH) || obj->tt == MRBC_TT_CLASS) {
    push_root_stack(obj->instance);
  }
}

static inline void push_mark_stack(mrbc_instance *obj)
{
  if (mark_stack_top < MARK_STACK_SIZE) {
    mark_stack[mark_stack_top++] = obj;
  } else {
    console_print("Error: StackOverFlow at mark_stack\n");
    exit(1);
  }
}

static inline mrbc_instance * pop_mark_stack()
{
  return mark_stack[--mark_stack_top];
}

static inline void push_mrbc_value_for_mark_stack(mrbc_value *obj)
{
  if ((obj->tt >= MRBC_TT_OBJECT && obj->tt <= MRBC_TT_HASH) || obj->tt == MRBC_TT_CLASS) {
    push_mark_stack(obj->instance);
  }
}

void add_vm_set(struct VM *vm)
{
  vms[vm_count++] = vm;
}

void remove_vm_set(struct VM *vm)
{
  int i;
  for (i = 0; i < vm_count; i++) {
    if (vms[i]->vm_id == vm->vm_id) {
      memmove(vms + i, vms + i + 1, sizeof(struct VM *) * (vm_count - i));
      vm_count--;
      return;
    }
  }
  console_print("Error: VM is not found from vms.\n");
}

#ifdef GC_MS
void reverse_mark_flag()
{
  marked_flag = !marked_flag & 1;
}
#endif /* GC_MS */

void push_vm();
void mark_from_stack();

#include "symbol.h"
void mrbc_mark()
{
  int i;
  init_mark_stack();

  mrbc_kv_handle *const_h = get_const_handle();
  mrbc_kv_handle *global_h = get_global_handle();
  if (const_h->data_size > 0) {
    if ((uint8_t *)const_h->data < memory_pool || (uint8_t *)const_h->data >= memory_pool + memory_pool_size)
      printf("aaaaa\n");
    push_mark_stack((mrbc_instance *) const_h->data);
  }
  if (global_h->data_size > 0) {
    if ((uint8_t *)global_h->data < memory_pool || (uint8_t *)global_h->data >= memory_pool + memory_pool_size)
      printf("bbbb\n");
    push_mark_stack((mrbc_instance *) global_h->data);
  }
  for (i = 0; i < const_h->n_stored ; i++) {
    push_mrbc_value_for_mark_stack(&const_h->data[i].value);
  }
  for (i = 0; i < global_h->n_stored; i++) {
    push_mrbc_value_for_mark_stack(&global_h->data[i].value);
  }

  for (i = 0; i < vm_count; i++) {
    push_vm(vms[i]);
  }
  mark_from_stack();
}

void push_vm(struct VM *vm) {
  int i;
  if (vm->pc_irep != NULL)
    for (i = 0; vm->regs + i < vm->current_regs + vm->pc_irep->nregs && i < MAX_REGS_SIZE; i++) {
      push_mrbc_value_for_mark_stack(vm->regs + i);
    }

  if (vm->target_class != NULL) {
    push_mark_stack((mrbc_instance *)vm->target_class);
  }

  if (vm->callinfo_tail != NULL) {
    mrb_callinfo *callinfo = vm->callinfo_tail;
    while(1) {
      if (callinfo->target_class != NULL) {
        push_mark_stack((mrbc_instance *) callinfo->target_class);
      }
      if (callinfo->prev == NULL)
        break;
      callinfo = callinfo->prev;
    }
  }
}

#define GET_BLOCK_HEADER(obj) (USED_BLOCK *)((uint8_t *)obj - sizeof(USED_BLOCK))

#ifdef GC_MS
static inline void mark(USED_BLOCK *block) {
  block->m = marked_flag;
}
#endif
#ifdef GC_BM
static inline void mark(USED_BLOCK *block) {
// TODO
}
#endif

#ifdef GC_MS
static inline int is_marked(USED_BLOCK *block) {
  return block->m == marked_flag;
}
#endif
#ifdef GC_BM
static inline int is_marked(USED_BLOCK *block) {
// TODO
}
#endif

void mark_from_stack() {

  while (1) {
    if (mark_stack_top <= 0) break;
    mrbc_instance *obj = pop_mark_stack();
    USED_BLOCK *block = GET_BLOCK_HEADER(obj);
    if (is_marked(block)) continue;
    mark(block);
    switch (block->bt) {
      case BT_INSTANCE:
      {
        mrbc_instance *instance = obj;
        if (instance->cls == NULL) {
          push_mark_stack((mrbc_instance *)instance->cls);
        }

        if (instance->ivar.data_size != 0) {
          mark(GET_BLOCK_HEADER(instance->ivar.data));
          int i = 0;
          while (i < instance->ivar.n_stored) {
            push_mrbc_value_for_mark_stack(&instance->ivar.data[i].value);
            i++;
          }
        }
        break;
      }
      case BT_PROC:
      {
        mrbc_proc *proc = (mrbc_proc *) obj;
        if (proc->next != NULL) {
          push_mark_stack((mrbc_instance *)proc->next);
        }
        break;
      }
      case BT_ARRAY:
      {
        mrbc_array *array = (mrbc_array *) obj;
        if (array->data == NULL) break;
        mark(GET_BLOCK_HEADER(array->data));
        int i = 0;
        while (i < array->n_stored) {
          push_mrbc_value_for_mark_stack(array->data + i++);
        }
        break;
      }
      case BT_STRING:
      {
        mrbc_string *string = (mrbc_string *) obj;
        if (string->data == NULL) break;
        mark(GET_BLOCK_HEADER(string->data));
        break;
      }
      case BT_RANGE:
      {
        mrbc_range *range = (mrbc_range *) obj;
        push_mrbc_value_for_mark_stack(&range->first);
        push_mrbc_value_for_mark_stack(&range->last);
        break;
      }
      case BT_HASH:
      {
        mrbc_hash *hash = (mrbc_hash *) obj;
        if (hash->data == NULL) break;
        mark(GET_BLOCK_HEADER(hash->data));
        int i = 0;
        while (i < hash->n_stored) {
          push_mrbc_value_for_mark_stack(hash->data + i++);
        }
      }
      case BT_CLASS:
      {
        mrbc_class *class = (mrbc_class *)obj;
        if (class->super != NULL) {
          push_mark_stack((mrbc_instance *)class->super);
        }
        if (class->procs != NULL) {
          push_mark_stack((mrbc_instance *)class->procs);
        }
        break;
      }
      default:
        break;
    }
  }
}

void mrbc_sweep()
{
  USED_BLOCK *block = (USED_BLOCK *) memory_pool;
  while (block->f == FLAG_FREE_BLOCK || block->bt < BT_INSTANCE || block->bt > BT_KV_HANDLE || is_marked(block)) {
    if ((uint8_t *)block >= memory_pool + memory_pool_size)
      return;
    block = (USED_BLOCK *) PHYS_NEXT(block);
  }
  USED_BLOCK *next = (USED_BLOCK *)PHYS_NEXT(block);
  if ((uint8_t *)next >= memory_pool + memory_pool_size) {
    next = NULL;
  }
  while (1) {
    while (next->f == FLAG_FREE_BLOCK || next->bt < BT_INSTANCE || next->bt > BT_KV_HANDLE || is_marked(next)) {
      if ((uint8_t *)next >= memory_pool + memory_pool_size)
        return;
      next = (USED_BLOCK *) PHYS_NEXT(next);
    }
    mrbc_raw_free((uint8_t *)block + sizeof(USED_BLOCK));
    if (next == NULL) return;
    block = next;
    next = (USED_BLOCK *) PHYS_NEXT(block);
  }
}

#endif /* GC_MS_OR_BM */

#ifdef GC_DEBUG

char* block_type_to_name(uint8_t bt);

void print_heap_summary()
{
  printf("==[heap summary]========\n");
  FREE_BLOCK *block = (FREE_BLOCK *) memory_pool;
  FREE_BLOCK *heap_end = (FREE_BLOCK *) (memory_pool + memory_pool_size);
  int block_count, free_count, used_count;
  uint32_t used_size, free_size, max_free_size;
  block_count = free_count =  used_count = 0;
  used_size = free_size = max_free_size = 0;
  while (1) {
    if (block >= heap_end) break;
    if (block->f == FLAG_FREE_BLOCK) {
      printf("[%4d]FREE_BLOCK(%4d) size: %8d(0x%6x) offset: %8d(0x%6x) (%p)\n", 
             block_count++, free_count++, block->size, block->size, block->prev_offset, block->prev_offset, block);
      free_size += block->size;
      if (max_free_size < block->size) max_free_size = block->size;
    } else {
      block_count++;
      used_count++;
      used_size += block->size;
    }
    block = (FREE_BLOCK *) PHYS_NEXT(block);
  }
  printf("==[heap summary]=====\n");
  printf("MAX_FREE_SIZE: %d bytes\n",max_free_size);
  printf("FREE_BLOCK: %d bytes %d counts\n" , free_size, free_count);
  printf("USED_BLOCK: %d bytes %d counts\n" , used_size, used_count);
  printf("HEAP_SIZE : %d bytes\n", memory_pool_size);
  printf("======================\n");
}

void heap_dump()
{
  printf("==[heap dump]========\n");
  FREE_BLOCK *block = (FREE_BLOCK *) memory_pool;
  FREE_BLOCK *heap_end = (FREE_BLOCK *) (memory_pool + memory_pool_size);
  int block_count, free_count, used_count;
  uint32_t used_size, free_size;
  block_count = free_count =  used_count = 0;
  used_size = free_size = 0;
  while (1) {
    if (block >= heap_end) break;
    if (block->f == FLAG_FREE_BLOCK) {
      printf("[%4d]FREE_BLOCK(%4d) size: %8d(0x%6x) offset: %8d(0x%6x) (%p)\n", 
             block_count++, free_count++, block->size, block->size, block->prev_offset, block->prev_offset, block);
      free_size += block->size;
    } else {
      printf("[%4d]USED_BLOCK(%4d) size: %8d(0x%6x) offset: %8d(0x%6x) (%p) type: %s mark: %d vm_id: %d\n", 
             block_count++, used_count++, block->size, block->size, block->prev_offset, block->prev_offset, block, block_type_to_name(block->bt), is_marked((USED_BLOCK *)block), block->vm_id);
      used_size += block->size;
    }
    block = (FREE_BLOCK *) PHYS_NEXT(block);
  }
  printf("==[heap summary]=====\n");
  printf("FREE_BLOCK: %d bytes (%d) " , free_size, free_count);
  printf("USED_BLOCK: %d bytes (%d) " , used_size, used_count);
  printf("HEAP_SIZE : %d\n", memory_pool_size);
  printf("======================\n");
}

char* block_type_to_name(uint8_t bt) {
  switch (bt) {
    case BT_OBJECT      : return "Object";
    case BT_CALLINFO    : return "Callinfo";
    case BT_CLASS       : return "Class";
    case BT_INSTANCE    : return "Instance";
    case BT_PROC        : return "Proc";
    case BT_ARRAY       : return "Array";
    case BT_STRING      : return "String";
    case BT_RANGE       : return "Range";
    case BT_HASH        : return "Hash";
    case BT_ARRAY_DATA  : return "Array Data";
    case BT_STRING_DATA : return "String Data";
    case BT_HASH_DATA   : return "Hash Data";
    case BT_KV_DATA     : return "KeyValue Data";
    case BT_KV_HANDLE   : return "KeyValue Handle";
    case BT_NAME        : return "Name";
    case BT_SYMBOL      : return "Symbol";
    case BT_IREP        : return "Irep";
    case BT_POOLS       : return "Pools";
    case BT_TCB         : return "Tcb";
    case BT_MUTEX       : return "Mutex";
    case BT_VM          : return "VM";
    case BT_PATTERN     : return "Pattern";
    case BT_OTHER       : 
    default             : return "Other";
  }
}

#endif /* defined(GC_MS_DEBUG) || defined(GC_BM_DEBUG) */