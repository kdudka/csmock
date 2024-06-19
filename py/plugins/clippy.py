import os

import csmock.common.util

RUN_CLIPPY_CONVERT = "/usr/share/csmock/scripts/convert-clippy.py"
CLIPPY_OUTPUT = "/builddir/clippy-output.txt"
CLIPPY_INJECT_SCRIPT = "/usr/share/csmock/scripts/inject-clippy.sh"

class PluginProps:
    def __init__(self):
        self.description = "Rust source code analyzer which looks for programming errors."


class Plugin:
    def __init__(self):
        self.enabled = False

    def get_props(self):
        return PluginProps()

    def enable(self):
        self.enabled = True

    def init_parser(self, parser):
        return

    def handle_args(self, parser, args, props):
        if not self.enabled:
            return

        def inject_clippy_hook(results, mock):
            return mock.exec_chroot_cmd(CLIPPY_INJECT_SCRIPT)
        props.post_depinst_hooks += [inject_clippy_hook]

        props.install_pkgs += ["clippy"]
        props.copy_out_files += [CLIPPY_OUTPUT]

        csmock.common.util.install_default_toolver_hook(props, "clippy")

        def convert_hook(results):
            src = f"{results.dbgdir_raw}{CLIPPY_OUTPUT}"
            if not os.path.exists(src):
                # if `cargo build` was not executed during the scan, there are no results to process
                return 0

            dst = f"{results.dbgdir_uni}/clippy-capture.err"
            cmd = f'set -o pipefail; {RUN_CLIPPY_CONVERT} < {src} | csgrep --remove-duplicates > {dst}'
            return results.exec_cmd(cmd, shell=True)

        props.post_process_hooks += [convert_hook]
