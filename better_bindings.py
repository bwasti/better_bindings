import os
import importlib
import importlib.util
import tempfile
import sysconfig
import functools

include_template = """#define PY_SSIZE_T_CLEAN
#define Py_LIMITED_API 0x030B0000
#include <Python.h>
#include <stdlib.h>

"""

method_template = """
static PyObject *method_{method_name}(PyObject *self, PyObject *args) {{
  {body}
}}
"""

method_def_template = """{{"{method_name}", method_{method_name}, METH_VARARGS, "{method_descr}"}},
"""

method_defs_template = """
static PyMethodDef {module_name}Methods[] = {{
  {methods}
  {{NULL, NULL, 0, NULL}}
}};
"""

module_init_template = """
static struct PyModuleDef {module_name}_module = {{
    PyModuleDef_HEAD_INIT,
    "{module_name}",
    "TODO",
    -1,
    {module_name}Methods
}};

PyMODINIT_FUNC PyInit_{module_name}(void) {{
    return PyModule_Create(&{module_name}_module);
}}
"""

build_template = "cc -O3 {generated_file} {lib_file} -shared -o {binary_name} {includes} -Wl,-undefined,dynamic_lookup 2>/dev/null"


class Types(object):
    def __init__(self):
        self.int32 = ("int32_t", "i")
        self.uint32 = ("uint32_t", "I")
        self.float = ("float", "f")
        self.string = ("char*", "s")
        self.ptr = ("void*", "L")  # encoded in a long
        self.void = ("void", "")


types = Types()


def gen_method(symbol, real_symbol, args, out, descr):
    arg_decl = "; ".join([f"{inp[0]} inp{i}" for i, inp in enumerate(args)]) + ";"
    arg_refs = ", ".join([f"&inp{i}" for i in range(len(args))])
    arg_real = ", ".join([f"inp{i}" for i in range(len(args))])

    body = arg_decl
    input_type_string = "".join(inp[1] for inp in args)
    body += f"""
    if(!PyArg_ParseTuple(args, "{input_type_string}", {arg_refs})) {{
        Py_RETURN_NONE;
    }}
    """
    if out[0] == "void":
        body += f"""
        {real_symbol}({arg_real});
        Py_RETURN_NONE;
        """
    else:
        body += f"""
        {out[0]} out = {real_symbol}({arg_real});
        PyObject* py_out = Py_BuildValue("{out[1]}", out);
        return py_out;
        """
    impl = method_template.format(method_name=symbol, body=body)
    reg = method_def_template.format(method_name=symbol, method_descr=descr)

    return impl, reg


module_count = 0


def bind(file, binding_map):
    global module_count

    declarations = []
    impls = []
    regs = []
    for symbol, v in binding_map.items():
        real_symbol = symbol
        inputs = []
        output = types.void
        if len(v) == 2:
            inputs, output = v
        elif len(v) == 3:
            real_symbol, inputs, output = v
        else:
            raise Exception(f"invalid binding: {v}")

        declaration = (
            f"{output[0]} {real_symbol}({', '.join([i[0] for i in inputs])});\n"
        )
        declarations.append(declaration)
        impl, reg = gen_method(symbol, real_symbol, inputs, output, declaration.strip())
        impls.append(impl)
        regs.append(reg)

    module_name = f"module{module_count}"
    module_count += 1
    registration = method_defs_template.format(
        module_name=module_name, methods="".join(regs)
    )
    init = module_init_template.format(module_name=module_name, lib_file=file)
    source = tempfile.NamedTemporaryFile(suffix=".c", delete=True)
    module_binary = tempfile.NamedTemporaryFile(
        suffix=sysconfig.get_config_var("EXT_SUFFIX")
    )
    include_flags = [
        "-I" + sysconfig.get_path("include"),
        "-I" + sysconfig.get_path("platinclude"),
    ]
    includes = " ".join(include_flags)
    with open(source.name, "w") as f:
        f.write(include_template)
        for d in declarations:
            f.write(d)
        for impl in impls:
            f.write(impl)
        f.write(registration)
        f.write(init)
        f.flush()
        os.system(
            build_template.format(
                generated_file=source.name,
                binary_name=module_binary.name,
                includes=includes,
                lib_file=file,
            )
        )
        spec = importlib.util.spec_from_file_location(module_name, module_binary.name)
        return importlib.util.module_from_spec(spec)


def object(file, binding_map):
    m = bind(file, binding_map)

    class Obj:
        def __init__(self, *args):
            self.ptr = m.__init__(*args)

        def __del__(self):
            m.__del__(self.ptr)

        @functools.cache
        def __getattr__(self, attr):
            if attr not in binding_map:
                raise Exception(f"Bound object does not have this method: {attr}")

            def f(*args):
                g = getattr(m, attr)
                return g(self.ptr, *args)

            return f

    return Obj


float = types.float
int32 = types.int32
void = types.void
ptr = types.ptr
__all__ = ["bind", "object", "float", "int32", "void", "ptr"]
