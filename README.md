# 🌱 Germinette

**Germinette** is a modern, lightweight Python testing tool designed to automate the evaluation of 42 school Python projects. Inspired by tools like output-matching testers, Germinette helps you verify your exercises with robust checks, clear feedback, and a touch of style.

---

## 🚀 Key Features

- **Auto-Detection**: Automatically identifies which module to test based on your file structure.
- **Strict Testing**: 
    - **Logic**: Runs multiple test cases (standard inputs, edge cases, type checks).
    - **Style (New)**: Enforces `flake8` compliance. If style fails, testing stops immediately ("Single KO Policy") to prevent confusion.
    - **Execution**: Verifies that your scripts run exactly as shown in the subject PDF examples.
    - **Docstrings**: Enforces docstrings on all classes and methods (Strict policy for Module 01).
- **Maintenance**:
    - **Auto-Cleanup**: Automatically wipes `__pycache__` directories after every run to keep your workspace pristine.
- **Detailed Error Reporting**: 
    - **Silent Checks**: Style checks run quietly.
    - **Final Report**: All errors (logic and style) are consolidated in a detailed report at the end.
    - **Context**: Input context provided for every failure (know *exactly* what input broke your code).
- **Global Updater**: `germinette -u` works from anywhere, automatically finding and updating your local Germinette repository.
- **Rich Output**: Beautiful, color-coded terminal output using the `rich` library.
- **Recursion & Depth Checks**: Detects infinite recursion or stack overflows.

## ✅ Supported Modules

| Module | Status | Features |
| :--- | :--- | :--- |
| **Module 00** | 🟢 Ready | Basic Python, Functions, I/O |
| **Module 01** | 🟢 Ready | Classes, Objects, Strict Docstrings |
| **Module 02** | 🟢 Ready | Error Handling, Custom Exceptions |
| **Module 03** | 🟢 Ready | `sys.argv`, Data Structures, Generators |
| **Module 04** | 🟢 Ready | File Manipulation, Context Managers, Stdin/out |
| **Module 05** | 🟢 Ready | Polymorphism, ABCs, Protocols |
| **Module 06** | 🟢 Ready | Advanced Imports, Package Structure, Circular Dependencies |
| **Module 07** | 🟢 Ready | Python's Magic, Decorators, Inner Functions |
| **Module 08** | 🟢 Ready | The Life of Data, Typing |
| **Module 09** | 🟢 Ready | The Validation, Decorators Pattern |
| **Module 10** | 🟢 Ready | Functional Power, Functools, Itertools |

---

## 📦 Installation for 42 Students (Ubuntu/Mac)

Getting `germinette` running is easy!

### 1. Requirements
- Python 3.10 or higher (Installed by default on 42 machines)

### 2. Setup & Install (One Command)
Open your terminal and run these commands:

```bash
# 1. Clone the repository
git clone https://github.com/ExceptedPrism3/germinette.git
cd germinette

# 2. Run the install script
./install.sh
```

**That's it!** The script will install Germinette and automatically configure your PATH (so you can run the command from anywhere).

### 🏠 For Managed Systems (Debian/Ubuntu/PEP 668)
If you encounter "externally-managed-environment" errors or prefer isolation, use:
```bash
./install.sh --home
```
This creates a local ecosystem (`.germinenv`) and symlinks the binary, keeping your system Python clean.

If installation fails, please [open an issue on GitHub](https://github.com/ExceptedPrism3/germinette/issues).

### 🔄 Updating
To update Germinette later, simply run this command from anywhere:
```bash
germinette -u
```
Germinette now remembers where you installed it, so it will automatically pull the latest changes and reinstall itself.

## 🗑️ Usage

Navigate to your exercise directory and run:
```bash
germinette
```

Or test a specific module/exercise:
```bash
germinette python_module_01
germinette -e "Exercise 2"
```

## ❌ Uninstalling

To remove Germinette completely:
```bash
./uninstall.sh
```
This will remove the package and clean up your configuration.

## 🚀 How to Use

### Basic Usage
Navigate to your project folder (where your `ex00`, `ex01` folders are) and run:

```bash
germinette
```
It will automatically detect which module you are working on (e.g., `python_module_00` or `python_module_01` etc...) and run the tests.

### Specific Module
If auto-detection is confused, or you want to be explicit:

```bash
germinette python_module_00
```
or
```bash
germinette python_module_01
```


### 📁 Project Structure Compliance

Different 42 projects have different strict naming conventions. **Germinette enforces the conventions specified in the subject PDF for each module.**

For **Module 00** and **Module 01**, the subject explicitly requires:

```text
python_module_00/
├── ex0/
│   └── ft_hello_garden.py
...
```

- **Use `ex0`, `ex1`, etc.** (Not `ex00`).
- **Always check your subject PDF!** If a future module requires `ex00`, Germinette will be updated to enforce *that* specific rule for that module.

## 🐛 Bug Reporting

Found a bug? The tester saying "KO" when it should be "OK"?
1.  **Check the Subject**: 42 subjects are tricky. Double-check the PDF requirements.
2.  **Open an Issue**: Please verify your folder structure key-by-key, then open an issue on this repository with:
    -   Your OS (Mac/Ubuntu)
    -   The module and exercise
    -   The error output

## 🤝 Contributing

We welcome contributions! If you want to add support for missing modules, or fix a bug:

👉 **Read the [Contribution Guide](CONTRIBUTING.md) for step-by-step instructions!**

1.  Fork the repo.
2.  Create a branch for your feature (`git checkout -b feature/project_name`).
3.  Implement the tester following the guide.
4.  Submit a Pull Request!



---

## 📂 Project Structure

Your project should look something like this for auto-detection to work best:

```
python_module_00/
├── ex0/
│   └── ft_hello_garden.py
├── ex1/
│   └── ft_plot_area.py
...
```

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Made with 🐍 and ☕ by <b>42 Heilbronn Students</b> 🇩🇪</sub>
</div>
