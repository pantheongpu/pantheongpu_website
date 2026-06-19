#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
export DEBIAN_FRONTEND=noninteractive

curl -fsSL \
  https://github.com/saqibkh/pantheongpu_website/releases/download/v1.0.13/pantheongpu_1.0.13_amd64.deb \
  -o /tmp/pantheongpu.deb
apt-get install -y --no-install-recommends /tmp/pantheongpu.deb

mkdir -p /root/.cache/pantheongpu/builds/stale
mkdir -p /opt/pantheongpu/cache/builds/stale
cat >/usr/local/bin/pantheon <<EOF
#!/usr/bin/env sh
exec /opt/pantheongpu/bin/pantheon "\$@"
EOF
chmod 0755 /usr/local/bin/pantheon

test -x /usr/bin/pantheon
test -d /opt/pantheongpu
test -d /root/.cache/pantheongpu

apt-get remove -y pantheongpu

! dpkg-query -W pantheongpu
! test -e /usr/bin/pantheon

# Runtime-created files and portable-install files are not owned by v1.0.13.
test -e /usr/local/bin/pantheon
test -d /opt/pantheongpu
test -d /root/.cache/pantheongpu

sh "${repo_root}/docs/uninstall.sh"

! test -e /usr/bin/pantheon
! test -e /usr/local/bin/pantheon
! test -e /opt/pantheongpu
! test -e /root/.cache/pantheongpu
