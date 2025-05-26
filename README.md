# titration_bot

## 🚀 About

A package used to design and analyse titration experiments.<br> 
Titration experiments can be created and then their parameters evaluated. Once the experiment is conducted,
the data can be combined with the experiment in a single python data structure (DataFrame) for succinct analysis and plotting.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15112907.svg)](https://doi.org/10.5281/zenodo.15112907)

## 🔧 Install
It is recommended to build from within a virtual environment:<br> 
https://docs.python.org/3/library/venv.html

The package is pip installable (ssh recommended):
```shell
# ssh
pip install git+ssh://git@github.com/lucaAyt/titration_bot.git
```
To setup ssh keys see the following:<br>
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

For development installation, the following is recommended:
```shell
# For development purposes it is best to clone and then pip install as an editable.
git clone ssh://git@github.com/lucaAyt/titration_bot.git
cd titration_bot
pip install -e .
```

## 🚁 Usage


- For usage you will need to edit the `env_example` file after installation and save as `.env` in the same location.
    >Note: Above is only required if the `mfethuls` package is used to parse data.
- Consult the notebook ``notebooks\titration_usecase`` for an example.
- For developers, please work on a suitable branch and send a pull request.

## 📃 License

MIT

## Notes
This package is still under development and is in no way a production ready service.

