#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"

#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/ScalarEvolution.h"
#include "llvm/Analysis/ScalarEvolutionExpressions.h"
#include "llvm/IR/Dominators.h"           // New location for dominator tree
#include "llvm/Transforms/Utils/LoopUtils.h" // For InsertPreheaderForLoop
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct LICMInductionElimModulePass : public PassInfoMixin<LICMInductionElimModulePass> {

  // Recursively process a loop.
  bool processLoop(Loop *L, ScalarEvolution &SE, DominatorTree &DT, LoopInfo &LI) {
    bool modified = false;

    // Process subloops first.
    for (Loop *SubLoop : L->getSubLoops())
      modified |= processLoop(SubLoop, SE, DT, LI);

    // Ensure the loop has a preheader; if not, create one.
    BasicBlock *Preheader = L->getLoopPreheader();
    if (!Preheader) {
      // Note: Pass a nullptr for MemorySSAUpdater, then a bool.
      Preheader = InsertPreheaderForLoop(L, &DT, &LI, /*MSSAU=*/nullptr, /*PreserveLCSSA=*/false);
      if (!Preheader) {
        errs() << "Warning: Failed to insert preheader for loop: " << *L << "\n";
      } else {
        errs() << "Inserted preheader: " << Preheader->getName() << " for loop: " << *L << "\n";
        modified = true;
      }
    }

    // Iterate over each instruction in the loop.
    for (BasicBlock *BB : L->getBlocks()) {
      // Use a safe iterator since we might move instructions.
      for (auto It = BB->begin(), End = BB->end(); It != End; ) {
        Instruction *Inst = &*It++;
        if (L->isLoopInvariant(Inst))
          continue;

        const SCEV *S = SE.getSCEV(Inst);
        if (isa<SCEVCouldNotCompute>(S))
          continue;

        // If the SCEV is an affine add recurrence, hoist the instruction.
        if (auto *AR = dyn_cast<SCEVAddRecExpr>(S)) {
          if (AR->isAffine()) {
            Inst->moveBefore(Preheader->getTerminator());
            errs() << "Hoisted instruction: " << *Inst << "\n";
            modified = true;
          }
        }
      }
    }
    return modified;
  }

  // Process every function in the module.
  bool processFunction(Function &F, LoopInfo &LI, ScalarEvolution &SE, DominatorTree &DT) {
    bool modified = false;
    for (Loop *L : LI)
      modified |= processLoop(L, SE, DT, LI);
    return modified;
  }

  // Main entry point for the module pass.
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &MAM) {
    bool Modified = false;

    // Obtain a FunctionAnalysisManager for functions in the module.
    auto &FAM = MAM.getResult<FunctionAnalysisManagerModuleProxy>(M).getManager();

    for (Function &F : M) {
      if (F.isDeclaration())
        continue;
      // Retrieve analyses needed for function F.
      auto &LI = FAM.getResult<LoopAnalysis>(F);
      auto &SE = FAM.getResult<ScalarEvolutionAnalysis>(F);
      auto &DT = FAM.getResult<DominatorTreeAnalysis>(F);

      Modified |= processFunction(F, LI, SE, DT);
    }
    return (Modified ? PreservedAnalyses::none() : PreservedAnalyses::all());
  }
};

} // end anonymous namespace

// Register the pass so it can be invoked via "-passes=licm-indvar-elim".
extern "C" LLVM_ATTRIBUTE_WEAK llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "LICMInductionElimModulePass", "v0.2",
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, ModulePassManager &MPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "licm-indvar-elim") {
            MPM.addPass(LICMInductionElimModulePass());
            return true;
          }
          return false;
        });
    }
  };
}
