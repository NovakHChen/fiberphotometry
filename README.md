# Fiberphotometry Analysis Routies

Basic routines for reading, visualizing and analyzing fiberphotometry recordings.

## Local Installation via Anaconda Using a CLI tools (e.g. Anaconda Prompt)

1. install Anaconda.

1. clone the repository:

   ```bash
   git clone https://github.com/GergelyTuri/fiberphotometry.git
   ```

   Alternatively, you can download only the `environment.yaml` file.

1. change directories

   ```bash
   cd fiberphotometry
   ```

1. Create a new environment by running the following lines in the anaconda terminal

   ```bash
   conda env create -f environment.yaml
   ```

1. activte the environment:

   ```bash
   conda activate fiber-photometry-analysis
   ```

1. finally:

   ```bash
   pip install .
   ```

   or if you want to install the package in editable mode:

   ```bash
   pip install -e .
   ```

## Local installation via pip (some sort of environment is higly recommended)

1. clone the repository:

   ```bash
   git clone https://github.com/GergelyTuri/fiberphotometry.git
   ```

1. change directories

   ```bash
   cd fiberphotometry
   ```

1. finally:

   ```bash
   pip install .
   ```

   or if you want to install the package in editable mode:

   ```bash
   pip install -e .
   ```

## Usage

1. The package can be used as a module in python scripts or jupyter notebooks. E.g.:

```python
import src.fiberphotometry as fp
```

## Installation in a Google Colab notebook

1. open a Colab notebook then type this in a code cell:

   ```bash
   !git clone https://github.com/GergelyTuri/fiberphotometry.git
   %cd fiberphotometry
   !pip install .
   ```

1. you may need to restart your runtime/session after this.

## Requirements

see `environment.yaml` or `pyproject.toml` files for the list of required packages.
