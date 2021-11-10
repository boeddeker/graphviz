"""Render DOT source files with Graphviz ``dot``."""

import os
import typing

from .. import parameters

from . import dot_command
from . import execute

__all__ = ['render']


def render(engine: str, format: str, filepath: typing.Union[os.PathLike, str],
           renderer: typing.Optional[str] = None,
           formatter: typing.Optional[str] = None,
           quiet: bool = False, *,
           rendered_filename: typing.Optional[str] = None) -> str:
    """Render file with Graphviz ``engine`` into ``format``,
        return result filename.

    Args:
        engine: Layout engine for rendering (``'dot'``, ``'neato'``, ...).
        format: Output format for rendering (``'pdf'``, ``'png'``, ...).
        filepath: Path to the DOT source file to render.
        renderer: Output renderer (``'cairo'``, ``'gd'``, ...).
        formatter: Output formatter (``'cairo'``, ``'gd'``, ...).
        quiet: Suppress ``stderr`` output from the layout subprocess.
        rendered_filename:

    Returns:
        The (possibly relative) path of the rendered file.

    Raises:
        ValueError: If ``engine``, ``format``, ``renderer``, or ``formatter``
            are not known.
        graphviz.RequiredArgumentError: If ``formatter`` is given
            but ``renderer`` is None.
        graphviz.ExecutableNotFound: If the Graphviz 'dot' executable
            is not found.
        subprocess.CalledProcessError: If the returncode (exit status)
            of the rendering 'dot' subprocess is non-zero.

    Note:
        The layout command is started from the directory of ``filepath``,
        so that references to external files
        (e.g. ``[image=images/camelot.png]``)
        can be given as paths relative to the DOT source file.
    """
    dirname, filename = os.path.split(filepath)
    del filepath

    if rendered_filename is not None:
        suffix_format = get_rendering_format(rendered_filename)
        if format is not None and format.lower() != suffix_format:
            raise ValueError(f'format {format!r} contradicts suffix'
                             f' from rendered_filename: {suffix_format!r}')
        format = suffix_format

    cmd = dot_command.command(engine, format,
                              renderer=renderer, formatter=formatter)

    if rendered_filename is not None:
        cmd.append(f'-o{rendered_filename}')
        rendered = rendered_filename
    else:
        cmd.append('-O')
        suffix_args = (formatter, renderer, format)
        suffix = '.'.join(a for a in suffix_args if a is not None)
        rendered = f'{filename}.{suffix}'

    cmd.append(filename)

    if dirname:
        cwd = dirname
        rendered = os.path.join(dirname, rendered)
    else:
        cwd = None

    execute.run_check(cmd, capture_output=True, cwd=cwd, quiet=quiet)
    return rendered


def get_rendering_format(rendered_filename: str) -> str:
    """Return rendering format derived from filename suffix."""
    _, suffix = os.path.splitext(rendered_filename)
    if not suffix:
        raise ValueError('cannot infer rendering format from rendered_filename'
                         f' without suffix: {rendered_filename}')

    assert suffix.startswith('.')
    format = suffix[1:].lower()

    try:
        parameters.verfify_format(format)
    except ValueError as e:
        raise ValueError('cannot infer rendering format from rendered_filename'
                         f' suffix {rendered_filename!r}')
    return format
