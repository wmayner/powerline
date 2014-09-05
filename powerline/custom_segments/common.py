# vim:fileencoding=utf-8:noet
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os

from powerline.segments import Segment, with_docstring
from powerline.theme import requires_segment_info
from powerline.lib.unicode import u


cpu_count = None


@requires_segment_info
class FullPathSegment(Segment):
    def argspecobjs(self):
        for obj in super(FullPathSegment, self).argspecobjs():
            yield obj
        yield 'get_shortened_path', self.get_shortened_path

    def omitted_args(self, name, method):
        if method is self.get_shortened_path:
            return (0, 1, 2)
        else:
            return super(FullPathSegment, self).omitted_args(name, method)

    def get_shortened_path(self, pl, segment_info, shorten_home=True, **kwargs):
        try:
            path = u(segment_info['getcwd']())
        except OSError as e:
            if e.errno == 2:
                # user most probably deleted the directory
                # this happens when removing files from Mercurial repos for #
                # example
                pl.warn('Current directory not found')
                return "[not found]"
            else:
                raise
        if shorten_home:
            home = segment_info['home']
            if home:
                home = u(home)
                if path.startswith(home):
                    path = '~' + path[len(home):]
        return path

    def __call__(self, pl, segment_info, dir_shorten_len=None, dir_limit_depth=None, use_path_separator=False, ellipsis=' … ', **kwargs):
        cwd = self.get_shortened_path(pl, segment_info, **kwargs)
        cwd_split = cwd.split(os.sep)

        # Cut out current directory
        cwd_split = cwd_split[:-1]

        cwd_split_len = len(cwd_split)
        cwd = [i[0:dir_shorten_len] if dir_shorten_len and i else i for i in cwd_split[:-1]] + [cwd_split[-1]]
        if dir_limit_depth and cwd_split_len > dir_limit_depth + 1:
            del(cwd[0:-dir_limit_depth])
            if ellipsis is not None:
                cwd.insert(0, ellipsis)
        ret = []
        if not cwd[0]:
            cwd[0] = '/'
        draw_inner_divider = not use_path_separator
        for part in cwd:
            if not part:
                continue
            if use_path_separator:
                part += os.sep
            ret.append({
                'contents': part,
                'divider_highlight_group': 'cwd:divider',
                'draw_inner_divider': draw_inner_divider,
            })
        if use_path_separator:
            ret[-1]['contents'] = ret[-1]['contents'][:-1]
            if len(ret) > 1 and ret[0]['contents'][0] == os.sep:
                ret[0]['contents'] = ret[0]['contents'][1:]
        return ret


full_path = with_docstring(FullPathSegment(),
'''Return the full path to the parent of the current working directory.

Returns a segment list to create a breadcrumb-like effect.

:param int dir_shorten_len:
    shorten parent directory names to this length (e.g.
    :file:`/long/path/to/powerline` → :file:`/l/p/t/powerline`)
:param int dir_limit_depth:
    limit directory depth to this number (e.g.
    :file:`/long/path/to/powerline` → :file:`⋯/to/powerline`)
:param bool use_path_separator:
    Use path separator in place of soft divider.
:param bool shorten_home:
    Shorten home directory to ``~``.
:param str ellipsis:
    Specifies what to use in place of omitted directories. Use None to not
    show this subsegment at all.

Divider highlight group used: ``cwd:divider``.

Highlight groups used: ``cwd:current_folder`` or ``cwd``. It is recommended to define all highlight groups.
''')
