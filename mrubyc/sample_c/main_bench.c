/*
 * Sample Main Program
 */

#include <stdio.h>
#include <stdlib.h>
#include "mrubyc.h"
#include "c_ext.h"
#include <time.h>
#include <math.h>

#define MEMORY_SIZE (1024*32)

uint8_t * load_mrb_file(const char *filename)
{
  FILE *fp = fopen(filename, "rb");

  if( fp == NULL ) {
    fprintf(stderr, "File not found\n");
    return NULL;
  }

  // get filesize
  fseek(fp, 0, SEEK_END);
  size_t size = ftell(fp);
  fseek(fp, 0, SEEK_SET);

  // allocate memory
  uint8_t *p = malloc(size);
  if( p != NULL ) {
    fread(p, sizeof(uint8_t), size, fp);
  } else {
    fprintf(stderr, "Memory allocate error.\n");
  }
  fclose(fp);

  return p;
}


void mrubyc(uint8_t *mrbbuf, uint8_t *memory_pool, size_t memory_pool_size)
{
  struct VM *vm;
  struct timespec vm_start, vm_end;

#ifdef GC_MS_OR_BM
  ready_marksweep_static();
#endif

  mrbc_init_alloc(memory_pool, memory_pool_size);
  init_static();
  mrbc_init_class_extension(0);

  vm = mrbc_vm_open(NULL);
  if( vm == 0 ) {
    return;
  }

  if( mrbc_load_mrb(vm, mrbbuf) != 0 ) {
    return;
  }

  mrbc_vm_begin(vm);
  clock_gettime(CLOCK_MONOTONIC_RAW, &vm_start);
  mrbc_vm_run(vm);
  clock_gettime(CLOCK_MONOTONIC_RAW, &vm_end);
  double vm_time = (double)(vm_end.tv_sec - vm_start.tv_sec) + (double)(vm_end.tv_nsec - vm_start.tv_nsec) * 1.0E-9;
  printf("size %ld\n", memory_pool_size);
  printf("vm time %.9lf\n", vm_time);
  mrbc_vm_end(vm);
  mrbc_vm_close(vm);
  
#ifdef GC_MS_OR_BM
  end_marksweep_static();
#endif /* GC_MS_OR_BM */
}


int main(int argc, char *argv[])
{
  int prog_start = 1;
  size_t memory_pool_size = MEMORY_SIZE;
  uint8_t *memory_pool;
  uint8_t *mrb_buf;

  if (argc >= prog_start + 2 &&
      strcmp(argv[prog_start], "-m") == 0) {
    memory_pool_size = atoi(argv[prog_start + 1]);
    prog_start += 2;
  }

  if( argc != prog_start + 1 ) {
    printf("Usage: %s <xxxx.mrb>\n", argv[0]);
    return 1;
  }

  memory_pool = (uint8_t *)malloc(memory_pool_size);
  if ( memory_pool == 0 ) return 1;

  mrb_buf = load_mrb_file( argv[prog_start] );
  if ( mrb_buf == 0 ) return 1;

  mrubyc( mrb_buf, memory_pool, memory_pool_size );
  free( memory_pool );
  free( mrb_buf );

  return 0;
}
