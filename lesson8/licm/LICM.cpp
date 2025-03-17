#include "llvm/IR/Module.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct SkeletonPass : public PassInfoMixin<SkeletonPass> {
  // This run method is invoked on each Module.
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
    for (auto &F : M) {
      errs() << "I saw a function called " << F.getName() << "!\n";
    }
    return PreservedAnalyses::all();
  }
};

} // end anonymous namespace

extern "C" LLVM_ATTRIBUTE_WEAK PassPluginLibraryInfo llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "SkeletonPass", "v0.1",
    [](PassBuilder &PB) {
      // Register a callback that allows our pass to be invoked with:
      //   -passes="skeleton-pass"
      PB.registerPipelineParsingCallback(
        [](StringRef Name, ModulePassManager &MPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "skeleton-pass") {
            MPM.addPass(SkeletonPass());
            return true;
          }
          return false;
        });
    }
  };
}