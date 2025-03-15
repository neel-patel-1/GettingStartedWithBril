#include "llvm/IR/PassManager.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/ScalarEvolution.h"
#include "llvm/Analysis/ScalarEvolutionExpressions.h"
#include "llvm/Transforms/Utils/LoopUtils.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct LICMInductionElimPass : public PassInfoMixin<LICMInductionElimPass> {
  bool processLoop(Loop *L, ScalarEvolution &SE) {
    errs() <<"Processing loop: " << *L << "\n";
    bool modified = false;
    for (Loop *SubLoop : L->getSubLoops())
      modified |= processLoop(SubLoop, SE);

    BasicBlock *Preheader = L->getLoopPreheader();
    if (!Preheader)
      return modified;

    for (BasicBlock *BB : L->getBlocks()) {
      for (auto It = BB->begin(), End = BB->end(); It != End; ) {
        Instruction *Inst = &*It++;
        if (L->isLoopInvariant(Inst))
          continue;

        // Obtain the Scalar Evolution expression for the instruction.
        const SCEV *S = SE.getSCEV(Inst);
        if (isa<SCEVCouldNotCompute>(S))
          continue;


        if (auto *ar = dyn_cast<SCEVAddRecExpr>(S)) {
            // A + B*x where A
            /// and B are loop invariant values
          if (ar->isAffine()) {
            Inst->moveBefore(Preheader->getTerminator());
            errs() << "Hoisted instruction: " << *Inst << "\n";
            modified = true;
          }
        }
      }
    }
    return modified;
  }

  // Main entry point for the pass.
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
    auto &LI = FAM.getResult<LoopAnalysis>(F);
    auto &SE = FAM.getResult<ScalarEvolutionAnalysis>(F);
    bool modified = false;
    errs() << "Running LICMInductionElimPass on function: " << F.getName() << "\n";
    // Process all top-level loops in the function.
    for (Loop *L : LI){
        // Process each loop and its subloops.
        errs() << "Processing top-level loop: " << *L << "\n";
      modified |= processLoop(L, SE);
    }

    // We have modified the IR if we hoisted any instructions.
    return (modified ? PreservedAnalyses::none() : PreservedAnalyses::all());
  }
};
} // end anonymous namespace

// Pass registration for the new pass manager.
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "LICMInductionElimPass", "v0.1",
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, FunctionPassManager &FPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "licm-indvar-elim") {
            FPM.addPass(LICMInductionElimPass());
            return true;
          }
          return false;
        });
    }
  };
}