/*! @file
  @brief
  Declare static data.

  <pre>
  Copyright (C) 2015-2016 Kyushu Institute of Technology.
  Copyright (C) 2015-2016 Shimane IT Open-Innovation Center.

  This file is distributed under BSD 3-Clause License.
  </pre>
*/

#include "vm_config.h"
#include "static.h"
#include "global.h"
#include "class.h"
#ifdef GC_MS_OR_BM
#include "alloc.h"
#include <stdio.h>
#endif /* GC_MS_OR_BM */

/* Class Tree */
mrbc_class *mrbc_class_object;

/* Proc */
mrbc_class *mrbc_class_proc;

/* Classes */
mrbc_class *mrbc_class_false;
mrbc_class *mrbc_class_true;
mrbc_class *mrbc_class_nil;
mrbc_class *mrbc_class_array;
mrbc_class *mrbc_class_fixnum;
mrbc_class *mrbc_class_symbol;
mrbc_class *mrbc_class_float;
mrbc_class *mrbc_class_math;
mrbc_class *mrbc_class_string;
mrbc_class *mrbc_class_range;
mrbc_class *mrbc_class_hash;

void init_static(void)
{
  mrbc_init_global();

  mrbc_init_class();

#ifdef GC_MS_OR_BM
  push_root_stack((mrbc_instance *)mrbc_class_object);
  push_root_stack((mrbc_instance *)mrbc_class_proc);
  push_root_stack((mrbc_instance *)mrbc_class_false);
  push_root_stack((mrbc_instance *)mrbc_class_true);
  push_root_stack((mrbc_instance *)mrbc_class_nil);
  push_root_stack((mrbc_instance *)mrbc_class_array);
  push_root_stack((mrbc_instance *)mrbc_class_fixnum);
  push_root_stack((mrbc_instance *)mrbc_class_symbol);
  push_root_stack((mrbc_instance *)mrbc_class_float);
  push_root_stack((mrbc_instance *)mrbc_class_math);
  push_root_stack((mrbc_instance *)mrbc_class_string);
  push_root_stack((mrbc_instance *)mrbc_class_range);
  push_root_stack((mrbc_instance *)mrbc_class_hash);
#endif /* GC_MS_OR_BM */
}