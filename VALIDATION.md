# Validation

## Git branch packaging, 2026-10-09

- Replaced the scheduled tagged-release workflow and updater script with native
  makepkg Git sources, `prepare()` and `pkgver()`. The package name is unchanged.
- Built Strata main at fb58e0dbc8399662c0e47c76578c6e878b14f6cf as
  `0.1.41.r1552.gfb58e0db-1`, using its pinned llama.cpp commit
  3cf03257f219afbe7334045ff7c6a06ac68c627d.
- The text engine compiled for CUDA architectures 75/86/89/120. The completed
  package builds text and vision for CUDA architecture 120, using 16 build jobs.
  The attempted portable vision build was stopped to use this machine's GPU
  architecture, not because of a compiler failure. The shared recipe retains
  portable defaults; paru's native environment settings select local targets.
- Eight launcher tests and nine upstream runconfig tests passed. Bash syntax,
  local source checksums and .SRCINFO consistency checks passed. Git sources
  use makepkg's standard SKIP checksum handling.
- The packaged device executable detected the RTX 5090. Text and vision help
  commands ran, and native shared-library dependencies resolved.
- Existing production service remained active. Installation requires the user's
  sudo password; install through paru once to initialise native commit tracking.
  No model downloads, real-model inference checks or quality benchmarks were
  performed for this package update. These checks do not establish that future
  main-branch commits are regression-free.

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
