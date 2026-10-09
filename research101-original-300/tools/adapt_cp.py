"""Apply a disclosed I/O and signed-profit big-M adaptation to the CP 2024 code.

The original algorithm/proof logger remains in the upstream pinned supplement.
"""
import difflib,hashlib,json,pathlib,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'Dependency-setup.json').read_text());original=pathlib.Path(meta['sources']['cp2024']['folder'])/'knapsack/knapsack.cc'
text=original.read_text();start=text.index('    if (argc != 4)');end=text.index('    {\n        ofstream opb',start)
replacement='''    if (argc != 2) return EXIT_FAILURE;
    std::ifstream input{argv[1]};
    int n = 0, max_weight = 0;
    input >> n >> max_weight;
    if (!input || n < 1 || n > 16 || max_weight < 0) return EXIT_FAILURE;
    vector<int> weights, profits;
    for (int i = 0; i < n; ++i) {
        int w = 0, p = 0;
        input >> w >> p;
        if (!input || w <= 0 || std::abs(p) > 1000000) return EXIT_FAILURE;
        weights.push_back(w); profits.push_back(p);
    }

'''
adapted=text[:start]+replacement+text[end:]
adapted=adapted.replace('big_number += p;', 'big_number += std::abs(p);')
adapted=adapted.replace('" -" << profits[p]', '" " << -profits[p]')
adapted=adapted.replace('" -" << profits.at(l)', '" " << -profits.at(l)')
adapted='#include <cstdlib>\n'+adapted
folder=ROOT/'external/cp2024';folder.mkdir(parents=True,exist_ok=True);target=folder/'adapted-knapsack.cc';target.write_text(adapted)
patch=''.join(difflib.unified_diff(text.splitlines(True),adapted.splitlines(True),fromfile='upstream/knapsack.cc',tofile='adapted-knapsack.cc'))
(ROOT/'CP2024-adaptation.patch').write_text(patch)
start=time.perf_counter();p=subprocess.run(['g++','-O2','-std=c++20','-o',str(folder/'knapsack'),str(target)],capture_output=True,text=True,timeout=60)
record=dict(upstream_commit=meta['sources']['cp2024']['commit'],upstream_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),adapted_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),exit_code=p.returncode,wall=time.perf_counter()-start,stderr=p.stderr,
 changes=['deterministic supplied item input instead of random generation','positive big-M uses sum of absolute profits for signed point objectives','signed objective coefficients are printed as integers, avoiding double minus','cstdlib header for integer abs'],algorithm_changes=False)
if p.returncode==0:record['binary_sha256']=hashlib.sha256((folder/'knapsack').read_bytes()).hexdigest()
(ROOT/'CP2024-build.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
