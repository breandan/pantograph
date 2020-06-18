# Pantograph

Pantograph is a framework for dynamic analysis of a Python interpreter. It allows users to reconstruct the source code and program dependence graph for code in Jupyter Notebook, Python shell, and Python scripts.

## Setup

To install Pantograph, run the following command (Python 3.5+ recommended):

```
git clone git@github.com:breandan/pantograph.git && cd pantograph && pip install .
```

## Usage

Arbitrary Python code can be recovered by passing variables to Pantograph like so:

```
z = 'Hello '
y = ' Pantograph '
a = z + y + '!'
p = PGraph(a, z, y)

```

For more details, check out the [Jupyter notebook](pantograph.ipynb).

PDG visualization is made possible by [pydot](https://github.com/pydot/pydot).

## References

* [Gast, Beniget!](https://github.com/serge-sans-paille/beniget)
* [Program Slicing](https://en.wikipedia.org/wiki/Program_slicing)
* [Dependence Analysis](https://en.wikipedia.org/wiki/Dependence_analysis)