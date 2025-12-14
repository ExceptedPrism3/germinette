# 🌱 Germinette

**Germinette** is a modern, lightweight Python testing tool designed to automate the evaluation of 42 school Python projects. Inspired by tools like output-matching testers, Germinette helps you verify your exercises with robust checks, clear feedback, and a touch of style.

---

## 🚀 Key Features

- **Auto-Detection**: Automatically identifies which module to test based on your file structure.
- **Strict Testing**: Runs multiple test cases (standard inputs, edge cases, type checks) to ensure your code is solid.
- **Detailed Error Reporting**: 
    - Real-time "OK/KO" status.
    - Consolidated, rigorous error reports at the end.
    - Input context provided for every failure (know *exactly* what input broke your code).
- **Recursion & Depth Checks**: Detects infinite recursion or stack overflows.
- **Smart File Search**: Finds your files in the strictly correct module directories (e.g. `ex0`, `ex1`).
- **Rich Output**: Beautiful, color-coded terminal output using the `rich` library.

---

## 📦 Installation for 42 Students (Ubuntu/Mac)

Getting `germinette` running is easy, whether you're on a lab machine (Ubuntu) or Mac.

### 1. Requirements
- Python 3.10 or higher (Installed by default on 42 machines)

### 2. Setup & Install
Open your terminal and run these commands:

```bash
# 1. Clone the repository
git clone https://github.com/ExceptedPrism3/germinette.git
cd germinette

### 2. Installation
Run this command in the `germinette` folder:

```bash
pip install --user .
```

**That's it!** You can now open a new terminal anywhere and type:
```bash
germinette
```

> ⚠️ **Note**: If it says `command not found`, your local bin folder might not be in your PATH.
> *   **Mac**: Add `export PATH="$HOME/Library/Python/3.13/bin:$PATH"` to your shell config.
> *   **Linux/42**: Add `export PATH="$HOME/.local/bin:$PATH"` to your shell config.

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

## 🛠 Features
2.  Run strict tests on all available exercises.
3.  Show you a summary and a detailed error log if anything fails.

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
