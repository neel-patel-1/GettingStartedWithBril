#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"

#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/IR/Dominators.h"           // For DominatorTree
#include "llvm/Transforms/Utils/LoopUtils.h" // For InsertPreheaderForLoop
#include "llvm/Analysis/ValueTracking.h"   // For isSafeToSpeculativelyExecute
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct LICMInvariantModulePass : public PassInfoMixin<LICMInvariantModulePass> {

  // Recursively process a loop.
  bool processLoop(Loop *L, DominatorTree &DT, LoopInfo &LI) {
    bool modified = false;
    errs() << "Processing loop: " << *L << "\n";

    // Process subloops first.
    for (Loop *SubLoop : L->getSubLoops())
      modified |= processLoop(SubLoop, DT, LI);

    // Ensure the loop has a preheader; if not, create one.
    BasicBlock *Preheader = L->getLoopPreheader();
    if (!Preheader) {
      errs() << "Loop does not have a preheader: " << *L << "\n";
      // Pass a nullptr for MemorySSAUpdater.
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
        // Skip PHI nodes and terminators.
        if (isa<PHINode>(Inst) || Inst->isTerminator())
          continue;
        // Use the free function to check if it's safe to speculatively execute.
        if (!isSafeToSpeculativelyExecute(Inst))
          continue;
        // If the instruction is loop invariant and not already in the preheader, hoist it.
        if (L->isLoopInvariant(Inst)) {
          Inst->moveBefore(Preheader->getTerminator());
          errs() << "Hoisted invariant instruction: " << *Inst << "\n";
          modified = true;
        } else {
          errs() << "Instruction is not loop invariant: " << *Inst << "\n";
        }
      }
    }
    return modified;
  }

  // Process every function in the module.
  bool processFunction(Function &F, LoopInfo &LI, DominatorTree &DT) {
    bool modified = false;
    errs() << "Processing function: " << F.getName() << "\n";
    for (Loop *L : LI)
      modified |= processLoop(L, DT, LI);
    return modified;
  }

  // Main entry point for the module pass.
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &MAM) {
    bool Modified = false;
    // Obtain a FunctionAnalysisManager for functions in the module.
    auto &FAM = MAM.getResult<FunctionAnalysisManagerModuleProxy>(M).getManager();

    errs() << "Processing module: " << M.getName() << "\n";

    for (Function &F : M) {
      if (F.isDeclaration())
        continue;
      // Retrieve analyses needed for function F.
      auto &LI = FAM.getResult<LoopAnalysis>(F);
      auto &DT = FAM.getResult<DominatorTreeAnalysis>(F);
      Modified |= processFunction(F, LI, DT);
    }
    return (Modified ? PreservedAnalyses::none() : PreservedAnalyses::all());
  }
};

} // end anonymous namespace

// Register the pass so it can be invoked via "-passes=licm-invariant".
extern "C" LLVM_ATTRIBUTE_WEAK llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "LICMInvariantModulePass", "v0.1",
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, llvm::ModulePassManager &MPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "licm-invariant") {
            MPM.addPass(LICMInvariantModulePass());
            return true;
          }
          return false;
        });
    }
  };
}
