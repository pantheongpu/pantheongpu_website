Name:           pantheon-gpu
Version:        1.2.4
Release:        1%{?dist}
Summary:        GPU stress testing and diagnostics for NVIDIA CUDA and AMD ROCm

License:        Apache-2.0
URL:            https://pantheongpu.com
Source0:        %{pypi_source pantheon_gpu}
BuildArch:      noarch

BuildRequires:  python3-devel

# %%check runs the CPU "mock" backend, which compiles the workloads with the
# same C++ toolchain a real run uses.
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  python3-numpy
BuildRequires:  python3-pandas

# Runtime dependencies are declared by hand, so the dependency generator is
# off. Upstream metadata lists nvidia-ml-py, which Fedora does not package;
# the tool imports it inside try/except and reports telemetry as unavailable
# without it, so it is left out here rather than made a hard requirement.
# pandas and numpy are imported at module scope. gcc-c++ and make are runtime
# requirements because the package ships kernel sources, not binaries: each
# workload is compiled on first run for the GPU that is present.
%{?python_disable_dependency_generator}
Requires:       python3
Requires:       python3-pandas
Requires:       python3-numpy
Requires:       gcc-c++
Requires:       make
Recommends:     python3-psutil
Suggests:       python3-openpyxl

%description
Pantheon runs targeted stress and diagnostic workloads against NVIDIA and AMD
GPUs: power viruses, memory diagnostics (march tests, disturb and retention
patterns), interconnect and AI-shaped workloads, with RAS/ECC snapshots
collected on every run. Kernels compile on first run into a per-user cache,
which needs the CUDA or ROCm toolkit installed separately for real hardware;
the mock backend exercises the tooling with no GPU at all.

%prep
%autosetup -n pantheon_gpu-%{version}

%generate_buildrequires
# -R: runtime dependencies are declared by hand above; without it this stage
# demands python3dist(nvidia-ml-py), which no Fedora repository carries.
%pyproject_buildrequires -R

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l pantheon_gpu
# setuptools writes the same launcher twice; keep one and link the other.
ln -sf pantheon %{buildroot}%{_bindir}/pantheon-gpu

%check
# Fedora's default build flags (hardening, LTO) are meant for the package's own
# compiled code; here they would be handed to the workloads' nvcc/hipcc/g++
# invocations, whose plugins are not installed at run time.
unset CFLAGS CXXFLAGS LDFLAGS
export HOME=%{_builddir}/home
mkdir -p "$HOME"
export PYTHONPATH=%{buildroot}%{python3_sitelib}
cd "$HOME"
test "$(%{buildroot}%{_bindir}/pantheon --version | awk '{print $NF}')" = "%{version}"
%{buildroot}%{_bindir}/pantheon --platform mock --test baseline_metrics --duration 5 --mem 5

%files -f %{pyproject_files}
%doc README.md
%{_bindir}/pantheon
%{_bindir}/pantheon-gpu

%changelog
* Sun Oct 18 2026 Saqib Khan <saqibkhan@utexas.edu> - 1.2.4-1
- Update to 1.2.4 (choose the default GEMM format from the part: no BF16
  default below Ampere)
- Add %%check, running the CPU mock backend
