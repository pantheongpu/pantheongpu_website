#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Pantheon uninstall must run as root. Try: curl -fsSL https://pantheongpu.com/uninstall.sh | sudo sh" >&2
    exit 1
fi

package_installed=false
if command -v dpkg-query >/dev/null 2>&1 &&
    dpkg-query -W -f='${db:Status-Status}\n' pantheongpu 2>/dev/null |
        grep -qx 'installed'; then
    package_installed=true
fi

if [ "${package_installed}" = true ]; then
    if command -v apt-get >/dev/null 2>&1; then
        DEBIAN_FRONTEND=noninteractive apt-get purge -y pantheongpu ||
            dpkg --purge pantheongpu
    else
        dpkg --purge pantheongpu
    fi
fi

# The portable installer creates this launcher. Only remove it when it points
# at Pantheon's default installation so an unrelated command is never deleted.
if [ -f /usr/local/bin/pantheon ] &&
    grep -q '/opt/pantheongpu/bin/pantheon' /usr/local/bin/pantheon; then
    rm -f /usr/local/bin/pantheon
fi

# Remove files created at runtime, which are not tracked by the Debian package.
rm -rf /opt/pantheongpu

uninstall_user=${SUDO_USER:-}
if [ -n "${PANTHEON_UNINSTALL_HOME:-}" ]; then
    uninstall_home=${PANTHEON_UNINSTALL_HOME}
elif [ -n "${uninstall_user}" ] && [ "${uninstall_user}" != root ] &&
    command -v getent >/dev/null 2>&1; then
    uninstall_home=$(getent passwd "${uninstall_user}" | cut -d: -f6)
else
    uninstall_home=${HOME:-/root}
fi

cache_home=${PANTHEON_CACHE_HOME:-"${uninstall_home}/.cache"}
rm -rf "${cache_home}/pantheongpu"

echo "Pantheon GPU and the current user's workload cache were removed."
