#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

docker run --rm \
  --volume "${repo_root}:/workspace:ro" \
  ubuntu:24.04 \
  sh -euxc '
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y --no-install-recommends ca-certificates curl

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

    sh /workspace/docs/uninstall.sh

    ! dpkg-query -W pantheongpu
    ! test -e /usr/bin/pantheon
    ! test -e /usr/local/bin/pantheon
    ! test -e /opt/pantheongpu
    ! test -e /root/.cache/pantheongpu
  '
