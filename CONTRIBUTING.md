# Contributing to Obsidian Article Breakdown Agent

Thank you for considering contributing to the Obsidian Article Breakdown Agent! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

There are many ways to contribute to this project:

1. **Reporting Bugs**: If you find a bug, please create an issue with a detailed description of the problem, steps to reproduce it, and your environment details.

2. **Suggesting Enhancements**: Have an idea for a new feature or improvement? Create an issue with the "enhancement" label and describe your suggestion in detail.

3. **Code Contributions**: If you'd like to contribute code, please follow the process below.

## Development Process

1. **Fork the Repository**: Create your own fork of the repository.

2. **Create a Branch**: Create a branch for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**: Implement your changes, following the coding style and guidelines.

4. **Write Tests**: Add tests for your changes to ensure they work as expected.

5. **Run Tests**: Make sure all tests pass.
   ```bash
   poetry run pytest
   ```

6. **Commit Your Changes**: Write clear, concise commit messages.
   ```bash
   git commit -m "Add feature: your feature description"
   ```

7. **Push to Your Fork**: Push your changes to your fork.
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**: Submit a pull request from your fork to the main repository.

## Development Setup

1. **Clone the Repository**:
   ```bash
   git clone <your-fork-url>
   cd obsidian-article-breakdown
   ```

2. **Install Dependencies**:
   ```bash
   python setup.py
   ```

3. **Set Up Environment Variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

## Coding Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.
- Write docstrings for all functions, classes, and modules.
- Use type hints where appropriate.
- Keep functions and methods focused on a single responsibility.
- Write clear, descriptive variable and function names.

## Testing

- Write tests for all new features and bug fixes.
- Ensure all tests pass before submitting a pull request.
- Use pytest for testing.

## Documentation

- Update documentation for any changes to the API or functionality.
- Document new features thoroughly.
- Keep the README.md up to date.

## Pull Request Process

1. Ensure your code follows the coding guidelines.
2. Update documentation as necessary.
3. Make sure all tests pass.
4. Describe your changes in the pull request description.
5. Link any related issues in the pull request description.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have any questions or need help, please create an issue with the "question" label.

Thank you for your contributions!
