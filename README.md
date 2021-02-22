# train-of-thought

[Ramaximization](https://ramaximization.ru) hackathon solution made by team "Свидетели ретротранспозонов" (task 1 - Wagon logistics)

Our best solution have produced the following results:

![Our solution's KPI table](KPI.png)

The full results, which were produced by `notebooks/basic_template.ipynb` script, can be found at `results` folder. `KPI.xlsx` file has LPI sheet filled by hand (screenshot shows its contents), the orders and empty moves can be found at `orders.csv` and `empty_moves.csv`.

## Project structure

- `data` contains prepared contest's dataset. xlsx are saved "as is", description is saved to txt file (to view it at github). It also contains prepared preprocessed tables extracted from `data/input_wagon.xlsx`.
- `notebooks` contains .ipynb files - exploratorials and experiments with data (and maybe some plots)
- `utils` contains method used in notebooks (common code to build graphs, work with data, etc.).
- `results` contains required tables with metrics - KPI, emptyMoves and orders.


## Installation
### Dependencies installation

Currently the code is written in python 3.7, some dependencies are provided at `requirements.txt` file. To install them, run
```
pip install -r requirements.txt
```
To run (or re-run) .ipynb-files, which are located at notebooks directory, you'll need to install jupyter notebook.

## HOWTO run code

During the hackathon we've used http://deepnote.com/ to edit data collaboratively. If you want to run provided .ipynb files locally, install [jupyter notebook](https://jupyter.org/install) and use it to open them.


