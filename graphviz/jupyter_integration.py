"""Display rendered graph as SVG in Jupyter Notebooks and QtConsole."""

import typing

__all__ = ['JUPYTER_FORMATS', 'DEFAULT_JUPYTER_FORMAT',
           'get_jupyter_format_mimetype',
           'JupyterIntegration']

_IMAGE_JPEG = 'image/jpeg'

JUPYTER_FORMATS = {'jpeg': _IMAGE_JPEG,
                   'jpg': _IMAGE_JPEG,
                   'png': 'image/png',
                   'svg': 'image/svg+xml'}

DEFAULT_JUPYTER_FORMAT = 'svg'

MIME_TYPES = {'image/jpeg': '_repr_image_jpeg',
              'image/png': '_repr_image_png',
              'image/svg+xml': '_repr_image_svg_xml'}


def get_jupyter_format_mimetype(jupyter_format: str) -> str:
    try:
        return JUPYTER_FORMATS[jupyter_format]
    except KeyError:
        raise ValueError(f'unknown jupyter_format: {jupyter_format!r}')


def get_jupyter_mimetype_format(mimetype: str) -> typing.Optional[str]:
    if mimetype not in MIME_TYPES:
        raise ValueError(r'unsupported mimetype: {mimetype!r}')
    for format, jupyter_mimetype in JUPYTER_FORMATS.items():
        if jupyter_mimetype == mimetype:
            return format


class JupyterIntegration:
    """Display rendered graph as SVG in Jupyter Notebooks and QtConsole."""

    _jupyter_mimetype = get_jupyter_format_mimetype(DEFAULT_JUPYTER_FORMAT)

    def _repr_mimebundle_(self,
                          include: typing.Optional[typing.Iterable[str]] = None,
                          exclude: typing.Optional[typing.Iterable[str]] = None,
                          **_) -> typing.Dict[str, typing.Union[bytes, str]]:
        """Return the rendered graph as mimebundle.

        >>> doctest_mark_exe()
        >>> import graphviz
        >>> dot = graphviz.Graph()
        >>> dot._repr_mimebundle_()  # doctest: +ELLIPSIS
        {'image/svg+xml': '<?xml version=...
        >>> dot._repr_mimebundle_(include=['image/png'])  # doctest: +ELLIPSIS
        {'image/png': b'\x89PNG...
        >>> dot._repr_mimebundle_(include=[])
        {}
        >>> dot._repr_mimebundle_(include=['image/svg+xml', 'image/jpeg'],
        ...                       exclude=['image/svg+xml'])  # doctest: +ELLIPSIS
        {'image/jpeg': b'\xff...

        https://ipython.readthedocs.io/en/stable/config/integrating.html#MyObject._repr_mimebundle
        https://nbviewer.org/github/ipython/ipython/blob/master/examples/IPython%20Kernel/Custom%20Display%20Logic.ipynb
        """
        include = set(include) if include is not None else {self._jupyter_mimetype}
        include -= set(exclude or [])
        return {mimetype: getattr(self, method_name)()
                for mimetype, method_name in MIME_TYPES.items()
                if mimetype in include and hasattr(self, method_name)}

    def _repr_image_jpeg(self) -> bytes:
        """Return the rendered graph as JPEG bytes."""
        return self.pipe(format='jpeg')

    def _repr_image_png(self) -> bytes:
        """Return the rendered graph as PNG bytes."""
        return self.pipe(format='png')

    def _repr_image_svg_xml(self) -> str:
        """Return the rendered graph as SVG string."""
        return self.pipe(format='svg', encoding=self._encoding)
