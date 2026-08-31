Name:           pantheon-gpu
Version:        1.2.0
Release:        1%{?dist}
Summary:        GPU stress testing and diagnostics for NVIDIA CUDA and AMD ROCm

License:        Apache-2.0
URL:            https://pantheongpu.com
Source0:        https://pypi.org/packages/source/p/pantheon-gpu/pantheon_gpu-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

# Dependencies are declared by hand, the same call the Debian package makes:
# upstream metadata lists nvidia-ml-py, which Fedora does not package, and the
# tool degrades gracefully without it (telemetry only). pandas and numpy are
# imported at module scope. gcc-c++ and make are runtime requirements because
# the package carries kernel sources rather than prebuilt binaries: workloads
# compile for the GPU actually present on first run.
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
# -R: runtime deps are declared by hand above; without it this stage demands
# python3dist(nvidia-ml-py), which no Fedora repository carries.
%pyproject_buildrequires -R

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pantheon_gpu

%files -f %{pyproject_files}
%{_bindir}/pantheon
%{_bindir}/pantheon-gpu

%changelog
* Mon Aug 31 2026 Saqib Khan <saqibkhan@utexas.edu> - 1.2.0-1
- First COPR release, from the published PyPI sdist
