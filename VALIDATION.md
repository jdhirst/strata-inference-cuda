# Validation

Validated locally on 2026-10-05 with CachyOS, Ryzen 9 9950X3D, RTX 5090,
192 GB installed RAM, CUDA 13.4.2, GCC 16.2.1 and Python 3.14.7.

- Built the package with makepkg, first for CUDA architecture 120 and then with
  the default 75/86/89/120 architecture set. Both builds completed.
- Six launcher tests passed: symlinked model storage, model-root confinement,
  configuration placement, preservation of an existing config, authenticated
  network binding, no implicit downloads during preparation, and split lookup
  table discovery (several checks share a test).
- Nine upstream runconfig tests passed in the package's check() phase.
- Extracted the package and verified the device executable detects the RTX 5090.
- ldd resolved all native runtime dependencies, including system CUDA libraries.
- Packaged Python server and MTP packer accepted --help using system Python.
- Started the extracted API server in upstream mock mode: /health, /v1/models
  and the packaged browser UI responded successfully. Stopped it afterward.
- PKGBUILD passed bash syntax validation and makepkg source checksum validation.

No real model was downloaded, prepared or loaded for these checks. No inference
speed or quality benchmark has been performed. Existing model services remained
running. The package has not yet been installed into the system, tested in a
clean chroot, or tested on GPUs other than the RTX 5090. GPU code for the other
architectures compiled but has not been executed on those cards.

The default portable build explicitly overrides a local -march=native setting
with x86-64 / generic tuning; upstream separately selects its AVX2 baseline and
runtime AVX-512 kernels. Compiler warnings originate in upstream code. makepkg
may report embedded CUDA diagnostic source paths; these are not runtime file
dependencies.

GitHub CI checks the launcher, source checksums and .SRCINFO consistency. The CI
workflow has not been run on GitHub yet and does not claim to test GPU inference.
