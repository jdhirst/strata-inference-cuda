# Validation

Validated locally on 2026-10-05 with CachyOS, Ryzen 9 9950X3D, RTX 5090,
192 GB installed RAM, CUDA 13.4.2, GCC 16.2.1 and Python 3.14.7.

- Built the package with makepkg, first for CUDA architecture 120 and then with
  the default 75/86/89/120 architecture set. Both builds completed.
- Eight launcher tests passed: symlinked model storage, model-root confinement,
  configuration placement, preservation of an existing config, authenticated
  network binding, no implicit downloads during preparation, and split lookup
  table discovery, CUDA vision configuration with image-token limits and VRAM
  reservation, and rejection of a missing projector (several checks share a test).
- Nine upstream runconfig tests passed in the package's check() phase.
- Extracted the package and verified the device executable detects the RTX 5090.
- ldd resolved all native runtime dependencies, including system CUDA libraries.
- Packaged Python server and MTP packer accepted --help using system Python.
- Started the extracted API server in upstream mock mode: /health, /v1/models
  and the packaged browser UI responded successfully. Stopped it afterward.
- Built version 0.1.39-2 with the CUDA vision encoder for architectures
  75/86/89/120; compilation and the package check() phase completed.
- PKGBUILD passed bash syntax validation and makepkg source checksum validation.

No real model was downloaded, prepared or loaded for these checks. No inference
speed or quality benchmark has been performed. Existing model services remained
running. Installation was attempted but sudo requires the user's password, so
testing the installed image encoder is pending. The package has not been tested
in a clean chroot or on GPUs other than the RTX 5090. GPU code for the other
architectures compiled but has not been executed on those cards.

The default portable build explicitly overrides a local -march=native setting
with x86-64 / generic tuning; upstream separately selects its AVX2 baseline and
runtime AVX-512 kernels. Compiler warnings originate in upstream code. makepkg
may report embedded CUDA diagnostic source paths; these are not runtime file
dependencies.

GitHub CI checks the launcher, source checksums and .SRCINFO consistency.
The initial text-package CI run passed on GitHub. CI does not test GPU inference.
