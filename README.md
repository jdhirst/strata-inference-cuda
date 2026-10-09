# strata-inference-cuda

Arch Linux / CachyOS packaging for [Strata](https://github.com/Niko1221/Strata),
the CUDA local inference engine for Qwen3.8-Flash-Next. Strata sources track
upstream main; local packaging files are checksummed. The engine is built by
makepkg and managed by pacman.
Python, CUDA and build tools come from native repositories. No pip, virtualenv,
self-updater, model downloads, or running services are invoked by installation.

## Build and install

```sh
git clone https://github.com/jdhirst/strata-inference-cuda.git
cd strata-inference-cuda
makepkg -si
```

The default build includes RTX 20/30/40/50 CUDA architectures (75/86/89/120),
with an AVX2 CPU baseline and runtime-selected AVX-512 kernels. Requires a CUDA
13-compatible NVIDIA driver and a supported NVIDIA GPU. Model requirements and
speed vary by quantization, context, RAM, VRAM and PCIe bandwidth.

For a faster build on this RTX 5090, targeting only its GPU:

```sh
STRATA_CUDA_ARCHITECTURES=120 STRATA_BUILD_JOBS=8 makepkg -si
```

This locally customized package will only support the specified GPU architecture.
CUDA K-quant prompt kernels are enabled for supported Unsloth models.
The package includes text and image inference with a CUDA vision encoder.
The pinned llama.cpp sources provide upstream's required ggml kernels and
gguf Python format support; system llama-server remains independent.

## Package updates through paru

No AUR account is needed. Add this GitHub PKGBUILD repository to
`~/.config/paru/paru.conf`:

```ini
[strata]
Url = https://github.com/jdhirst/strata-inference-cuda.git
Depth = 1
```

Normal `paru -Syu` checks this repository and offers newer versions of the same
`strata-inference-cuda` package. Model files and the user's configuration are
separate from the package. Keep an older `.pkg.tar.zst` for rollback with
`sudo pacman -U /path/to/package.pkg.tar.zst`.

This same package now tracks Strata's `main` branch using native makepkg Git
sources and `pkgver()`. In paru's existing `[options]` section enable:

```ini
Devel
DevelSuffixes = -git -cvs -svn -bzr -darcs -always -hg -fossil strata-inference-cuda
IgnoreDevelSource = https://github.com/ggml-org/llama.cpp.git
```

The extra development suffix preserves the existing package name. Paru records
upstream Git revisions when it builds the package and offers rebuilds for new
Strata commits on `paru -Syu`. No schedule, wrapper or update script is needed.
Install this Git-backed version once with `paru -S strata/strata-inference-cuda`
to initialise commit tracking. The build checks out the llama.cpp commit pinned
by the selected Strata revision; unrelated llama.cpp commits do not trigger
updates. Versions include the upstream project version, commit count and hash.

Main is development code and can regress. Source checks and launcher tests do
not establish GPU inference quality. Keep the previous package for rollback;
a failing build leaves the installed package in place.

## Models

Models are deliberately separate from the package. Put all GGUF shards together
in a descriptive directory under `~/.models`, e.g.
`~/.models/qwen3.8-flash-next-gsq-rco-iq3-s/`. The launcher preserves a symlinked
model root. Prepared packs, tokenizers, draft weights and runtime files also stay
under that root. No large model download happens without an explicit command.

```sh
strata-inference prepare ~/.models/qwen3.8-flash-next-gsq-rco-iq3-s/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf
# Explicit ~6 GB download of the original BF16 draft head, followed by conversion:
strata-inference prepare-mtp
strata-inference configure ~/.models/qwen3.8-flash-next-gsq-rco-iq3-s/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf --context 131072
strata-inference serve --config ~/.config/strata-inference/qwen3.8-flash-next-gsq-rco-iq3-s.json
```

Browser: `http://127.0.0.1:8082`. OpenAI API: `http://127.0.0.1:8082/v1`.
Check readiness with `curl http://127.0.0.1:8082/health`.
Configuration lives in `~/.config/strata-inference`; logs live in
`~/.local/state/strata-inference`. XDG_CONFIG_HOME and XDG_STATE_HOME are respected.
No service is enabled automatically. Stop other GPU model servers before loading
if they occupy the required VRAM. Ctrl-C stops the foreground server.

## Image input

Put the matching vision projector GGUF beside your model under `~/.models`.
When generating a new configuration, add `--mmproj`:

```sh
strata-inference configure ~/.models/qwen3.8-flash-next-gsq-rco-iq3-s/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf \
  --mmproj ~/.models/qwen3.8-flash-next-gsq-rco-iq3-s/mmproj-Qwen3.8-Flash-Next-BF16.gguf
```

The model and projector must match and be supported by upstream. The launcher
enables the engine's vision path, runs image encoding on CUDA, and reserves
1400 MiB beyond the encoder's allocations for image-processing buffers. Image
resolution is capped at 1024 image tokens by default; use `--vision-tokens N`
to change it. Higher values can use more VRAM. Attach pictures in the web Chat
page or send OpenAI-compatible image input through the API. Projectors are not
downloaded by package installation.

Existing configurations are preserved. To enable images in one, add a `vision`
object with `exe` `/usr/bin/strata-inference-vision`, absolute `mmproj` and `model`
paths, `gpu: true`, and `max_tokens: 1024`; append `--vision`,
`--vram-reserve-mib`, `1400` to the engine's `args` array. Alternatively, back up
the existing config and generate it again with `--mmproj`.

For network access, specify both `--host 0.0.0.0` and `--api-key SECRET`.
`STRATA_API_KEY` can supply the key without placing it in the shell history.
Upstream answers one request at a time by default.

Custom quants require upstream compatibility checks. `prepare --compat-bf16`
explicitly converts certain auxiliary projections; this does not establish that
an arbitrary GGUF is supported or restore its original quality. In particular,
the existing IQ4XS-NGQ4 uncensored model has not been validated with this package.
See upstream [model documentation](https://github.com/Niko1221/Strata/blob/main/docs/MODELS.md).

## Development and AUR publication

```sh
bash -n PKGBUILD
python -m unittest discover -s tests -v
makepkg --verifysource
makepkg --printsrcinfo > .SRCINFO
makepkg --cleanbuild
```

The GitHub repository is the development home; AUR hosting is a separate git
repository. Publish only after validating the built package and setting up an
AUR account with an SSH key. Copy PKGBUILD, .SRCINFO, strata-inference and README.md
into `ssh://aur@aur.archlinux.org/strata-inference-cuda.git` and push there.
Do not upload binary packages or model weights to the AUR. Update source hashes
when changing upstream versions. Native dependency updates come through pacman.
Refresh local source hashes after editing the launcher, README or license, and
regenerate .SRCINFO. See [VALIDATION.md](VALIDATION.md) for the exact local checks
and remaining validation limits.

Package recipes and launcher: MIT. Upstream Strata and pinned llama.cpp: MIT,
with their license files installed by this package. Model licenses remain separate.
