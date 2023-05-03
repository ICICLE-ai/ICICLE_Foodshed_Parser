# Constrained Language Models Yield Few-Shot Semantic Parsers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

<img align="right" src="https://avatars2.githubusercontent.com/u/9585815?s=200&v=4" width="18%">

This repository contains tools and instructions for reproducing the experiments in the paper
[**Constrained Language Models Yield Few-Shot Semantic Parsers** (EMNLP 2021)](https://aclanthology.org/2021.emnlp-main.608/).
If you use any source code or data included in this toolkit in your work, please cite the following paper.
```bib
@inproceedings{ConstrainedLMSemanticParser2021,
    title = "Constrained Language Models Yield Few-Shot Semantic Parsers",
    author = "Shin, Richard and Lin, Christopher H. and Thomson, Sam and Chen, Charles and Roy, Subhro and Platanios,  Emmanouil Antonios and Pauls, Adam and Klein, Dan and Eisner, Jason and Van Durme, Benjamin",
    booktitle = "Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing",
    year = "2021",
    publisher = "Association for Computational Linguistics",
}
```

## Initial set-up
- Install Poetry: https://python-poetry.org/docs/#installation.
- Install Python 3.7, which is the version of Python that has been used for developing this repository.
- Install `pipx` so that we can install command-line dependencies: https://pypa.github.io/pipx/.

First, check that we are not unintentionally in a virtualenv.
Run `poetry env info`; under "Virtualenv", it should show `Path:           NA`.
If it displays the path to an existing virtualenv, deactivate it, for example by running `deactivate` or `conda deactivate`.

Then run the following to set up the package:
```
cd semantic_parsing_with_constrained_lm
poetry config virtualenvs.in-project true
poetry env use <path to python3.7>
poetry install
poetry shell
```

Before running any of the commands below, run `poetry shell` to activate the virtualenv where all packages have been installed. You can `exit` to deactivate the virtualenv.


## Running a command
To run this script, you first need to source and load the virtual environment through poetry:
source $HOME/.poetry/env
poetry shell


Afterwards you can run the script as follows:
bash runCompletePipeline.sh "Entery query here within quotations"

This will output a list of options which the user will have to select from. Currently output to output.json

<!-- From the orginal repository -->
## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
