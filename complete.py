# Copyright (c) 2022, 2023 Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""Completer class and supporting classes."""

__all__ = [
    'CompletionError',
    'UnexpectedResponseError',
    'Supplier',
    'Completer',
]

from collections.abc import Callable
import functools
import random
import re
import textwrap
from typing import Any

from huggingface_hub.inference_api import InferenceApi

_PARA_BREAK = re.compile(r'\n{2,}')
"""Regular expression matching a paragraph break."""


class CompletionError(Exception):
    """An error in attempting to complete text with BLOOM."""


class UnexpectedResponseError(AssertionError):
    """An unexpected error completing text. Probably a bug."""


class Supplier:
    """As the value of a BLOOM parameter, is called instead of used."""

    __slots__ = ('_func',)

    __match_args__ = ('_func',)

    def __init__(self, func: Callable[[], Any]) -> None:
        self._func = func

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._func!r})'

    def __call__(self) -> Any:
        return self._func()


@functools.cache
def _get_inference_api() -> InferenceApi:
    """Create an InferenceApi object for BLOOM, using the HuggingFace token."""
    with open('.hf_token', encoding='utf-8') as file:
        api_token = file.read().strip()

    return InferenceApi(repo_id='bigscience/bloom', token=api_token)


def _normalize_paragraphs(text: str) -> str:
    """Remove any hard wrapping and separate paragraphs by single newlines."""
    pretty = _PARA_BREAK.split(text)
    raw = (para.strip().replace('\n', ' ') for para in pretty)
    return '\n'.join(raw)


def _prettify_paragraphs(text: str) -> str:
    """Add hard wrapping and separate paragraphs by blank lines."""
    raw = text.strip().split('\n')
    pretty = ('\n'.join(textwrap.wrap(graf)) for graf in raw)
    return '\n\n'.join(pretty)


class Completer:
    """High-level interface to Bloom completion."""

    __slots__ = ('_inference', '_text', '__dict__')

    def __init__(self, prompt: str, **parameters: Any) -> None:
        """Create a completer for the given prompt and optional parameters."""
        self._inference = _get_inference_api()
        self.text = _normalize_paragraphs(prompt)

        if any(name.startswith('_') for name in parameters):
            raise TypeError('cannot set parameter name with leading "_"')

        self._set_defaults()
        self.__dict__.update(parameters)

    def __str__(self) -> str:
        """Prettified version of the text stored so far."""
        return _prettify_paragraphs(self.text)

    @property
    def text(self) -> str:
        """The prompt plus any appended completions."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('prompt must be a string')
        if not value:
            raise ValueError('prompt must be nonempty')
        self._text = value

    def __call__(self) -> None:
        """Attempt to complete the stored text, and print all text so far."""
        self.complete()
        print(self)

    def complete(self) -> None:
        """Attempt to complete the stored text, but do not print anything."""
        match self._inference(inputs=self.text, params=self._build_params()):
            case [{'generated_text': completion}]:
                self._text = completion  # Whatever BLOOM returns, we accept.
            case {'error': [*errors]}:
                raise CompletionError(*errors)
            case other_response:
                raise UnexpectedResponseError(other_response)

    def _set_defaults(self) -> None:
        self.do_sample = True
        self.max_new_tokens = 250
        self.seed = Supplier(functools.partial(random.randrange, 2**64))
        self.temperature = 0.75

    def _build_params(self) -> dict[str, Any]:
        return {name: (value() if isinstance(value, Supplier) else value)
                for name, value in sorted(self.__dict__.items())}
