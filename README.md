# 🔒 READI - Risk Evaluation and De-Identification

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Lint](https://github.com/IBM/READI/actions/workflows/lint.yml/badge.svg)](https://github.com/IBM/READI/actions/workflows/lint.yml)
[![Testing](https://github.com/IBM/READI/actions/workflows/testing.yml/badge.svg)](https://github.com/IBM/READI/actions/workflows/testing.yml)
[![Publish to PyPI](https://github.com/IBM/READI/actions/workflows/publish.yml/badge.svg)](https://github.com/IBM/READI/actions/workflows/publish.yml)
[![PyPI](https://img.shields.io/pypi/v/READI.svg)](https://pypi.org/project/readi-privacy/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **Privacy-preserving AI made simple** - A comprehensive toolkit for data privacy risk assessment and de-identification in Python-based ML pipelines.

READI augments the functionalities provided by [IBM Data Privacy Toolkit](https://github.com/IBM/data-privacy-toolkit), offering state-of-the-art capabilities for detecting Personal and Sensitive Information in unstructured documents. Built for modern compliance frameworks and AI model training workflows.

---

## ✨ Features

- 🎯 **Advanced PII Detection** - Identify personal and sensitive information across multiple data types
- 🔄 **Seamless Integration** - Low-effort integration with existing ML pipelines
- 📊 **Structured & Unstructured Data** - Support for both data formats
- 🌐 **REST API** - Easy-to-use HTTP interface for remote processing
- 🧪 **Extensible Framework** - Modular design for custom privacy requirements
- 📝 **Comprehensive Examples** - Jupyter notebooks with real-world use cases

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git with [git-lfs](https://git-lfs.com/) support (for large files >50 MB)
- [uv](https://docs.astral.sh/uv/) (recommended) - A fast Python package installer

### Installation

**Recommended: Using uv (10-100x faster)**
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install READI
uv pip install git+https://github.com/IBM/READI.git
```

**Standard Installation with pip:**
```bash
pip install git+https://github.com/IBM/READI.git
```

**Clone Repository:**
```bash
git clone https://github.com/IBM/READI.git
cd READI

# With uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

---

## 💻 Development Setup

For contributors and developers:

**Recommended: Using uv**
```bash
# Install in editable mode with development dependencies
uv pip install -e .
uv pip install -r requirements-dev.txt

# Set up pre-commit hooks (recommended)
pre-commit install
```

**Alternative: Using pip**
```bash
# Install in editable mode with development dependencies
pip install -e .
pip install -r requirements-dev.txt

# Set up pre-commit hooks (recommended)
pre-commit install
```

This installs the project in [editable mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) along with development tools (pytest, ruff, bandit, etc.).

> 💡 **Tip**: Using `uv` provides significantly faster dependency resolution and installation compared to traditional `pip`.

---

## 🌐 REST API Usage

READI provides a simple REST API for remote processing.

### Setup

```bash
# Install with REST API support
pip install -e '.[rest]'

# Start the server
uvicorn risk_assessment.entry_points.rest.api:app
```

### Example Request

```bash
curl -H 'Content-Type: application/json' \
     http://localhost:8000/detect_phi \
     --data-raw '{"text":"My text with email: john@gmail.com"}'
```

The API will be available at `http://localhost:8000` with interactive documentation at `/docs`.

---

## 📚 Examples & Tutorials

Explore our comprehensive Jupyter notebooks in the [`notebooks/`](./notebooks) directory:

| Notebook | Description |
|----------|-------------|
| [**Unstructured Data Classification**](https://github.com/IBM/READI/blob/main/notebooks/example-unstructured-data-classification.ipynb) | General overview of READI API for free-text processing |
| [**Structured Data Classification**](https://github.com/IBM/READI/blob/main/notebooks/example-structured-data-classification.ipynb) | Working with tabular and structured datasets |

---

## 📖 Documentation

For detailed documentation, API references, and advanced usage patterns, please visit our [documentation portal](https://github.com/IBM/READI/docs) *(coming soon)*.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Development workflow

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 📌 How to Cite

If you use READI in academic work, please cite the most relevant publication from the references below. A general citation entry is:

```bibtex
@software{readi_ibm,
  title        = {READI: Risk Evaluation and De-Identification},
  author       = {Stefano Braghin and Liubov Nedoshivina and Anisa Halimi and Naoise Holohan and Kieran Fraser},
  year         = {2026},
  url          = {https://github.com/IBM/READI}
}
```

When your usage specifically relates to unstructured document de-identification, prefer citing:

```bibtex
@article{nedoshivina2024pragmatic,
  title   = {Pragmatic De-Identification of Cross-Domain Unstructured Documents: A Utility-Preserving Approach with Relation Extraction Filtering},
  author  = {Liubov Nedoshivina and Anisa Halimi and Joa Bettencourt-Silva and Stefano Braghin},
  journal = {AMIA Summits on Translational Science Proceedings},
  volume  = {2024},
  pages   = {85},
  year    = {2024}
}
```

---

## 📚 Academic References

READI is built on years of privacy research. Key publications:

1. **Nedoshivina, L., Halimi, A., Bettencourt-Silva, J., & Braghin, S.** (2024). *Pragmatic De-Identification of Cross-Domain Unstructured Documents: A Utility-Preserving Approach with Relation Extraction Filtering.* AMIA Summits on Translational Science Proceedings, 2024, 85.

2. **Pachilakis, M., Antonatos, S., Levacher, K., & Braghin, S.** (2020). *PrivLeAD: Privacy Leakage Detection on the Web.* Intelligent Systems and Applications. IntelliSys 2020. Advances in Intelligent Systems and Computing, vol 1250. Springer, Cham. [DOI: 10.1007/978-3-030-55180-3_32](https://doi.org/10.1007/978-3-030-55180-3_32)

3. **Braghin, S., Bettencourt-Silva, J. H., Levacher, K., & Antonatos, S.** (2019). *An Extensible De-Identification Framework for Privacy Protection of Unstructured Health Information: Creating Sustainable Privacy Infrastructures.* MEDINFO 2019: Health and Wellbeing e-Networks for All (pp. 1140-1144). IOS Press. [DOI: 10.3233/SHTI190404](https://doi.org/10.3233/SHTI190404)

4. **Antonatos, S., Braghin, S., Holohan, N., Gkoufas, Y., & Mac Aonghusa, P.** (2018). *PRIMA: An End-to-End Framework for Privacy at Scale.* 2018 IEEE 34th International Conference on Data Engineering (ICDE), pp. 1531-1542. [DOI: 10.1109/ICDE.2018.00171](https://doi.org/10.1109/ICDE.2018.00171)

5. **Gkoulalas-Divanis, A., & Braghin, S.** (2016). *IPV: A system for identifying privacy vulnerabilities in datasets.* IBM Journal of Research and Development, vol. 60, no. 4, pp. 14:1-14:10. [DOI: 10.1147/JRD.2016.2576818](https://doi.org/10.1147/JRD.2016.2576818)

6. **Gkoulalas-Divanis, A., Braghin, S., & Antonatos, S.** (2016). *FPVI: A scalable method for discovering privacy vulnerabilities in microdata.* 2016 IEEE International Smart Cities Conference (ISC2), pp. 1-8. [DOI: 10.1109/ISC2.2016.7580849](https://doi.org/10.1109/ISC2.2016.7580849)

7. **Gkoulalas-Divanis, A., & Braghin, S.** (2015). *Efficient algorithms for identifying privacy vulnerabilities.* 2015 IEEE First International Smart Cities Conference (ISC2), pp. 1-8. [DOI: 10.1109/ISC2.2015.7366170](https://doi.org/10.1109/ISC2.2015.7366170)

---

## 🙏 Acknowledgment

This project is partly supported by the Innovative Health Initiative Joint Undertaking (IHI JU) under grant agreement No. 101172997 – SEARCH.

---

## 💬 Support & Community

- 🐛 **Issues**: [GitHub Issues](https://github.com/IBM/READI/issues)
- 💡 **Discussions**: [GitHub Discussions](https://github.com/IBM/READI/discussions)
- 📧 **Contact**: For enterprise support, please contact the IBM Research team

---

<div align="center">

**Built with ❤️ by IBM Research**

[Documentation](https://github.com/IBM/READI) • [Examples](./notebooks) • [Contributing](CONTRIBUTING.md) • [License](LICENSE)

</div>
