licenses(["notice"])  # Apache 2.0

load("//build_defs:rules.bzl", "j2cl_library")
load(
    "//transpiler/javatests/com/google/j2cl/transpiler/integration:integration_test.bzl",
    "integration_test",
)

j2cl_library(
    name = "SuperParent",
    srcs = ["SuperParent.java"],
)

j2cl_library(
    name = "MyInterface",
    srcs = ["MyInterface.java"],
)

j2cl_library(
    name = "Parent",
    srcs = ["Parent.java"],
    deps = [
        ":SuperParent",
        "//third_party:gwt-jsinterop-annotations-j2cl",
    ],
)

j2cl_library(
    name = "Child",
    srcs = ["Child.java"],
    deps = [
        ":MyInterface",
        ":Parent",
        "//third_party:gwt-jsinterop-annotations-j2cl",
    ],
)

# Creates targets
# blaze build :optimized_js
# blaze test :compiled_test
# blaze test :uncompiled_test
integration_test(
    name = "instancejsmethods",
    srcs = ["Main.java"],
    native_srcs = ["Main.native.js"],
    deps = [
        ":Child",
        ":MyInterface",
        ":Parent",
        ":SuperParent",
        "//third_party:gwt-jsinterop-annotations-j2cl",
    ],
)
