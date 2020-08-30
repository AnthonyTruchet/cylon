/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "parallel_op.hpp"

cylon::Op *cylon::Op::GetChild(int tag) {
  return this->children.find(tag)->second;
}

void cylon::Op::DrainQueueToChild(int queue, int child, int tag) {
  auto q = GetQueue(queue);
  auto c = GetChild(child);
  while (!q->empty()) {
    c->InsertTable(tag, q->front());
    q->pop();
  }
}

std::queue<std::shared_ptr<cylon::Table>> *cylon::Op::GetQueue(int tag) {
  return this->queues.find(tag)->second;
}

cylon::Op::Op(std::shared_ptr<cylon::CylonContext> ctx,
              std::shared_ptr<arrow::Schema> schema,
              int id,
              std::shared_ptr<ResultsCallback> callback, bool root_op) : all_parents_finalized(root_op) {
  this->ctx_ = ctx;
  this->id = id;
  this->callback = callback;
  this->schema = schema;
}

void cylon::Op::InsertTable(int tag, std::shared_ptr<cylon::Table> table) {
  if (queues.find(tag) == queues.end()) {
    queues.insert(std::make_pair<>(tag, new std::queue<std::shared_ptr<cylon::Table>>()));
  }
  this->queues.find(tag)->second->push(table);
  this->inputs_count++;
}

void cylon::Op::Progress() {
  // first process this Op
  if (this->Ready()) {
    for (auto const &q:this->queues) {
      if (!q.second->empty()) {
        bool done = this->Execute(q.first, q.second->front());
        if (done) {
          q.second->pop();
          this->inputs_count--;
          // todo instead of keeping in this queue, partially processed tables can be added to a different queue
          // todo check whether this is the best way to do this. But always assume that the status of the
          // partially processed tables will be kept by the Op implementation
          // std::queue<std::pair<int, std::shared_ptr<cylon::Table>>> partially_processed_queue{};
        }
      }
    }
  }

  // if no more inputs and all parents have finalized, try to finalize this op
  // if finalizing this Op is successful report that to children
  if (!this->finalized && this->inputs_count == 0 && this->all_parents_finalized) {
    // try to finalize this Op
    if (this->Finalize()) {
      for (auto child: children) {
        child.second->ReportParentCompleted();
      }
      this->finalized = true;
    }
  }

  // always progress children(or child branches)
  for (auto child: children) {
    // progress only if child(entire child branch) is not competed
    if (!child.second->IsComplete()) {
      child.second->Progress();
    }
  }
}

bool cylon::Op::IsComplete() {
  for (auto child: children) {
    if (!child.second->IsComplete()) {
      return false;
    }
  }
  // no more inputs will be received && no more items left in the queues
  // this->all_parents_finalized && this->inputs_count == 0; , this has been already checked in Progress()
  // hence checking finalized is sufficient
  return this->finalized;
}

cylon::Op::~Op() {
  for (auto p: queues) {
    delete p.second;
  }
}

cylon::Op *cylon::Op::AddChild(cylon::Op *child) {
  this->children.insert(std::make_pair(child->id, child));
  child->IncrementParentsCount();
  return this;
}

bool cylon::Op::TerminalCheck(int tag, std::shared_ptr<cylon::Table> table) {
  if (this->children.empty()) {
    this->callback->OnResult(tag, table);
    return true;
  }
  return false;
}

void cylon::Op::InsertToAllChildren(int tag, std::shared_ptr<cylon::Table> table) {
  if (!this->TerminalCheck(tag, table)) {
    for (auto const &child:this->children) {
      child.second->InsertTable(tag, table);
    }
  }
}

void cylon::Op::InsertToChild(int tag, int child, std::shared_ptr<cylon::Table> table) {
  if (!this->TerminalCheck(tag, table)) {
    this->children.find(child)->second->InsertTable(tag, table);
  }
}

bool cylon::Op::Ready() {
  return !this->finalized && this->inputs_count > 0;
}

void cylon::Op::IncrementParentsCount() {
  this->parents++;
}

void cylon::Op::ReportParentCompleted() {
  this->finalized_parents++;
  if (this->finalized_parents >= parents) {
    this->all_parents_finalized = true;
    this->OnParentsFinalized();
  }
}