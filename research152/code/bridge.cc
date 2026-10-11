// Thin credited adapter to unmodified OR-Tools 9.14 GenericMinCostFlow.
// It retains residual flow/capacity state; upstream Solve resets potentials.
#include <algorithm>
#include <cstdint>
#include <memory>
#include <vector>
#include "ortools/graph/graph.h"
#include "ortools/graph/min_cost_flow.h"

using Graph = util::ReverseArcListGraph<>;
using Generic = operations_research::GenericMinCostFlow<Graph>;
using I = int64_t;

struct State {
  int n, e, updates=0, solves=0;
  Graph graph;
  std::unique_ptr<Generic> solver;
  Generic* original;
  std::vector<int> a,z;
  std::vector<I> l,u,c,b;
  State(int nodes,int edges,const int* tails,const int* heads)
      : n(nodes),e(edges),graph(nodes,edges),a(tails,tails+edges),z(heads,heads+edges),
        l(edges),u(edges),c(edges),b(nodes) {
    for(int i=0;i<e;i++) {
      if(a[i]<0||a[i]>=n||z[i]<0||z[i]>=n) throw 1;
      if(graph.AddArc(a[i],z[i])!=i) throw 2;
    }
    solver=std::make_unique<Generic>(&graph);original=solver.get();
    // Safe only after an independently checked feasible witness at each Solve.
    solver->SetCheckFeasibility(false);
  }
  bool stable() const {return solver.get()==original && solver->graph()==&graph;}
  bool patch(const I* lower,const I* upper,const I* costs,const I* supplies) {
    I sum=0;
    for(int v=0;v<n;v++){if(supplies[v]<-1000000||supplies[v]>1000000)return false;sum+=supplies[v];}
    if(sum)return false;
    for(int i=0;i<e;i++)if(lower[i]<0||upper[i]<lower[i]||upper[i]>10000||costs[i]<-1000000||costs[i]>1000000)return false;
    for(int i=0;i<e;i++) {
      l[i]=lower[i];u[i]=upper[i];c[i]=costs[i];
      solver->SetArcCapacity(i,u[i]-l[i]);solver->SetArcUnitCost(i,c[i]);
    }
    std::vector<I> excess(supplies,supplies+n);
    b.assign(supplies,supplies+n);
    for(int i=0;i<e;i++) {
      // x = new lower + retained transformed flow. Capacity setters may clamp y.
      I x=l[i]+solver->Flow(i);excess[a[i]]-=x;excess[z[i]]+=x;
    }
    for(int v=0;v<n;v++)solver->SetNodeSupply(v,excess[v]);
    updates++;return stable();
  }
  bool witness(const I* x) const {
    if(!x)return false;std::vector<I> balance(n,0);
    for(int i=0;i<e;i++){if(x[i]<l[i]||x[i]>u[i])return false;balance[a[i]]+=x[i];balance[z[i]]-=x[i];}
    return balance==b;
  }
};

extern "C" {
void* m152_create(int n,int e,const int* a,const int* z,const I* l,const I* u,const I* c,const I* b) {
  if(n<1||n>256||e<0||e>16384)return nullptr;
  try {auto s=std::make_unique<State>(n,e,a,z);if(!s->patch(l,u,c,b))return nullptr;return s.release();}
  catch(...){return nullptr;}
}
int m152_patch(void* h,const I* l,const I* u,const I* c,const I* b) {
  try{return static_cast<State*>(h)->patch(l,u,c,b)?0:-1;}catch(...){return -2;}
}
int m152_solve(void* h,const I* witness) {
  try {
    auto* s=static_cast<State*>(h);if(!s->stable()||!s->witness(witness))return -2;
    s->solves++;return s->solver->Solve()?0:static_cast<int>(s->solver->status())+1;
  }catch(...){return -3;}
}
int m152_snapshot(void* h,I* y,I* excess,int* counts) {
  auto* s=static_cast<State*>(h);if(!s->stable())return -1;
  for(int i=0;i<s->e;i++)y[i]=s->solver->Flow(i);
  for(int v=0;v<s->n;v++)excess[v]=s->solver->Supply(v);
  counts[0]=s->updates;counts[1]=s->solves;counts[2]=s->stable();return 0;
}
void m152_destroy(void* h){delete static_cast<State*>(h);}
int m152_simple(int n,int e,const int* a,const int* z,const I* l,const I* u,const I* c,const I* b,I* x) {
  try {
    operations_research::SimpleMinCostFlow solver;std::vector<I> supplies(b,b+n);
    for(int i=0;i<e;i++){solver.AddArcWithCapacityAndUnitCost(a[i],z[i],u[i]-l[i],c[i]);supplies[a[i]]-=l[i];supplies[z[i]]+=l[i];}
    for(int v=0;v<n;v++)solver.SetNodeSupply(v,supplies[v]);
    auto status=solver.Solve();
    if(status==operations_research::SimpleMinCostFlow::INFEASIBLE)return 1;
    if(status!=operations_research::SimpleMinCostFlow::OPTIMAL)return static_cast<int>(status)+2;
    for(int i=0;i<e;i++)x[i]=l[i]+solver.Flow(i);return 0;
  }catch(...){return -1;}
}
}
