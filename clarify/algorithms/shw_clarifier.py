# SPDX-FileCopyrightText: 2026 Sihyun Ahn <sihyun.ahn@kaist.ac.kr>
# SPDX-FileCopyrightText: 2026 Kwon Hyukwon <gerbera3090@kaist.ac.kr>
#
# SPDX-License-Identifier: MIT

"""SHWClarifier.

Registration-only placeholder that returns a dummy Python implementation.
It makes no model calls or clarification requests and claims no performance results.

Team: SHW
Team Members: Sihyun Ahn (KAIST), Kwon Hyukwon (KAIST)
Main Contact: Kwon Hyukwon <gerbera3090@kaist.ac.kr>
"""

from clarify.baselines import ClarificationAlgorithmBase


class SHWClarifier(ClarificationAlgorithmBase):
    DEFAULT_CONFIG = {}

    def run(self, env, problem) -> str:
        # shortcut: registration stub only; replace before the final submission deadline.
        return f"def {problem['entry_point']}(*args, **kwargs):\n    return None\n"
