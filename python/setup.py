# References
'''
https://github.com/FedericoStra/cython-package-example/blob/master/setup.py
https://github.com/thewtex/cython-cmake-example/blob/master/setup.py
'''

import os
from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages, find_namespace_packages, Extension
from Cython.Build import cythonize

import numpy as np
import pyarrow as pa

mpi_compile_args = os.popen("mpic++ --showme:compile").read().strip().split(' ')
mpi_link_args = os.popen("mpic++ --showme:link").read().strip().split(' ')

twisterx_cpp_third_party_glog = "../cpp/build/thirdparty/glog/"
_include_dirs = ["../cpp/src/twisterx/lib", "../cpp/src/twisterx/",
                 "../cpp/src/twisterx/data", "../cpp/src/twisterx/io", "../cpp/src/twisterx/join",
                 "../cpp/src/twisterx/util", " ../cpp/build/arrow/install/include/", twisterx_cpp_third_party_glog,
                 "../cpp/build/external/Catch/include", "../cpp/build/arrow/install/lib"
                 ]

ext_modules = [
    Extension("pytwisterx.geometry",
              sources=["../cpp/src/twisterx/lib/Circle.cpp", "twisterx/geometry/circle.pyx"],
              include_dirs=_include_dirs,
              language='c++',
              extra_compile_args=["-std=c++14"],
              extra_link_args=mpi_link_args,
              ),
    Extension("pytwisterx.tablebuilder",
              sources=["../cpp/src/twisterx/data/table_builder.cpp", "twisterx/tablebuilder/table_builder.pyx"],
              include_dirs=_include_dirs,
              language='c++',
              extra_compile_args=["-std=c++14"],
              extra_link_args=mpi_link_args,
              ),
    Extension("pytwisterx.common.code",
              sources=["twisterx/common/code.pyx"],
              include_dirs=_include_dirs,
              language='c++',
              extra_compile_args=["-std=c++14"],
              extra_link_args=mpi_link_args,
              ),
    Extension("pytwisterx.common.status",
              sources=["twisterx/common/status.pyx"],
              include_dirs=_include_dirs,
              language='c++',
              extra_compile_args=["-std=c++14"],
              extra_link_args=mpi_link_args,
              ),
    # Extension("pytwisterx.api.table",
    #           sources=["twisterx/api/table.pyx"],
    #           # "../cpp/src/twisterx/table_api.cpp"
    #           include_dirs=_include_dirs,
    #           language='c++',
    #           extra_compile_args=["-std=c++17"],
    #           extra_link_args=mpi_link_args,
    #           ),
    Extension("pytwisterx.tablebuilder",
              sources=["twisterx/tablebuilder/table_builder.pyx", "../cpp/src/twisterx/data/table_builder.cpp"],
              include_dirs=_include_dirs,
              library_dirs=[get_python_lib(),
                            "/home/vibhatha/github/forks/twisterx/cpp/build/arrow/install/lib/libarrow.so.16"],
              language='c++',
              extra_compile_args=["-std=c++14"],
              extra_link_args=mpi_link_args,
              )
]

# cython_files = ["twisterx/**/*.pyx"]
# ext_modules = [
#     Extension(
#         "*",
#         sources=cython_files,
#         include_dirs=[
#             "../cpp/src/twisterx/lib",
#             "../cpp/src/twisterx/data",
#             "../cpp/src/twisterx",
#             # "../../cpp/include",
#             # "../../cpp/build/include",
#             # "../../thirdparty/cub",
#             # "../../thirdparty/libcudacxx/include",
#             # os.path.dirname(sysconfig.get_path("include")),
#             numpy.get_include(),
#             pyarrow.get_include(),
#         ],
#         library_dirs=[get_python_lib(), os.path.join(os.sys.prefix, "lib")],
#         language="c++",
#         #libraries=["twisterx"],
#         extra_compile_args=["-std=c++17"],
#     )
# ]

compiler_directives = {"language_level": 3, "embedsignature": True}

ext_modules = cythonize(ext_modules, compiler_directives=compiler_directives)

for ext in ext_modules:
    # The Numpy C headers are currently required
    ext.include_dirs.append(np.get_include())
    ext.include_dirs.append(pa.get_include())
    ext.libraries.extend(pa.get_libraries())
    ext.library_dirs.extend(pa.get_library_dirs())
    ext.define_macros.append(("_GLIBCXX_USE_CXX11_ABI", "0"))

setup(
    name="pytwisterx",
    packages=['twisterx', 'twisterx.geometry', 'twisterx.tablebuilder', 'twisterx.common'],
    version='0.0.1',
    setup_requires=["cython", "setuptools", "numpy"],
    ext_modules=ext_modules,
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'cython',
        'pyarrow'
    ],
    zip_safe=False,
    library_dirs=[get_python_lib(),
                  os.path.join("/home/vibhatha/github/forks/twisterx/cpp/build/arrow/install/lib/libarrow.so.16")],
    package_data={'': ['/home/vibhatha/github/forks/twisterx/cpp/build/arrow/install/lib/libarrow.so.16']},
)

# print(find_namespace_packages())
