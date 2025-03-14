#include "llvm/IR/PassManager.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/GlobalVariable.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"

using namespace llvm;

#define MAX_ENTRIES 1024

namespace {
    struct InsertRDTSCPass : public PassInfoMixin<InsertRDTSCPass> {
        GlobalVariable *TimestampArray = nullptr;
        GlobalVariable *IndexVar = nullptr;
        Function *RDTSCFunction = nullptr;
        Function *HistogramFunction = nullptr;

        // Run pass on module
        PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
            LLVMContext &Context = M.getContext();
            IRBuilder<> Builder(Context);

            // Step 1: Create a global array for timestamps
            createGlobalTimestampArray(M, Context);

            // Step 2: Insert RDTSC every 5 IR instructions
            for (Function &F : M) {
                if (!F.isDeclaration()) {
                    insertRDTSCIntoFunction(F, M, Builder);
                }
            }

            // Step 3: Register histogram computation function at exit
            createHistogramFunction(M, Context);
            registerHistogramFunction(M, Context);

            return PreservedAnalyses::none();
        }

        void createGlobalTimestampArray(Module &M, LLVMContext &Context) {
            ArrayType *ArrayTy = ArrayType::get(Type::getInt64Ty(Context), MAX_ENTRIES);
            TimestampArray = new GlobalVariable(M, ArrayTy, false, GlobalValue::ExternalLinkage,
                                                Constant::getNullValue(ArrayTy), "timestamps");

            IndexVar = new GlobalVariable(M, Type::getInt32Ty(Context), false, GlobalValue::ExternalLinkage,
                                          ConstantInt::get(Type::getInt32Ty(Context), 0), "timestampIndex");
        }

        void insertRDTSCIntoFunction(Function &F, Module &M, IRBuilder<> &Builder) {
            int counter = 0;
            for (BasicBlock &BB : F) {
                for (auto it = BB.begin(); it != BB.end(); ++it) {
                    if (++counter % 5 == 0) { // Every 5 instructions
                        insertRDTSCCall(&*it, M, Builder);
                    }
                }
            }
        }

        void insertRDTSCCall(Instruction *I, Module &M, IRBuilder<> &Builder) {
            LLVMContext &Context = M.getContext();
            FunctionCallee RDTSC = getOrCreateRDTSCFunction(M);

            Builder.SetInsertPoint(I);
            Value *Timestamp = Builder.CreateCall(RDTSC);
            Value *Index = Builder.CreateLoad(Type::getInt32Ty(Context), IndexVar);

            // Store timestamp in global array
            Value *Ptr = Builder.CreateGEP(TimestampArray->getValueType(), TimestampArray, {Builder.getInt64(0), Index});
            Builder.CreateStore(Timestamp, Ptr);

            // Increment the index
            Value *NextIndex = Builder.CreateAdd(Index, Builder.getInt32(1));
            Builder.CreateStore(NextIndex, IndexVar);
        }

        FunctionCallee getOrCreateRDTSCFunction(Module &M) {
            if (!RDTSCFunction) {
                LLVMContext &Context = M.getContext();
                FunctionType *FT = FunctionType::get(Type::getInt64Ty(Context), {}, false);
                RDTSCFunction = Function::Create(FT, Function::ExternalLinkage, "rdtsc", M);
            }
            return RDTSCFunction;
        }

        void createHistogramFunction(Module &M, LLVMContext &Context) {
            FunctionType *FT = FunctionType::get(Type::getVoidTy(Context), {}, false);
            HistogramFunction = Function::Create(FT, Function::ExternalLinkage, "computeHistogram", M);
        }

        void registerHistogramFunction(Module &M, LLVMContext &Context) {
            // Get or create `llvm.global_dtors`
            GlobalVariable *GV = M.getGlobalVariable("llvm.global_dtors");
            if (!GV) {
                // Define struct type: { i32, void ()*, i8* }
                StructType *DtorType = StructType::get(
                    Type::getInt32Ty(Context),   // Priority (i32)
                    HistogramFunction->getType(), // Function pointer (void ()*)
                    PointerType::get(Type::getInt8Ty(Context), 0)  // Null (i8*)
                );

                // Create array of destructors with priority 65535
                Constant *DtorArray = ConstantArray::get(
                    ArrayType::get(DtorType, 1),
                    {ConstantStruct::get(DtorType,
                                         {ConstantInt::get(Type::getInt32Ty(Context), 65535),  // High priority
                                          HistogramFunction,  // Function to execute
                                          Constant::getNullValue(PointerType::get(Type::getInt8Ty(Context), 0))})}
                );

                GV = new GlobalVariable(
                    M, DtorArray->getType(), false, GlobalValue::AppendingLinkage, DtorArray, "llvm.global_dtors");
            } else {
                errs() << "Warning: llvm.global_dtors already exists.\n";
            }
        }

    };
}

// Pass registration
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {LLVM_PLUGIN_API_VERSION, "InsertRDTSCPass", LLVM_VERSION_STRING,
            [](PassBuilder &PB) {
                PB.registerPipelineParsingCallback(
                    [](StringRef Name, ModulePassManager &MPM,
                       ArrayRef<PassBuilder::PipelineElement>) {
                        if (Name == "insert-rdtsc") {
                            MPM.addPass(InsertRDTSCPass());
                            return true;
                        }
                        return false;
                    });
            }};
}
