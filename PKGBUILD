# Maintainer: jdhirst <jdhirst@hirstgroup.net>
pkgname=strata-inference-cuda
pkgver=0.1.39
pkgrel=1
pkgdesc='Strata CUDA inference engine and local API server for Qwen3.8-Flash-Next'
arch=('x86_64')
url='https://github.com/Niko1221/Strata'
license=('MIT')
depends=('cuda>=13' 'gcc-libs' 'glibc' 'python' 'python-numpy' 'python-jinja'
         'python-regex' 'python-yaml' 'python-tqdm' 'python-requests'
         'python-pillow' 'python-psutil')
makedepends=('cmake' 'ninja')
optdepends=('nvidia-utils: NVIDIA driver and GPU monitoring')
options=('!lto')
_llama_commit=3cf03257f219afbe7334045ff7c6a06ac68c627d
source=("strata-${pkgver}.tar.gz::https://github.com/Niko1221/Strata/archive/refs/tags/v${pkgver}.tar.gz"
        "llama.cpp-${_llama_commit}.tar.gz::https://github.com/ggml-org/llama.cpp/archive/${_llama_commit}.tar.gz"
        'strata-inference'
        'README.md'
        'LICENSE')
sha256sums=('e949372b264d21e7267636b7262db4dd70c65474fbfacaa3d25296c468622247'
            'c076d7534afa0e5d0ec2a0d425b11e791c16f3de0d727221aea071cef156a280'
            'bde9ce0fc12039f65e92586eff371b6ee38713690e9b14972444b67174bb23a1'
            '43af7d6ddbedddcc60ac9b05ed8ac8bdb6c62016c01a4f2981441631ab3c4562'
            '3aa11484d0b26858dc8e662f17e88ad03e4184d55b69f9b5e29e6feddd999ab5')

build() {
  # CachyOS may set -march=native. Keep redistributed binaries portable.
  export CFLAGS="${CFLAGS} -march=x86-64 -mtune=generic -ffile-prefix-map=${srcdir}=."
  export CXXFLAGS="${CXXFLAGS} -march=x86-64 -mtune=generic -ffile-prefix-map=${srcdir}=."
  cmake -S "Strata-${pkgver}" -B build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DSTRATA_ENABLE_CUDA=ON \
    -DSTRATA_PORTABLE=ON \
    -DSTRATA_BUILD_TESTS=OFF \
    -DSTRATA_MMQ_KQUANTS=ON \
    -DSTRATA_GGML_DIR="${srcdir}/llama.cpp-${_llama_commit}" \
    -DCMAKE_CUDA_COMPILER=/opt/cuda/bin/nvcc \
    -DCMAKE_CUDA_ARCHITECTURES="${STRATA_CUDA_ARCHITECTURES:-75;86;89;120}" \
    -DCMAKE_CUDA_RUNTIME_LIBRARY=Shared \
    -DCMAKE_BUILD_RPATH=/opt/cuda/lib64 \
    -DCMAKE_INSTALL_RPATH=/opt/cuda/lib64 \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON
  cmake --build build --target strata strata-device --parallel "${STRATA_BUILD_JOBS:-4}"
}

check() {
  python -c 'import numpy, jinja2, regex, yaml, tqdm, requests, PIL, psutil'
  python "${srcdir}/strata-inference" --help
  PYTHONPATH="${srcdir}/Strata-${pkgver}" \
    STRATA_GGUF_PY="${srcdir}/llama.cpp-${_llama_commit}/gguf-py" \
    python -m unittest discover -s "${srcdir}/Strata-${pkgver}/serve" -p 'test_runconfig.py'
}

package() {
  local upstream="${srcdir}/Strata-${pkgver}"
  local app="${pkgdir}/usr/lib/strata-inference"
  install -Dm755 build/strata "${pkgdir}/usr/bin/strata-inference-engine"
  install -Dm755 build/strata-device "${pkgdir}/usr/bin/strata-inference-device"
  install -Dm755 strata-inference "${pkgdir}/usr/bin/strata-inference"
  install -d "${app}/third_party/llama.cpp"
  cp -r "${upstream}/serve" "${upstream}/tools" "${app}/"
  cp -r "${srcdir}/llama.cpp-${_llama_commit}/gguf-py" "${app}/third_party/llama.cpp/"
  find "${app}" -type d -name __pycache__ -prune -exec rm -rf {} +
  find "${app}" -type f -name 'test_*.py' -delete
  install -d "${pkgdir}/usr/share/strata-inference"
  install -m644 "${upstream}/data/draft_vocab.bin" "${upstream}/data/expert-profile.bin" \
    "${pkgdir}/usr/share/strata-inference/"
  install -Dm644 "${upstream}/LICENSE" "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
  install -Dm644 "${srcdir}/llama.cpp-${_llama_commit}/LICENSE" \
    "${pkgdir}/usr/share/licenses/${pkgname}/llama.cpp-LICENSE"
  install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
  install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/packaging-LICENSE"
}
