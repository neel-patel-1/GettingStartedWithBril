"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
exports.__esModule = true;
exports.Heap = exports.Key = void 0;
var util_ts_1 = require("./bril-ts/util.ts");
/**
 * An interpreter error to print to the console.
 */
var BriliError = /** @class */ (function (_super) {
    __extends(BriliError, _super);
    function BriliError(message) {
        var _newTarget = this.constructor;
        var _this = _super.call(this, message) || this;
        Object.setPrototypeOf(_this, _newTarget.prototype);
        _this.name = BriliError.name;
        return _this;
    }
    return BriliError;
}(Error));
/**
 * Create an interpreter error object to throw.
 */
function error(message) {
    return new BriliError(message);
}
/**
 * An abstract key class used to access the heap.
 * This allows for "pointer arithmetic" on keys,
 * while still allowing lookups based on the based pointer of each allocation.
 */
var Key = /** @class */ (function () {
    function Key(b, o) {
        this.base = b;
        this.offset = o;
    }
    Key.prototype.add = function (offset) {
        return new Key(this.base, this.offset + offset);
    };
    return Key;
}());
exports.Key = Key;
/**
 * A Heap maps Keys to arrays of a given type.
 */
var Heap = /** @class */ (function () {
    function Heap() {
        this.count = 0;
        this.storage = new Map();
    }
    Heap.prototype.isEmpty = function () {
        return this.storage.size == 0;
    };
    Heap.prototype.getNewBase = function () {
        var val = this.count;
        this.count++;
        return val;
    };
    Heap.prototype.freeKey = function (key) {
        return;
    };
    Heap.prototype.alloc = function (amt) {
        if (amt <= 0) {
            throw error("cannot allocate ".concat(amt, " entries"));
        }
        var base = this.getNewBase();
        this.storage.set(base, new Array(amt));
        return new Key(base, 0);
    };
    Heap.prototype.free = function (key) {
        if (this.storage.has(key.base) && key.offset == 0) {
            this.freeKey(key);
            this.storage["delete"](key.base);
        }
        else {
            throw error("Tried to free illegal memory location base: ".concat(key.base, ", offset: ").concat(key.offset, ". Offset must be 0."));
        }
    };
    Heap.prototype.write = function (key, val) {
        var data = this.storage.get(key.base);
        if (data && data.length > key.offset && key.offset >= 0) {
            data[key.offset] = val;
        }
        else {
            throw error("Uninitialized heap location ".concat(key.base, " and/or illegal offset ").concat(key.offset));
        }
    };
    Heap.prototype.read = function (key) {
        var data = this.storage.get(key.base);
        if (data && data.length > key.offset && key.offset >= 0) {
            return data[key.offset];
        }
        else {
            throw error("Uninitialized heap location ".concat(key.base, " and/or illegal offset ").concat(key.offset));
        }
    };
    return Heap;
}());
exports.Heap = Heap;
var argCounts = {
    add: 2,
    mul: 2,
    sub: 2,
    div: 2,
    id: 1,
    lt: 2,
    le: 2,
    gt: 2,
    ge: 2,
    eq: 2,
    not: 1,
    and: 2,
    or: 2,
    fadd: 2,
    fmul: 2,
    fsub: 2,
    fdiv: 2,
    flt: 2,
    fle: 2,
    fgt: 2,
    fge: 2,
    feq: 2,
    print: null,
    br: 1,
    jmp: 0,
    ret: null,
    nop: 0,
    call: null,
    alloc: 1,
    free: 1,
    store: 2,
    load: 1,
    ptradd: 2,
    phi: null,
    speculate: 0,
    guard: 1,
    commit: 0,
    ceq: 2,
    clt: 2,
    cle: 2,
    cgt: 2,
    cge: 2,
    char2int: 1,
    int2char: 1
};
/**
 * Check whether a run-time value matches the given static type.
 */
function typeCheck(val, typ) {
    if (typ === "int") {
        return typeof val === "bigint";
    }
    else if (typ === "bool") {
        return typeof val === "boolean";
    }
    else if (typ === "float") {
        return typeof val === "number";
    }
    else if (typeof typ === "object" && typ.hasOwnProperty("ptr")) {
        return val.hasOwnProperty("loc");
    }
    else if (typ === "char") {
        return typeof val === "string";
    }
    throw error("unknown type ".concat(typ));
}
/**
 * Check whether the types are equal.
 */
function typeCmp(lhs, rhs) {
    if (lhs === "int" || lhs == "bool" || lhs == "float" || lhs == "char") {
        return lhs == rhs;
    }
    else {
        if (typeof rhs === "object" && rhs.hasOwnProperty("ptr")) {
            return typeCmp(lhs.ptr, rhs.ptr);
        }
        else {
            return false;
        }
    }
}
function get(env, ident) {
    var val = env.get(ident);
    if (typeof val === 'undefined') {
        throw error("undefined variable ".concat(ident));
    }
    return val;
}
function findFunc(func, funcs) {
    var matches = funcs.filter(function (f) {
        return f.name === func;
    });
    if (matches.length == 0) {
        throw error("no function of name ".concat(func, " found"));
    }
    else if (matches.length > 1) {
        throw error("multiple functions of name ".concat(func, " found"));
    }
    return matches[0];
}
function alloc(ptrType, amt, heap) {
    if (typeof ptrType != 'object') {
        throw error("unspecified pointer type ".concat(ptrType));
    }
    else if (amt <= 0) {
        throw error("must allocate a positive amount of memory: ".concat(amt, " <= 0"));
    }
    else {
        var loc = heap.alloc(amt);
        var dataType = ptrType.ptr;
        return {
            loc: loc,
            type: dataType
        };
    }
}
/**
 * Ensure that the instruction has exactly `count` arguments,
 * throw an exception otherwise.
 */
function checkArgs(instr, count) {
    var found = instr.args ? instr.args.length : 0;
    if (found != count) {
        throw error("".concat(instr.op, " takes ").concat(count, " argument(s); got ").concat(found));
    }
}
function getPtr(instr, env, index) {
    var val = getArgument(instr, env, index);
    if (typeof val !== 'object' || val instanceof BigInt) {
        throw "".concat(instr.op, " argument ").concat(index, " must be a Pointer");
    }
    return val;
}
function getArgument(instr, env, index, typ) {
    var args = instr.args || [];
    if (args.length <= index) {
        throw error("".concat(instr.op, " expected at least ").concat(index + 1, " arguments; got ").concat(args.length));
    }
    var val = get(env, args[index]);
    if (typ && !typeCheck(val, typ)) {
        throw error("".concat(instr.op, " argument ").concat(index, " must be a ").concat(typ));
    }
    return val;
}
function getInt(instr, env, index) {
    return getArgument(instr, env, index, 'int');
}
function getBool(instr, env, index) {
    return getArgument(instr, env, index, 'bool');
}
function getFloat(instr, env, index) {
    return getArgument(instr, env, index, 'float');
}
function getChar(instr, env, index) {
    return getArgument(instr, env, index, 'char');
}
function getLabel(instr, index) {
    if (!instr.labels) {
        throw error("missing labels; expected at least ".concat(index + 1));
    }
    if (instr.labels.length <= index) {
        throw error("expecting ".concat(index + 1, " labels; found ").concat(instr.labels.length));
    }
    return instr.labels[index];
}
function getFunc(instr, index) {
    if (!instr.funcs) {
        throw error("missing functions; expected at least ".concat(index + 1));
    }
    if (instr.funcs.length <= index) {
        throw error("expecting ".concat(index + 1, " functions; found ").concat(instr.funcs.length));
    }
    return instr.funcs[index];
}
var NEXT = { "action": "next" };
/**
 * Interpet a call instruction.
 */
function evalCall(instr, state) {
    // Which function are we calling?
    var funcName = getFunc(instr, 0);
    var func = findFunc(funcName, state.funcs);
    if (func === null) {
        throw error("undefined function ".concat(funcName));
    }
    var newEnv = new Map();
    // Check arity of arguments and definition.
    var params = func.args || [];
    var args = instr.args || [];
    if (params.length !== args.length) {
        throw error("function expected ".concat(params.length, " arguments, got ").concat(args.length));
    }
    for (var i = 0; i < params.length; i++) {
        // Look up the variable in the current (calling) environment.
        var value = get(state.env, args[i]);
        // Check argument types
        if (!typeCheck(value, params[i].type)) {
            throw error("function argument type mismatch");
        }
        // Set the value of the arg in the new (function) environment.
        newEnv.set(params[i].name, value);
    }
    // Invoke the interpreter on the function.
    var newState = {
        env: newEnv,
        heap: state.heap,
        funcs: state.funcs,
        icount: state.icount,
        lastlabel: null,
        curlabel: null,
        specparent: null
    };
    var retVal = evalFunc(func, newState);
    state.icount = newState.icount;
    // Dynamically check the function's return value and type.
    if (!('dest' in instr)) { // `instr` is an `EffectOperation`.
        // Expected void function
        if (retVal !== null) {
            throw error("unexpected value returned without destination");
        }
        if (func.type !== undefined) {
            throw error("non-void function (type: ".concat(func.type, ") doesn't return anything"));
        }
    }
    else { // `instr` is a `ValueOperation`.
        // Expected non-void function
        if (instr.type === undefined) {
            throw error("function call must include a type if it has a destination");
        }
        if (instr.dest === undefined) {
            throw error("function call must include a destination if it has a type");
        }
        if (retVal === null) {
            throw error("non-void function (type: ".concat(func.type, ") doesn't return anything"));
        }
        if (!typeCheck(retVal, instr.type)) {
            throw error("type of value returned by function does not match destination type");
        }
        if (func.type === undefined) {
            throw error("function with void return type used in value call");
        }
        if (!typeCmp(instr.type, func.type)) {
            throw error("type of value returned by function does not match declaration");
        }
        state.env.set(instr.dest, retVal);
    }
    return NEXT;
}
/**
 * Interpret an instruction in a given environment, possibly updating the
 * environment. If the instruction branches to a new label, return that label;
 * otherwise, return "next" to indicate that we should proceed to the next
 * instruction or "end" to terminate the function.
 */
function evalInstr(instr, state) {
    state.icount += BigInt(1);
    // Check that we have the right number of arguments.
    if (instr.op !== "const") {
        var count = argCounts[instr.op];
        if (count === undefined) {
            throw error("unknown opcode " + instr.op);
        }
        else if (count !== null) {
            checkArgs(instr, count);
        }
    }
    // Function calls are not (currently) supported during speculation.
    // It would be cool to add, but aborting from inside a function call
    // would require explicit stack management.
    if (state.specparent && ['call', 'ret'].includes(instr.op)) {
        throw error("".concat(instr.op, " not allowed during speculation"));
    }
    switch (instr.op) {
        case "const":
            // Interpret JSON numbers as either ints or floats.
            var value = void 0;
            if (typeof instr.value === "number") {
                if (instr.type === "float")
                    value = instr.value;
                else
                    value = BigInt(Math.floor(instr.value));
            }
            else if (typeof instr.value === "string") {
                if (__spreadArray([], instr.value, true).length !== 1)
                    throw error("char must have one character");
                value = instr.value;
            }
            else {
                value = instr.value;
            }
            state.env.set(instr.dest, value);
            return NEXT;
        case "id": {
            var val = getArgument(instr, state.env, 0);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "add": {
            var val = getInt(instr, state.env, 0) + getInt(instr, state.env, 1);
            val = BigInt.asIntN(64, val);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "mul": {
            var val = getInt(instr, state.env, 0) * getInt(instr, state.env, 1);
            val = BigInt.asIntN(64, val);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "sub": {
            var val = getInt(instr, state.env, 0) - getInt(instr, state.env, 1);
            val = BigInt.asIntN(64, val);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "div": {
            var lhs = getInt(instr, state.env, 0);
            var rhs = getInt(instr, state.env, 1);
            if (rhs === BigInt(0)) {
                throw error("division by zero");
            }
            var val = lhs / rhs;
            val = BigInt.asIntN(64, val);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "le": {
            var val = getInt(instr, state.env, 0) <= getInt(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "lt": {
            var val = getInt(instr, state.env, 0) < getInt(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "gt": {
            var val = getInt(instr, state.env, 0) > getInt(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "ge": {
            var val = getInt(instr, state.env, 0) >= getInt(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "eq": {
            var val = getInt(instr, state.env, 0) === getInt(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "not": {
            var val = !getBool(instr, state.env, 0);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "and": {
            var val = getBool(instr, state.env, 0) && getBool(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "or": {
            var val = getBool(instr, state.env, 0) || getBool(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "fadd": {
            var val = getFloat(instr, state.env, 0) + getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "fsub": {
            var val = getFloat(instr, state.env, 0) - getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "fmul": {
            var val = getFloat(instr, state.env, 0) * getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "fdiv": {
            var val = getFloat(instr, state.env, 0) / getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "fle": {
            var val = getFloat(instr, state.env, 0) <= getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "flt": {
            var val = getFloat(instr, state.env, 0) < getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "fgt": {
            var val = getFloat(instr, state.env, 0) > getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "fge": {
            var val = getFloat(instr, state.env, 0) >= getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "feq": {
            var val = getFloat(instr, state.env, 0) === getFloat(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "print": {
            var args = instr.args || [];
            var values = args.map(function (i) {
                var val = get(state.env, i);
                if (Object.is(-0, val)) {
                    return "-0.00000000000000000";
                }
                ;
                if (typeof val == "number") {
                    return val.toFixed(17);
                }
                else {
                    return val.toString();
                }
            });
            console.log.apply(console, values);
            return NEXT;
        }
        case "jmp": {
            return { "action": "jump", "label": getLabel(instr, 0) };
        }
        case "br": {
            var cond = getBool(instr, state.env, 0);
            if (cond) {
                return { "action": "jump", "label": getLabel(instr, 0) };
            }
            else {
                return { "action": "jump", "label": getLabel(instr, 1) };
            }
        }
        case "ret": {
            var args = instr.args || [];
            if (args.length == 0) {
                return { "action": "end", "ret": null };
            }
            else if (args.length == 1) {
                var val = get(state.env, args[0]);
                return { "action": "end", "ret": val };
            }
            else {
                throw error("ret takes 0 or 1 argument(s); got ".concat(args.length));
            }
        }
        case "nop": {
            return NEXT;
        }
        case "call": {
            return evalCall(instr, state);
        }
        case "alloc": {
            var amt = getInt(instr, state.env, 0);
            var typ = instr.type;
            if (!(typeof typ === "object" && typ.hasOwnProperty('ptr'))) {
                throw error("cannot allocate non-pointer type ".concat(instr.type));
            }
            var ptr = alloc(typ, Number(amt), state.heap);
            state.env.set(instr.dest, ptr);
            return NEXT;
        }
        case "free": {
            var val = getPtr(instr, state.env, 0);
            state.heap.free(val.loc);
            return NEXT;
        }
        case "store": {
            var target = getPtr(instr, state.env, 0);
            state.heap.write(target.loc, getArgument(instr, state.env, 1, target.type));
            return NEXT;
        }
        case "load": {
            var ptr = getPtr(instr, state.env, 0);
            var val = state.heap.read(ptr.loc);
            if (val === undefined || val === null) {
                throw error("Pointer ".concat(instr.args[0], " points to uninitialized data"));
            }
            else {
                state.env.set(instr.dest, val);
            }
            return NEXT;
        }
        case "ptradd": {
            var ptr = getPtr(instr, state.env, 0);
            var val = getInt(instr, state.env, 1);
            state.env.set(instr.dest, { loc: ptr.loc.add(Number(val)), type: ptr.type });
            return NEXT;
        }
        case "phi": {
            var labels = instr.labels || [];
            var args = instr.args || [];
            if (labels.length != args.length) {
                throw error("phi node has unequal numbers of labels and args");
            }
            if (!state.lastlabel) {
                throw error("phi node executed with no last label");
            }
            var idx = labels.indexOf(state.lastlabel);
            if (idx === -1) {
                // Last label not handled. Leave uninitialized.
                state.env["delete"](instr.dest);
            }
            else {
                // Copy the right argument (including an undefined one).
                if (!instr.args || idx >= instr.args.length) {
                    throw error("phi node needed at least ".concat(idx + 1, " arguments"));
                }
                var src = instr.args[idx];
                var val = state.env.get(src);
                if (val === undefined) {
                    state.env["delete"](instr.dest);
                }
                else {
                    state.env.set(instr.dest, val);
                }
            }
            return NEXT;
        }
        // Begin speculation.
        case "speculate": {
            return { "action": "speculate" };
        }
        // Abort speculation if the condition is false.
        case "guard": {
            if (getBool(instr, state.env, 0)) {
                return NEXT;
            }
            else {
                return { "action": "abort", "label": getLabel(instr, 0) };
            }
        }
        // Resolve speculation, making speculative state real.
        case "commit": {
            return { "action": "commit" };
        }
        case "ceq": {
            var val = getChar(instr, state.env, 0) === getChar(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "clt": {
            var val = getChar(instr, state.env, 0) < getChar(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "cle": {
            var val = getChar(instr, state.env, 0) <= getChar(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "cgt": {
            var val = getChar(instr, state.env, 0) > getChar(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "cge": {
            var val = getChar(instr, state.env, 0) >= getChar(instr, state.env, 1);
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "char2int": {
            var code = getChar(instr, state.env, 0).codePointAt(0);
            var val = BigInt.asIntN(64, BigInt(code));
            state.env.set(instr.dest, val);
            return NEXT;
        }
        case "int2char": {
            var i = getInt(instr, state.env, 0);
            if (i > 1114111 || i < 0 || (55295 < i && i < 57344)) {
                throw error("value ".concat(i, " cannot be converted to char"));
            }
            var val = String.fromCodePoint(Number(i));
            state.env.set(instr.dest, val);
            return NEXT;
        }
    }
    (0, util_ts_1.unreachable)(instr);
    throw error("unhandled opcode ".concat(instr.op));
}
function evalFunc(func, state) {
    for (var i = 0; i < func.instrs.length; ++i) {
        var line = func.instrs[i];
        if ('op' in line) {
            // Run an instruction.
            var action = evalInstr(line, state);
            // Take the prescribed action.
            switch (action.action) {
                case 'end': {
                    // Return from this function.
                    return action.ret;
                }
                case 'speculate': {
                    // Begin speculation.
                    state.specparent = __assign({}, state);
                    state.env = new Map(state.env);
                    break;
                }
                case 'commit': {
                    // Resolve speculation.
                    if (!state.specparent) {
                        throw error("commit in non-speculative state");
                    }
                    state.specparent = null;
                    break;
                }
                case 'abort': {
                    // Restore state.
                    if (!state.specparent) {
                        throw error("abort in non-speculative state");
                    }
                    // We do *not* restore `icount` from the saved state to ensure that we
                    // count "aborted" instructions.
                    Object.assign(state, {
                        env: state.specparent.env,
                        lastlabel: state.specparent.lastlabel,
                        curlabel: state.specparent.curlabel,
                        specparent: state.specparent.specparent
                    });
                    break;
                }
                case 'next':
                case 'jump':
                    break;
                default:
                    (0, util_ts_1.unreachable)(action);
                    throw error("unhandled action ".concat(action.action));
            }
            // Move to a label.
            if ('label' in action) {
                // Search for the label and transfer control.
                for (i = 0; i < func.instrs.length; ++i) {
                    var sLine = func.instrs[i];
                    if ('label' in sLine && sLine.label === action.label) {
                        --i; // Execute the label next.
                        break;
                    }
                }
                if (i === func.instrs.length) {
                    throw error("label ".concat(action.label, " not found"));
                }
            }
        }
        else if ('label' in line) {
            // Update CFG tracking for SSA phi nodes.
            state.lastlabel = state.curlabel;
            state.curlabel = line.label;
        }
    }
    // Reached the end of the function without hitting `ret`.
    if (state.specparent) {
        throw error("implicit return in speculative state");
    }
    return null;
}
function parseChar(s) {
    var c = s;
    if (__spreadArray([], c, true).length === 1) {
        return c;
    }
    else {
        throw error("char argument to main must have one character; got ".concat(s));
    }
}
function parseBool(s) {
    if (s === 'true') {
        return true;
    }
    else if (s === 'false') {
        return false;
    }
    else {
        throw error("boolean argument to main must be 'true'/'false'; got ".concat(s));
    }
}
function parseNumber(s) {
    var f = parseFloat(s);
    // parseFloat and Number have subtly different behaviors for parsing strings
    // parseFloat ignores all random garbage after any valid number
    // Number accepts empty/whitespace only strings and rejects numbers with seperators
    // Use both and only accept the intersection of the results?
    var f2 = Number(s);
    if (!isNaN(f) && f === f2) {
        return f;
    }
    else {
        throw error("float argument to main must not be 'NaN'; got ".concat(s));
    }
}
function parseMainArguments(expected, args) {
    var newEnv = new Map();
    if (args.length !== expected.length) {
        throw error("mismatched main argument arity: expected ".concat(expected.length, "; got ").concat(args.length));
    }
    for (var i = 0; i < args.length; i++) {
        var type = expected[i].type;
        switch (type) {
            case "int":
                // https://dev.to/darkmavis1980/you-should-stop-using-parseint-nbf
                var n = BigInt(Number(args[i]));
                newEnv.set(expected[i].name, n);
                break;
            case "float":
                var f = parseNumber(args[i]);
                newEnv.set(expected[i].name, f);
                break;
            case "bool":
                var b = parseBool(args[i]);
                newEnv.set(expected[i].name, b);
                break;
            case "char":
                var c = parseChar(args[i]);
                newEnv.set(expected[i].name, c);
                break;
        }
    }
    return newEnv;
}
function evalProg(prog) {
    var heap = new Heap();
    var main = findFunc("main", prog.functions);
    if (main === null) {
        console.warn("no main function defined, doing nothing");
        return;
    }
    // Silly argument parsing to find the `-p` flag.
    var args = Array.from(Deno.args);
    var profiling = false;
    var pidx = args.indexOf('-p');
    if (pidx > -1) {
        profiling = true;
        args.splice(pidx, 1);
    }
    // Remaining arguments are for the main function.k
    var expected = main.args || [];
    var newEnv = parseMainArguments(expected, args);
    var state = {
        funcs: prog.functions,
        heap: heap,
        env: newEnv,
        icount: BigInt(0),
        lastlabel: null,
        curlabel: null,
        specparent: null
    };
    evalFunc(main, state);
    if (!heap.isEmpty()) {
        throw error("Some memory locations have not been freed by end of execution.");
    }
    if (profiling) {
        console.error("total_dyn_inst: ".concat(state.icount));
    }
}
function main() {
    return __awaiter(this, void 0, void 0, function () {
        var prog, _a, _b, e_1;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    _c.trys.push([0, 2, , 3]);
                    _b = (_a = JSON).parse;
                    return [4 /*yield*/, (0, util_ts_1.readStdin)()];
                case 1:
                    prog = _b.apply(_a, [_c.sent()]);
                    evalProg(prog);
                    return [3 /*break*/, 3];
                case 2:
                    e_1 = _c.sent();
                    if (e_1 instanceof BriliError) {
                        console.error("error: ".concat(e_1.message));
                        Deno.exit(2);
                    }
                    else {
                        throw e_1;
                    }
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    });
}
main();
