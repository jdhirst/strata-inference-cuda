# Maintainer: jdhirst <jdhirst@hirstgroup.net>
pkgname=strata-inference-cuda
pkgver=0.1.41.r1552.gfb58e0db
pkgrel=1
pkgdesc='Strata CUDA inference engine and local API server for Qwen3.8-Flash-Next'
arch=('x86_64')
url='https://github.com/Niko1221/Strata'
license=('MIT')
depends=('cuda>=13' 'gcc-libs' 'glibc' 'python' 'python-numpy' 'python-jinja'
         'python-regex' 'python-yaml' 'python-tqdm' 'python-requests'
         'python-pillow' 'python-psutil')
makedepends=('cmake' 'ninja' 'git')
optdepends=('nvidia-utils: NVIDIA driver and GPU monitoring')
options=('!lto')
source=('strata::git+https://github.com/Niko1221/Strata.git#branch=main'
        'llama.cpp::git+https://github.com/ggml-org/llama.cpp.git#branch=master'
        'strata-inference'
        'README.md'
        'LICENSE')
sha256sums=('SKIP'
            'SKIP'
            'f6b898688d5cdc62fd974cb2ec25de8000a3e9f489b519ed7befa8d2d50cad9b'
            '87233fc184aa1397bc6f2c56dfa5ada20433638ea712560b465dbda196391d84'
            '3aa11484d0b26858dc8e662f17e88ad03e4184d55b69f9b5e29e6feddd999ab5')

pkgver() {
  cd "${srcdir}/strata"
  local release revision
  release=$(sed -n 's/^project(strata VERSION \([0-9.]*\) LANGUAGES.*$/\1/p' CMakeLists.txt)
  [[ "$release" =~ ^[0-9]+(\.[0-9]+)+$ ]] || return 1
  revision=$(git rev-list --count HEAD)
  printf '%s.r%s.g%s' "$release" "$revision" "$(git rev-parse --short HEAD)"
}

prepare() {
  # Match Strata's ggml dependency, rather than building against arbitrary HEAD.
  local pin
  read -r pin _ < "${srcdir}/strata/third_party/ggml/VERSION.txt"
  [[ "$pin" =~ ^[0-9a-f]{40}$ ]] || return 1
  git -C "${srcdir}/llama.cpp" checkout --detach "$pin"
}

build() {
  # CachyOS may set -march=native. Keep redistributed binaries portable.
  export CFLAGS="${CFLAGS} -march=x86-64 -mtune=generic -ffile-prefix-map=${srcdir}=."
  export CXXFLAGS="${CXXFLAGS} -march=x86-64 -mtune=generic -ffile-prefix-map=${srcdir}=."
  cmake -S "strata" -B build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DSTRATA_ENABLE_CUDA=ON \
    -DSTRATA_PORTABLE=ON \
    -DSTRATA_BUILD_TESTS=OFF \
    -DSTRATA_MMQ_KQUANTS=ON \
    -DSTRATA_GGML_DIR="${srcdir}/llama.cpp" \
    -DCMAKE_CUDA_COMPILER=/opt/cuda/bin/nvcc \
    -DCMAKE_CUDA_ARCHITECTURES="${STRATA_CUDA_ARCHITECTURES:-75;86;89;120}" \
    -DCMAKE_CUDA_RUNTIME_LIBRARY=Shared \
    -DCMAKE_BUILD_RPATH=/opt/cuda/lib64 \
    -DCMAKE_INSTALL_RPATH=/opt/cuda/lib64 \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON
  cmake --build build --target strata strata-device --parallel "${STRATA_BUILD_JOBS:-4}"
  cmake -S "strata/tools/vision" -B build-vision -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLAMA_DIR="${srcdir}/llama.cpp" \
    -DSTRATA_VISION_CUDA=ON \
    -DSTRATA_PORTABLE=ON \
    -DCMAKE_CUDA_COMPILER=/opt/cuda/bin/nvcc \
    -DCMAKE_CUDA_ARCHITECTURES="${STRATA_CUDA_ARCHITECTURES:-75;86;89;120}" \
    -DCMAKE_CUDA_RUNTIME_LIBRARY=Shared \
    -DCMAKE_BUILD_RPATH=/opt/cuda/lib64 \
    -DCMAKE_INSTALL_RPATH=/opt/cuda/lib64 \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON
  cmake --build build-vision --target strata-vision --parallel "${STRATA_BUILD_JOBS:-4}"
}

check() {
  python -c 'import numpy, jinja2, regex, yaml, tqdm, requests, PIL, psutil'
  python "${srcdir}/strata-inference" --help
  PYTHONPATH="${srcdir}/strata" \
    STRATA_GGUF_PY="${srcdir}/llama.cpp/gguf-py" \
    python -m unittest discover -s "${srcdir}/strata/serve" -p 'test_runconfig.py'
}

package() {
  local upstream="${srcdir}/strata"
  local app="${pkgdir}/usr/lib/strata-inference"
  install -Dm755 build/strata "${pkgdir}/usr/bin/strata-inference-engine"
  install -Dm755 build/strata-device "${pkgdir}/usr/bin/strata-inference-device"
  install -Dm755 build-vision/bin/strata-vision "${pkgdir}/usr/bin/strata-inference-vision"
  install -Dm755 strata-inference "${pkgdir}/usr/bin/strata-inference"
  install -d "${app}/third_party/llama.cpp"
  cp -r "${upstream}/serve" "${upstream}/tools" "${app}/"
  cp -r "${srcdir}/llama.cpp/gguf-py" "${app}/third_party/llama.cpp/"
  find "${app}" -type d -name __pycache__ -prune -exec rm -rf {} +
  find "${app}" -type f -name 'test_*.py' -delete
  install -d "${pkgdir}/usr/share/strata-inference"
  install -m644 "${upstream}/data/draft_vocab.bin" "${upstream}/data/expert-profile.bin" \
    "${pkgdir}/usr/share/strata-inference/"
  install -Dm644 "${upstream}/LICENSE" "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
  install -Dm644 "${srcdir}/llama.cpp/LICENSE" \
    "${pkgdir}/usr/share/licenses/${pkgname}/llama.cpp-LICENSE"
  install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
  install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/packaging-LICENSE"
}
