# HiLT (Human in the Loop Tools)

This repository contains the source code for HiLT, located in `src`, a number of example programs (both in the base folder and in `corpus`), and case studies partially reimplementing interface from prior published work (located in `case_studies`). To run, set up a Python virtual environment (we used `python -m venv path/to/venv` during development) and use `pip install -r requirements.txt` to install required libraries. Running the case studies will require also cloning the code repositories published by the authors of the relevant paper, and installing any needed requirements in the same virtual environment. Some futzing with `PYTHONPATH` and file paths may be needed.

Some documentation for HiLT's APIs is available [here](https://skberkeley.github.io/CNLDocs/#/).
