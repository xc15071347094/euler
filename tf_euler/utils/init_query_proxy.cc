/* Copyright 2020 Alibaba Group Holding Limited. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#include "tf_euler/utils/euler_query_proxy.h"
#include "euler/common/str_util.h"

extern "C" {
  bool InitQueryProxy(const char* conf) {
    euler::GraphConfig config;
    auto vec = euler::Split(conf, ';');
    if (vec.empty()) {
      return false;
    }
    for (auto it = vec.begin(); it != vec.end(); ++it) {
      auto key_value = euler::Split(*it, '=');
      if (key_value.size() != 2 || key_value[0].empty() ||
          key_value[1].empty()) {
        return false;
      }
      config.Add(key_value[0], key_value[1]);
    }
    euler::QueryProxy::Init(config);
    return true;
  }
}
