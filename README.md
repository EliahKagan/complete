<!-- SPDX-License-Identifier: 0BSD -->

# complete - Text generation with BLOOM in Jupyter notebooks

This repository provides a `Completer` class for helping with BLOOM completions
from Python. It is specifically oriented toward beng used from a Jupyter
notebook in story writing (fiction generation), though it doesn't have to be
used that way.

## License

[0BSD](https://spdx.org/licenses/0BSD.html). See [**`LICENSE`**]().

## Why?

The [inference widget](https://huggingface.co/docs/hub/models-widgets) on the
[**BLOOM** HuggingFace page](https://huggingface.co/bigscience/bloom) is good
for many purposes and a great way to get started. It does not offer access to
most parameters: you can choose between *greedy* and *sampling*, but you cannot
set parameters like *temperature*, *top_p*, *top_k*, and *max_new_tokens*.

It is useful to adjust these interactively, especially in story-writing
(fiction generation). [Gradio
Spaces](https://huggingface.co/docs/hub/spaces-sdks-gradio) can be used to make
web-based interfaces that customize parameters of your choice and provide
access to whichever ones you like. **This project is for the alternative
approach of using BLOOM from a Jupyter notebook.** It might be helpful if you
like working in a notebook, or if you want to experiment with parameters in
Python for some other reason, such as when experimenting toward developing some
more specific application.

## Setup

### Dependencies

You can install dependencies with `conda`:

```sh
conda env create
conda activate complete
```

Then open `complete.ipynb` in VS Code, JupyterLab, or whatever else you prefer
for interacting with Jupyter notebooks. Make sure to activate the `complete`
environment in that application, too.

### API Key

To use BLOOM, you'll need a [HuggingFace](https://huggingface.co/) account. The
`Completer` class expects to read a [HuggingFace
token](https://huggingface.co/docs/hub/security-tokens) from a file called
`.hf_token` in the current directory. (A HuggingFace token is an API key and
you should make sure *not* to commit it to source control. The `.gitignore`
file in this repository lists `.hf_token`, to help avoid that.)

## Usage

### Creating a `Completer`

The workflow I suggest is to first assign a `Completer` with your initial
prompt to a variable, by writing a statement like this in a code cell:

```python
bloom = Completer("""
Sometimes I marvel at how the sky contains no advertisements. Oh, sometimes
someone goes up in a little plane and skywrites a birthday greeting. But the
sky... you don't have to watch an ad to see it.

When people learn I fought in the war to free the sky, they say, "Thank you for
""", temperature=1.0, top_k=30)
```

The prompt is reformatted, removing single line breaks and separating
paragraphs by single newlines. If you want to use `Completer`'s defaults for
all parameters, it is fine to omit the keyword arguments and pass only the
prompt text.

### Using the `Completer` to complete text

Then call the `Completer` instance to retrieve a completion from the BLOOM model through the HuggingFace inference API and print it, formatted for readability:

```python
bloom()
```

All text is displayed, not just new text. **To ask for further completion, just
execute that cell again.** This replaces the old completion with the new one.
You can do this a number of times (until you exceed BLOOM's token limit).

If there is an error, you'll see the message from the HuggingFace API in the exception traceback. It is usually clear. If you want to print the accumulated text so far--for example, if you no longer see it because the last call gave an error--then simply print the `Completer` object rather than calling it:

```python
print(bloom)
```

### `Completer` objects are independent

Separate `Completer`s maintain separate state, so you can work on more than one
story (or other text) at the same time in the same notebook.

**See `complete.ipynb` for examples.**
