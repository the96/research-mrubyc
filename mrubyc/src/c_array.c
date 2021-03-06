/*! @file
  @brief
  mruby/c Array class

  <pre>
  Copyright (C) 2015-2018 Kyushu Institute of Technology.
  Copyright (C) 2015-2018 Shimane IT Open-Innovation Center.

  This file is distributed under BSD 3-Clause License.

  </pre>
*/

#include "vm_config.h"
#include <string.h>
#include <assert.h>

#include "value.h"
#include "vm.h"
#include "alloc.h"
#include "static.h"
#include "class.h"
#include "c_array.h"
#include "c_string.h"
#include "c_range.h"
#include "console.h"
#include "opcode.h"

/*
  function summary

 (constructor)
    mrbc_array_new

 (destructor)
    mrbc_array_delete

 (setter)
  --[name]-------------[arg]---[ret]-------------------------------------------
    mrbc_array_set	*T	int
    mrbc_array_push	*T	int
    mrbc_array_unshift	*T	int
    mrbc_array_insert	*T	int

 (getter)
  --[name]-------------[arg]---[ret]---[note]----------------------------------
    mrbc_array_get		T	Data remains in the container
    mrbc_array_get_range  T Data remains in the container
    mrbc_array_pop		T	Data does not remain in the container
    mrbc_array_shift		T	Data does not remain in the container
    mrbc_array_remove		T	Data does not remain in the container

 (others)
    mrbc_array_resize
    mrbc_array_clear
    mrbc_array_compare
    mrbc_array_minmax
*/


//================================================================
/*! constructor

  @param  vm	pointer to VM.
  @param  size	initial size
  @return 	array object
  gc infomation:
   * gc trigger
*/
mrbc_value mrbc_array_new(struct VM *vm, int size)
{
  mrbc_value value = {.tt = MRBC_TT_ARRAY};

  /*
    Allocate handle and data buffer.
  */
#if defined(GC_RC) && !defined(RC_OPERATION_ONLY)
  mrbc_array *h = mrbc_alloc(vm, sizeof(mrbc_array));
#endif /* GC_RC and !RC_OPERATION_ONLY */
#ifdef GC_MS_OR_BM
  mrbc_array *h = mrbc_alloc(vm, sizeof(mrbc_array), BT_ARRAY);
  h->data = NULL;
  push_root_stack((mrbc_instance *) h);
#endif
  if( !h ) return value;	// ENOMEM

#if defined(GC_RC) && !defined(RC_OPERATION_ONLY)
  mrbc_value *data = mrbc_alloc(vm, sizeof(mrbc_value) * size);
#endif /* GC_RC and !RC_OPERATION_ONLY */
#ifdef GC_MS_OR_BM
  mrbc_value *data = mrbc_alloc(vm, sizeof(mrbc_value) * size, BT_ARRAY_DATA);
  pop_root_stack();
#endif
  if( !data ) {			// ENOMEM
    mrbc_raw_free( h );
    return value;
  }

#ifdef GC_RC
  h->ref_count = 1;
  h->tt = MRBC_TT_ARRAY;
#endif /* GC_RC */
  h->data_size = size;
  h->n_stored = 0;
  h->data = data;

  value.array = h;
  return value;
}


//================================================================
/*! get array copy

  @param  ary		pointer to source value
  gc infomation:
   * duplicated in method
   * gc trigger
*/
mrbc_value mrbc_array_dup(struct VM *vm, mrbc_value *array)
{
  mrbc_value ret = mrbc_array_new(vm, array->array->n_stored);
  if( ret.array == NULL ) return mrbc_nil_value();		// ENOMEM
  memcpy(ret.array->data, array->array->data, sizeof(mrbc_value) * array->array->n_stored);
  ret.array->n_stored = array->array->n_stored;
#ifdef GC_RC
  int i;
  for (i = 0; i < ret.array->n_stored; i++) {
    mrbc_dup(ret.array->data + i);
  }
#endif /* GC_RC */
  return ret;
}

#ifdef GC_RC
//================================================================
/*! destructor

  @param  ary	pointer to target value
*/
void mrbc_array_delete(mrbc_value *ary)
{
  mrbc_array *h = ary->array;

  mrbc_value *p1 = h->data;
  const mrbc_value *p2 = p1 + h->n_stored;
  while( p1 < p2 ) {
    mrbc_dec_ref_counter(p1++);
  }

#ifndef RC_OPERATION_ONLY
  mrbc_raw_free(h->data);
  mrbc_raw_free(h);
#endif /* RC_OPERATION_ONLY */
}
#endif /* GC_RC */


//================================================================
/*! delete all data what equal argument value from array.
*!  destructive operation.
*!  decremented ref_count in method.
* @param array  pointer to target array
* @param value pointer to comparison target value
*/
void mrbc_array_delete_value(mrbc_value *array, mrbc_value *value) {
  mrbc_value *data = array->array->data;
  int n_stored = array->array->n_stored;
  int i, idx;
  for (i = idx = 0; i < n_stored; i++) {
    if (mrbc_compare(data + idx, value) == 0) {
#ifdef GC_RC
      mrbc_dec_ref_counter(data + idx);
#endif /* GC_RC */
      mrbc_array_remove(array, idx);
      continue;
    }
    idx++;
  }
}


//================================================================
/*! clear vm_id

  @param  ary	pointer to target value
*/
void mrbc_array_clear_vm_id(mrbc_value *ary)
{
  mrbc_array *h = ary->array;

  mrbc_set_vm_id( h, 0 );

  mrbc_value *p1 = h->data;
  const mrbc_value *p2 = p1 + h->n_stored;
  while( p1 < p2 ) {
    mrbc_clear_vm_id(p1++);
  }
}


//================================================================
/*! resize buffer

  @param  ary	pointer to target value
  @param  size	size
  @return	mrbc_error_code

gc infomation:
   * gc trigger
*/
int mrbc_array_resize(mrbc_value *ary, int size)
{
  mrbc_array *h = ary->array;
  mrbc_value *data2 = mrbc_realloc(h->data, sizeof(mrbc_value) * size);
  if( !data2 ) return E_NOMEMORY_ERROR;	// ENOMEM

  h->data = data2;
  h->data_size = size;

  return 0;
}


//================================================================
/*! setter

  @param  ary		pointer to target value
  @param  idx		index
  @param  set_val	set value
  @return		mrbc_error_code

gc infomation:
   * gc trigger
*/
int mrbc_array_set(mrbc_value *ary, int idx, mrbc_value *set_val)
{
  mrbc_array *h = ary->array;

  if( idx < 0 ) {
    idx = h->n_stored + idx;
    if( idx < 0 ) return E_INDEX_ERROR;		// raise?
  }

  // need resize?
  if( idx >= h->data_size && mrbc_array_resize(ary, idx + 1) != 0 ) {
    return E_NOMEMORY_ERROR;			// ENOMEM
  }

  if( idx < h->n_stored ) {
    // release existing data.
#ifdef GC_RC
    mrbc_dec_ref_counter( &h->data[idx] );
#endif /* GC_RC */
  } else {
    // clear empty cells.
    int i;
    for( i = h->n_stored; i < idx; i++ ) {
      h->data[i] = mrbc_nil_value();
    }
    h->n_stored = idx + 1;
  }

  h->data[idx] = *set_val;

  return 0;
}


//================================================================
/*! getter

  @param  ary		pointer to target value
  @param  idx		index
  @return		mrbc_value data at index position or Nil.
*/
mrbc_value mrbc_array_get(mrbc_value *ary, int idx)
{
  mrbc_array *h = ary->array;

  if( idx < 0 ) idx = h->n_stored + idx;
  if( idx < 0 || idx >= h->n_stored ) return mrbc_nil_value();

  return h->data[idx];
}

//================================================================
/*! get many data what subset of array
  @param  array pointer to source array
  @param  start index of start
  @param  end   index of end
  @return       mrbc_array in mrbc_value or Nil

  gc infomation:
   * gc trigger
*/
mrbc_value mrbc_array_get_range(struct VM *vm, mrbc_value *array, int start, int end)
{
  mrbc_value ret;
  mrbc_array *dist, *src;
  int size;
  int len = mrbc_array_size(array);
  if (start < 0) start += len;
  if (end < 0) end += len;
  size = end - start + 1;
  if (start < 0 || start > len || end < 0 || end > len) return mrbc_nil_value();
  if (size < 0) return mrbc_array_new(vm, 0);
  ret = mrbc_array_new(vm, size);
  if (ret.array == NULL || ret.array->data == NULL) return mrbc_nil_value();
  dist = ret.array;
  src = array->array;
  if (size > src->n_stored) {
    size = src->n_stored;
  }
  memcpy(dist->data, src->data + start, sizeof(mrbc_value) * size);
  dist->n_stored = size;
  return ret;

}

//================================================================
/*! push a data to tail

  @param  ary		pointer to target value
  @param  set_val	set value
  @return		mrbc_error_code

  gc trigger
*/
int mrbc_array_push(mrbc_value *ary, mrbc_value *set_val)
{
  mrbc_array *h = ary->array;

  if( h->n_stored >= h->data_size ) {
    int size = h->data_size + 6;
    if( mrbc_array_resize(ary, size) != 0 )
      return E_NOMEMORY_ERROR;		// ENOMEM
  }

  h->data[h->n_stored++] = *set_val;

  return 0;
}


//================================================================
/*! pop a data from tail.

  @param  ary		pointer to target value
  @return		tail data or Nil
*/
mrbc_value mrbc_array_pop(mrbc_value *ary)
{
  mrbc_array *h = ary->array;

  if( h->n_stored <= 0 ) return mrbc_nil_value();
  return h->data[--h->n_stored];
}


//================================================================
/*! insert a data to the first.

  @param  ary		pointer to target value
  @param  set_val	set value
  @return		mrbc_error_code
  gc trigger
*/
int mrbc_array_unshift(mrbc_value *ary, mrbc_value *set_val)
{
  return mrbc_array_insert(ary, 0, set_val);
}


//================================================================
/*! removes the first data and returns it.

  @param  ary		pointer to target value
  @return		first data or Nil
*/
mrbc_value mrbc_array_shift(mrbc_value *ary)
{
  mrbc_array *h = ary->array;

  if( h->n_stored <= 0 ) return mrbc_nil_value();

  mrbc_value ret = h->data[0];
  memmove(h->data, h->data+1, sizeof(mrbc_value) * --h->n_stored);

  return ret;
}


//================================================================
/*! insert a data

  @param  ary		pointer to target value
  @param  idx		index
  @param  set_val	set value
  @return		mrbc_error_code

  gc trigger
*/
int mrbc_array_insert(mrbc_value *ary, int idx, mrbc_value *set_val)
{
  mrbc_array *h = ary->array;

  if( idx < 0 ) {
    idx = h->n_stored + idx + 1;
    if( idx < 0 ) return E_INDEX_ERROR;		// raise?
  }

  // need resize?
  int size = 0;
  if( idx >= h->data_size ) {
    size = idx + 1;
  } else if( h->n_stored >= h->data_size ) {
    size = h->data_size + 1;
  }
  if( size && mrbc_array_resize(ary, size) != 0 ) {
    return E_NOMEMORY_ERROR;			// ENOMEM
  }

  // move datas.
  if( idx < h->n_stored ) {
    memmove(h->data + idx + 1, h->data + idx,
	    sizeof(mrbc_value) * (h->n_stored - idx));
  }

  // set data
  h->data[idx] = *set_val;
  h->n_stored++;

  // clear empty cells if need.
  if( idx >= h->n_stored ) {
    int i;
    for( i = h->n_stored-1; i < idx; i++ ) {
      h->data[i] = mrbc_nil_value();
    }
    h->n_stored = idx + 1;
  }

  return 0;
}


//================================================================
/*! remove a data

  @param  ary		pointer to target value
  @param  idx		index
  @return		mrbc_value data at index position or Nil.
*/
mrbc_value mrbc_array_remove(mrbc_value *ary, int idx)
{
  mrbc_array *h = ary->array;

  if( idx < 0 ) idx = h->n_stored + idx;
  if( idx < 0 || idx >= h->n_stored ) return mrbc_nil_value();

  mrbc_value val = h->data[idx];
  h->n_stored--;
  if( idx < h->n_stored ) {
    memmove(h->data + idx, h->data + idx + 1,
	    sizeof(mrbc_value) * (h->n_stored - idx));
  }

  return val;
}


//================================================================
/*! clear all

  @param  ary		pointer to target value
*/
void mrbc_array_clear(mrbc_value *ary)
{
  mrbc_array *h = ary->array;

#ifdef GC_RC
  mrbc_value *p1 = h->data;
  const mrbc_value *p2 = p1 + h->n_stored;
  while( p1 < p2 ) {
    mrbc_dec_ref_counter(p1++);
  }
#endif /* GC_RC */

  h->n_stored = 0;
}


//================================================================
/*! compare

  @param  v1	Pointer to mrbc_value
  @param  v2	Pointer to another mrbc_value
  @retval 0	v1 == v2
  @retval plus	v1 >  v2
  @retval minus	v1 <  v2
*/
int mrbc_array_compare(const mrbc_value *v1, const mrbc_value *v2)
{
  int i;
  for( i = 0; ; i++ ) {
    if( i >= mrbc_array_size(v1) || i >= mrbc_array_size(v2) ) {
      return mrbc_array_size(v1) - mrbc_array_size(v2);
    }

    int res = mrbc_compare( &v1->array->data[i], &v2->array->data[i] );
    if( res != 0 ) return res;
  }
}


//================================================================
/*! get min, max value

  @param  ary		pointer to target value
  @param  pp_min_value	returns minimum mrbc_value
  @param  pp_max_value	returns maxmum mrbc_value
*/
void mrbc_array_minmax(mrbc_value *ary, mrbc_value **pp_min_value, mrbc_value **pp_max_value)
{
  mrbc_array *h = ary->array;

  if( h->n_stored == 0 ) {
    *pp_min_value = NULL;
    *pp_max_value = NULL;
    return;
  }

  mrbc_value *p_min_value = h->data;
  mrbc_value *p_max_value = h->data;

  int i;
  for( i = 1; i < h->n_stored; i++ ) {
    if( mrbc_compare( &h->data[i], p_min_value ) < 0 ) {
      p_min_value = &h->data[i];
    }
    if( mrbc_compare( &h->data[i], p_max_value ) > 0 ) {
      p_max_value = &h->data[i];
    }
  }

  *pp_min_value = p_min_value;
  *pp_max_value = p_max_value;
}


//================================================================
/*! get reversed array

  @param  ary		pointer to source value
  @return       reversed array in mrbc_value
  gc infomation:
   * duplicated in method
   * gc trigger
*/
mrbc_value mrbc_array_reverse (struct VM *vm, mrbc_value *array)
{
  mrbc_value ret = mrbc_array_new(vm, array->array->data_size);
  if (ret.array == NULL) return mrbc_nil_value(); // ENOMEM
  int i;
  mrbc_value *data = array->array->data;
  int n_stored = array->array->n_stored;
#ifdef GC_MS_OR_BM
  push_root_stack((mrbc_instance *) ret.array);
#endif /* GC_MS_OR_BM */
  for (i = 0; i < n_stored; i++) {
    mrbc_value val = data[n_stored - i - 1];
#ifdef GC_RC
    mrbc_dup(&val);
#endif /* GC_RC */
    mrbc_array_push(&ret, &val);
  }
#ifdef GC_MS_OR_BM
  pop_root_stack();
#endif /* GC_MS_OR_BM */
  return ret;
}


//================================================================
/*! method new
*/
static void c_array_new(struct VM *vm, mrbc_value v[], int argc)
{
  /*
    in case of new()
  */
  if( argc == 0 ) {
    mrbc_value ret = mrbc_array_new(vm, 0);
    if( ret.array == NULL ) return;		// ENOMEM

    SET_RETURN(ret);
    return;
  }

  /*
    in case of new(num)
  */
  if( argc == 1 && v[1].tt == MRBC_TT_FIXNUM && v[1].i >= 0 ) {
    mrbc_value ret = mrbc_array_new(vm, v[1].i);
    if( ret.array == NULL ) return;		// ENOMEM

    mrbc_value nil = mrbc_nil_value();
    if( v[1].i > 0 ) {
#ifdef GC_MS_OR_BM
      push_root_stack((mrbc_instance *)ret.array);
#endif /* GC_MS_OR_BM */
      mrbc_array_set(&ret, v[1].i - 1, &nil);
#ifdef GC_MS_OR_BM
      pop_root_stack();
#endif /* GC_MS_OR_BM */
    }
    SET_RETURN(ret);
    return;
  }

  /*
    in case of new(num, value)
  */
  if( argc == 2 && v[1].tt == MRBC_TT_FIXNUM && v[1].i >= 0 ) {
    mrbc_value ret = mrbc_array_new(vm, v[1].i);
    if( ret.array == NULL ) return;		// ENOMEM

    int i;
#ifdef GC_MS_OR_BM
    push_root_stack((mrbc_instance *)ret.array);
#endif /* GC_MS_OR_BM */
    for( i = 0; i < v[1].i; i++ ) {
#ifdef GC_RC
      mrbc_dup(&v[2]);
#endif /* GC_RC */
      mrbc_array_set(&ret, i, &v[2]);
    }
#ifdef GC_MS_OR_BM
    pop_root_stack();
#endif /* GC_MS_OR_BM */
    SET_RETURN(ret);
    return;
  }

  /*
    other case
  */
  console_print( "ArgumentError\n" );	// raise?
}


//================================================================
/*! (operator) +
*/
static void c_array_add(struct VM *vm, mrbc_value v[], int argc)
{
  if( GET_TT_ARG(1) != MRBC_TT_ARRAY ) {
    console_print( "TypeError\n" );	// raise?
    return;
  }

  mrbc_array *h1 = v[0].array;
  mrbc_array *h2 = v[1].array;

  mrbc_value value = mrbc_array_new(vm, h1->n_stored + h2->n_stored);
  if( value.array == NULL ) return;		// ENOMEM

  memcpy( value.array->data,                h1->data,
	  sizeof(mrbc_value) * h1->n_stored );
  memcpy( value.array->data + h1->n_stored, h2->data,
	  sizeof(mrbc_value) * h2->n_stored );
  value.array->n_stored = h1->n_stored + h2->n_stored;

#ifdef GC_RC
  mrbc_value *p1 = value.array->data;
  const mrbc_value *p2 = p1 + value.array->n_stored;
  while( p1 < p2 ) {
    mrbc_dup(p1++);
  }

#endif /* GC_RC */
  mrbc_release(v+1);
  SET_RETURN(value);
}


//================================================================
/*! (operator) -
*/
static void c_array_sub(struct VM *vm, mrbc_value v[], int argc)
{
  if( GET_TT_ARG(1) != MRBC_TT_ARRAY ) {
    console_print( "TypeError\n" );	// raise?
    return;
  }

  mrbc_array *value = v[1].array;
  mrbc_value array = mrbc_array_dup(vm, v);
  if( array.tt == MRBC_TT_NIL ) return;		// ENOMEM

  int i;
  for (i = 0; i < value-> n_stored; i++) {
    mrbc_array_delete_value(&array, value->data + i);
  }

  mrbc_release(v+1);
  SET_RETURN(array);
}


//================================================================
/*! (operator) *
*/
static void c_array_mul(struct VM *vm, mrbc_value v[], int argc)
{
  if( GET_TT_ARG(1) != MRBC_TT_FIXNUM ) {
    console_print( "TypeError\n" );	// raise?
    return;
  }

  mrbc_array *h1 = v[0].array;
  int n = v[1].i;

  if (n < 0) {
    SET_NIL_RETURN();
    return;
  }
  mrbc_value value = mrbc_array_new(vm, h1->n_stored * n);
  if( value.array == NULL ) return;		// ENOMEM

  int i;
  for (i = 0; i < n; i++) {
    memcpy( value.array->data + h1->n_stored * i, h1->data, sizeof(mrbc_value) * h1->n_stored );
  }
  value.array->n_stored = h1->n_stored * n;

#ifdef GC_RC
  mrbc_value *p1 = value.array->data;
  const mrbc_value *p2 = p1 + value.array->n_stored;
  while( p1 < p2 ) {
    mrbc_dup(p1++);
  }
#endif /* GC_RC */
  mrbc_release(v+1);
  SET_RETURN(value);
}

//================================================================
/*! (operator) []
*/
static void c_array_get(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value ret;
  /*
    in case of self[nth] -> object | nil
  */
  if( argc == 1 && v[1].tt == MRBC_TT_FIXNUM ) {
    ret = mrbc_array_get(v, v[1].i);
#ifdef GC_RC
    mrbc_dup(&ret);
#endif /* GC_RC */
    SET_RETURN(ret);
    return;
  }

  /*
    in case of self[start, length] -> Array | nil
  */
  int start, end, size;
  if (argc == 2 && v[1].tt == MRBC_TT_FIXNUM && v[2].tt == MRBC_TT_FIXNUM) {
    start = v[1].i;
    size = v[2].i;
    end = start + size - 1;
    goto RETURN_ARRAY_RANGE;
  } else
  /*
    in case of self[range] -> Array | nil
  */
  if (argc == 1 && v[1].tt == MRBC_TT_RANGE) {
    mrbc_range *range = v[1].range;
    if (range->first.tt != MRBC_TT_FIXNUM || range->last.tt != MRBC_TT_FIXNUM) {
      console_print("Invalid range in Array#[].\n");
      goto RETURN_NIL;
    }
    start = range->first.i;
    end = range->last.i;
    size = end - start + 1;
    goto RETURN_ARRAY_RANGE;
  }

  /*
    other case
  */
  console_print( "Not support such case in Array#[].\n" );
  return;

RETURN_ARRAY_RANGE:
  ret = mrbc_array_get_range(vm, v, start, end);
  if (ret.tt == MRBC_TT_NIL) goto RETURN_NIL;
#ifdef GC_RC
  int i;
  for ( i = 0; i < size; i++) {
    mrbc_dup(ret.array->data + i);
  }
#endif /* GC_RC */
  SET_RETURN(ret);
  return;

 RETURN_NIL:
  SET_NIL_RETURN();
}


//================================================================
/*! (operator) []=
*/
static void c_array_set(struct VM *vm, mrbc_value v[], int argc)
{
  /*
    in case of self[nth] = val
  */
  if( argc == 2 && v[1].tt == MRBC_TT_FIXNUM ) {
    mrbc_array_set(v, v[1].i, &v[2]);	// raise? IndexError or ENOMEM
    v[2].tt = MRBC_TT_EMPTY;
    return;
  }

  /*
    in case of self[start, length] = val
  */
  if( argc == 3 && v[1].tt == MRBC_TT_FIXNUM && v[2].tt == MRBC_TT_FIXNUM ) {
    // TODO: not implement yet.
  }

  /*
    other case
  */
  console_print( "Not support such case in Array#[].\n" );
}


//================================================================
/*! (method) clear
*/
static void c_array_clear(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_array_clear(v);
}

//================================================================
/*! (method) include?
*/
static void c_array_include(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value *value = &GET_ARG(1);
  mrbc_value *data = v->array->data;
  int n = v->array->n_stored;
  int i;

  for( i = 0; i < n; i++ ) {
    if( mrbc_compare(&data[i], value) == 0 ) break;
  }

  mrbc_release(v+1);
  if( i < n ) {
    SET_BOOL_RETURN(1);
  } else {
    SET_BOOL_RETURN(0);
  }
}


//================================================================
/*! (method) delete_at
*/
static void c_array_delete_at(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value val = mrbc_array_remove(v, GET_INT_ARG(1));
  SET_RETURN(val);
}


//==============================================================
/*! (method) delete
* Deletes all items that equal to mrbc_value of array from array.
* Returns last deleted item, or nil when item isn't found from array.
*
* TODO:
*  Specification of delete method of array of Ruby, is able to take code block.
*/
static void c_array_delete(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value *value = &GET_ARG(1);
  mrbc_value *data = v->array->data;
  mrbc_value ret; // last deleted value
  ret.tt = MRBC_TT_EMPTY;
  int n = v->array->n_stored;
  int i,idx;

  for (i = idx = 0; i < n; i++) {
    if (mrbc_compare(data + idx, value) == 0) {
#ifdef GC_RC
      if (ret.tt != MRBC_TT_EMPTY)
        mrbc_dec_ref_counter(&ret);
#endif /* GC_RC*/
      ret = data[idx];
      mrbc_array_remove(v, idx);
      continue;
    }
    idx++;
  }
  mrbc_release(v+1);
  if (i == idx) {
    // v[0].tt = MRBC_TT_NIL;
    SET_NIL_RETURN();
  } else {
    // v[0] = ret;
    SET_RETURN(ret);
  }
}


//================================================================
/*! (method) empty?
*/
static void c_array_empty(struct VM *vm, mrbc_value v[], int argc)
{
  int n = mrbc_array_size(v);

  if( n ) {
    SET_FALSE_RETURN();
  } else {
    SET_TRUE_RETURN();
  }
}


//================================================================
/*! (method) size,length,count
*/
static void c_array_size(struct VM *vm, mrbc_value v[], int argc)
{
  int n = mrbc_array_size(v);

  SET_INT_RETURN(n);
}


//================================================================
/*! (method) index
*/
static void c_array_index(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value *value = &GET_ARG(1);
  mrbc_value *data = v->array->data;
  int n = v->array->n_stored;
  int i;

  for( i = 0; i < n; i++ ) {
    if( mrbc_compare(&data[i], value) == 0 ) break;
  }

  if( i < n ) {
    SET_INT_RETURN(i);
  } else {
    SET_NIL_RETURN();
  }
}


//================================================================
/*! (method) first
*/
static void c_array_first(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value val = mrbc_array_get(v, 0);
#ifdef GC_RC
  mrbc_dup(&val);
#endif /* GC_RC */
  SET_RETURN(val);
}


//================================================================
/*! (method) last
*/
static void c_array_last(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value val = mrbc_array_get(v, -1);
#ifdef GC_RC
  mrbc_dup(&val);
#endif /* GC_RC */
  SET_RETURN(val);
}


//================================================================
/*! (method) push
*/
static void c_array_push(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_array_push(&v[0], &v[1]);	// raise? ENOMEM
  v[1].tt = MRBC_TT_EMPTY;
}


//================================================================
/*! (method) pop
*/
static void c_array_pop(struct VM *vm, mrbc_value v[], int argc)
{
  /*
    in case of pop() -> object | nil
  */
  if( argc == 0 ) {
    mrbc_value val = mrbc_array_pop(v);
    SET_RETURN(val);
    return;
  }

  /*
    in case of pop(n) -> Array
  */
  if( argc == 1 && v[1].tt == MRBC_TT_FIXNUM ) {
    // TODO: not implement yet.
  }

  /*
    other case
  */
  console_print( "Not support such case in Array#pop.\n" );
}


//================================================================
/*! (method) unshift
*/
static void c_array_unshift(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_array_unshift(&v[0], &v[1]);	// raise? IndexError or ENOMEM
  v[1].tt = MRBC_TT_EMPTY;
}


//================================================================
/*! (method) shift
*/
static void c_array_shift(struct VM *vm, mrbc_value v[], int argc)
{
  /*
    in case of pop() -> object | nil
  */
  if( argc == 0 ) {
    mrbc_value val = mrbc_array_shift(v);
    SET_RETURN(val);
    return;
  }

  /*
    in case of pop(n) -> Array
  */
  if( argc == 1 && v[1].tt == MRBC_TT_FIXNUM ) {
    // TODO: not implement yet.
  }

  /*
    other case
  */
  console_print( "Not support such case in Array#shift.\n" );
}


//================================================================
/*! (method) dup
*/
static void c_array_dup(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value value = mrbc_array_dup(vm, v);
  SET_RETURN(value);
}



//================================================================
/*! (method) min
*/
static void c_array_min(struct VM *vm, mrbc_value v[], int argc)
{
  // Subset of Array#min, not support min(n).

  mrbc_value *p_min_value, *p_max_value;

  mrbc_array_minmax(&v[0], &p_min_value, &p_max_value);
  if( p_min_value == NULL ) {
    SET_NIL_RETURN();
    return;
  }

#ifdef GC_RC
  mrbc_dup(p_min_value);
#endif /* GC_RC */
  SET_RETURN(*p_min_value);
}


//================================================================
/*! (method) max
*/
static void c_array_max(struct VM *vm, mrbc_value v[], int argc)
{
  // Subset of Array#max, not support max(n).

  mrbc_value *p_min_value, *p_max_value;

  mrbc_array_minmax(&v[0], &p_min_value, &p_max_value);
  if( p_max_value == NULL ) {
    SET_NIL_RETURN();
    return;
  }

#ifdef GC_RC
  mrbc_dup(p_max_value);
#endif /* GC_RC */
  SET_RETURN(*p_max_value);
}


//================================================================
/*! (method) minmax
*/
static void c_array_minmax(struct VM *vm, mrbc_value v[], int argc)
{
  // Subset of Array#minmax, not support minmax(n).

  mrbc_value *p_min_value, *p_max_value;
  mrbc_value nil = mrbc_nil_value();
  mrbc_value ret = mrbc_array_new(vm, 2);

  mrbc_array_minmax(&v[0], &p_min_value, &p_max_value);
  if( p_min_value == NULL ) p_min_value = &nil;
  if( p_max_value == NULL ) p_max_value = &nil;

#ifdef GC_RC
  mrbc_dup(p_min_value);
  mrbc_dup(p_max_value);
#endif /* GC_RC */
#ifdef GC_MS_OR_BM
  push_root_stack((mrbc_instance *)ret.array);
#endif /* GC_MS_OR_BM */
  mrbc_array_set(&ret, 0, p_min_value);
  mrbc_array_set(&ret, 1, p_max_value);
#ifdef GC_MS_OR_BM
  pop_root_stack();
#endif /* GC_MS_OR_BM */

  SET_RETURN(ret);
}


//================================================================
/*! (method) replace
*/
static void c_array_replace(struct VM *vm, mrbc_value v[], int argc)
{
#ifdef GC_RC
  int i;
  for (i = 0; i < v->array->n_stored; i++) {
    mrbc_dec_ref_counter(v->array->data + i);
  }
#endif /* GC_RC */
  mrbc_raw_free(v->array->data);
  mrbc_value src = mrbc_array_dup(vm, v + 1);
  if (src.tt == MRBC_TT_NIL) return;
  v->array->data = src.array->data;
  v->array->data_size = src.array->data_size;
  v->array->n_stored = src.array->n_stored;
  mrbc_raw_free(src.array);
  mrbc_release(v+1);
}


//================================================================
/*! (method) reverse
*/
static void c_array_reverse(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value ret = mrbc_array_reverse(vm, v);
  SET_RETURN(ret);
}

//================================================================
/*! (method) reverse!
*/
static void c_array_reverse_bang(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value ret = mrbc_array_reverse(vm, v);
#ifdef GC_RC
  mrbc_array *ary = v[0].array;
  mrbc_value *p1 = ary->data;
  mrbc_value *p2 = p1 + ary->n_stored;
  while (p1 < p2) {
    mrbc_dec_ref_counter(p1++);
  }
#endif
  mrbc_raw_free(v[0].array->data);
  v[0].array->data = ret.array->data;
  mrbc_raw_free(ret.array);
}


static uint16_t partition(mrbc_value *data, int start, int end, int (*compare) (const mrbc_value *v1, const mrbc_value *v2)) {
  mrbc_value tmp;
  int i, j;
  for (i = start - 1, j = start; j < end; j++) {
    if (compare(data + j, data + end) < 0) {
      i++;
      tmp = data[j];
      data[j] = data[i];
      data[i] = tmp;
    }
  }
  tmp = data[end];
  data[end] = data[i + 1];
  data[i + 1] = tmp;
  return i + 1;
}


static void quicksort(mrbc_value *data, int start, int end, int (*compare) (const mrbc_value *v1, const mrbc_value *v2)) {
  if (start < end) {
    uint16_t q = partition(data, start, end, compare);
    quicksort(data, start, q - 1, compare);
    quicksort(data, q + 1, end, compare);
  }
}

//================================================================
/* (method) sort
* Returns a new array created by sorting +self+.
* Default comparison method is #mrbc_compare.
* 
* TODO: Code block of comparisons is not implemented.
*/
static void c_array_sort(struct VM *vm, mrbc_value v[], int argc) {
  mrbc_value ary = mrbc_array_dup(vm, v);
  if (ary.tt == MRBC_TT_NIL) return;
  quicksort(ary.array->data, 0, ary.array->n_stored - 1, mrbc_compare);
  SET_RETURN(ary);
}


//================================================================
/* (method) sort!
* Destructive method
*/
static void c_array_sort_bang(struct VM *vm, mrbc_value v[], int argc) {
  quicksort(v->array->data, 0, v->array->n_stored - 1, mrbc_compare);
}


#if MRBC_USE_STRING
//================================================================
/*! (method) inspect
*/
static void c_array_inspect(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value ret = mrbc_string_new_cstr(vm, "[");
  if( !ret.string ) goto RETURN_NIL;		// ENOMEM

#ifdef GC_MS_OR_BM
  push_root_stack((mrbc_instance *)ret.string);
#endif /* GC_MS_OR_BM */
  int i;
  for( i = 0; i < mrbc_array_size(v); i++ ) {
    if( i != 0 ) mrbc_string_append_cstr( &ret, ", " );

    mrbc_value v1 = mrbc_array_get(v, i);
    mrbc_value s1 = mrbc_send( vm, v, argc, &v1, "inspect", 0 );
#ifdef GC_MS_OR_BM
    int f = push_mrbc_value_for_root_stack(&s1);
#endif /* GC_MS_OR_BM */
    mrbc_string_append( &ret, &s1 );
#ifdef GC_MS_OR_BM
    if (f) pop_root_stack();
#endif /* GC_MS_OR_BM */
#ifdef GC_RC
    mrbc_string_delete( &s1 );
#endif /* GC_RC */
  }

  mrbc_string_append_cstr( &ret, "]" );
#ifdef GC_MS_OR_BM
  pop_root_stack();
#endif /* GC_MS_OR_BM */
  SET_RETURN(ret);
  return;

 RETURN_NIL:
  SET_NIL_RETURN();
}


//================================================================
/*! (method) join
*/
static void c_array_join_1(struct VM *vm, mrbc_value v[], int argc,
			   mrbc_value *src, mrbc_value *ret, mrbc_value *separator)
{
  if( mrbc_array_size(src) == 0 ) return;

  int i = 0;
  int flag_error = 0;
  while( !flag_error ) {
    if( src->array->data[i].tt == MRBC_TT_ARRAY ) {
      c_array_join_1(vm, v, argc, &src->array->data[i], ret, separator);
    } else {
      mrbc_value v1 = mrbc_send( vm, v, argc, &src->array->data[i], "to_s", 0 );
#ifdef GC_MS_OR_BM
      int f = push_mrbc_value_for_root_stack(&v1);
#endif /* GC_MS_OR_BM */
      flag_error |= mrbc_string_append( ret, &v1 );
#ifdef GC_MS_OR_BM
      if (f) pop_root_stack();
#endif /* GC_MS_OR_BM */
#ifdef GC_RC
      mrbc_dec_ref_counter(&v1);
#endif /* GC_RC */
    }
    if( ++i >= mrbc_array_size(src) ) break;	// normal return.
    flag_error |= mrbc_string_append( ret, separator );
  }
}

static void c_array_join(struct VM *vm, mrbc_value v[], int argc)
{
  mrbc_value ret = mrbc_string_new(vm, NULL, 0);
  if( !ret.string ) goto RETURN_NIL;		// ENOMEM

#ifdef GC_MS_OR_BM
  push_root_stack((mrbc_instance *)ret.string);
#endif /* GC_MS_OR_BM */
  mrbc_value separator = (argc == 0) ? mrbc_string_new_cstr(vm, "") :
    mrbc_send( vm, v, argc, &v[1], "to_s", 0 );

#ifdef GC_MS_OR_BM
  int f = push_mrbc_value_for_root_stack(&separator);
#endif /* GC_MS_OR_BM */

  c_array_join_1(vm, v, argc, &v[0], &ret, &separator );
#ifdef GC_RC
  mrbc_dec_ref_counter(&separator);
#endif /* GC_RC */
#ifdef GC_MS_OR_BM
  if (f) pop_root_stack();
  pop_root_stack();
#endif /* GC_MS_OR_BM */
  SET_RETURN(ret);
  return;

 RETURN_NIL:
  SET_NIL_RETURN();
}

#endif



//================================================================
/*! initialize
*/
void mrbc_init_class_array(struct VM *vm)
{
  mrbc_class_array = mrbc_define_class(vm, "Array", mrbc_class_object);

  mrbc_define_method(vm, mrbc_class_array, "new", c_array_new);
  mrbc_define_method(vm, mrbc_class_array, "+", c_array_add);
  mrbc_define_method(vm, mrbc_class_array, "-", c_array_sub);
  mrbc_define_method(vm, mrbc_class_array, "*", c_array_mul);
  mrbc_define_method(vm, mrbc_class_array, "[]", c_array_get);
  mrbc_define_method(vm, mrbc_class_array, "at", c_array_get);
  mrbc_define_method(vm, mrbc_class_array, "[]=", c_array_set);
  mrbc_define_method(vm, mrbc_class_array, "<<", c_array_push);
  mrbc_define_method(vm, mrbc_class_array, "clear", c_array_clear);
  mrbc_define_method(vm, mrbc_class_array, "include?", c_array_include);
  mrbc_define_method(vm, mrbc_class_array, "delete", c_array_delete);
  mrbc_define_method(vm, mrbc_class_array, "delete_at", c_array_delete_at);
  mrbc_define_method(vm, mrbc_class_array, "empty?", c_array_empty);
  mrbc_define_method(vm, mrbc_class_array, "size", c_array_size);
  mrbc_define_method(vm, mrbc_class_array, "length", c_array_size);
  mrbc_define_method(vm, mrbc_class_array, "count", c_array_size);
  mrbc_define_method(vm, mrbc_class_array, "index", c_array_index);
  mrbc_define_method(vm, mrbc_class_array, "first", c_array_first);
  mrbc_define_method(vm, mrbc_class_array, "last", c_array_last);
  mrbc_define_method(vm, mrbc_class_array, "push", c_array_push);
  mrbc_define_method(vm, mrbc_class_array, "pop", c_array_pop);
  mrbc_define_method(vm, mrbc_class_array, "shift", c_array_shift);
  mrbc_define_method(vm, mrbc_class_array, "unshift", c_array_unshift);
  mrbc_define_method(vm, mrbc_class_array, "dup", c_array_dup);
  mrbc_define_method(vm, mrbc_class_array, "min", c_array_min);
  mrbc_define_method(vm, mrbc_class_array, "max", c_array_max);
  mrbc_define_method(vm, mrbc_class_array, "minmax", c_array_minmax);
  mrbc_define_method(vm, mrbc_class_array, "replace", c_array_replace);
  mrbc_define_method(vm, mrbc_class_array, "reverse", c_array_reverse);
  mrbc_define_method(vm, mrbc_class_array, "reverse!", c_array_reverse_bang);
  mrbc_define_method(vm, mrbc_class_array, "sort", c_array_sort);
  mrbc_define_method(vm, mrbc_class_array, "sort!", c_array_sort_bang);
#if MRBC_USE_STRING
  mrbc_define_method(vm, mrbc_class_array, "inspect", c_array_inspect);
  mrbc_define_method(vm, mrbc_class_array, "to_s", c_array_inspect);
  mrbc_define_method(vm, mrbc_class_array, "join", c_array_join);
#endif
}
