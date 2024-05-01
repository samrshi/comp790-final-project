# CSXL Visualizations

COMP 790 (Information Visualization) final project.

## Live Deployment

View live deployment here: https://samrshi.github.io/comp790-final-project/visualizations.html.

## Usage

### Building the book locally

If you'd like to develop and/or build the CSXL Visualizations book, you should:

1. Clone this repository
2. Run `pip install -r requirements.txt` (it is recommended you do this within a virtual environment)
3. (Optional) Edit the books source files located in the `csxl_visualizations/` directory
4. Run `jupyter-book clean csxl_visualizations/` to remove any existing builds
5. Run `jupyter-book build csxl_visualizations/`

A fully-rendered HTML version of the book will be built in `csxl_visualizations/_build/html/`.

### Deploying the book

To deploy the project, push to [github.com/samrshi/comp790-final-project](https://github.com/samrshi/comp790-final-project). This will trigger a GitHub Action that builds the book and deploys to GitHub Pages.
