# Agents Documentation for AutoTradeSpot

## Project Overview
- **Name**: AutoTradeSpot
- **Description**: A web application for users to post car listings for sale.
- **Technologies Used**: Django, HTMX, React, TailwindCss, Docker.

## Essential Commands
### Build Commands
- **Frontend**: Run `npm run build` for production build.
- **Backend**: Execute `python manage.py collectstatic` to gather static files.

### Test Commands
- **Run Tests**: Use `pytest` for executing tests defined in the directory.
- **Coverage**: Tests report coverage by default, analyzed via the command line.

## Code Organization
- **Main Components**:
  - `portfolios/`: Contains main application logic.
  - `tests/`: Holds test files and configurations.
  - `config/`: Configuration settings for Django.
- **Frontend**: React components are located under the `portfolios/` directory.

## Naming Conventions & Style Patterns
- Follow **PEP 8** for Python style guide.
- Frontend style follows **BEM** (Block Element Modifier) methodology in CSS.

## Testing Approach
- Unit tests should be placed in the `tests/` folder, following naming conventions like `test_*.py`.
- Coverage is handled by `pytest` with specific configurations in `pyproject.toml`.

## Important Gotchas
- Ensure to have a **virtual environment** activated when running Django scripts.
- **Static files** need to be collected via `manage.py` before serving.
- Database migrations need proper attention when changing models, run `python manage.py makemigrations` followed by `migrate`.

## Existing Rules & Context
- No existing specific agent rules found. The `README.md` contains necessary project insights and further details about the applications.

## Future Documentation Enhancements
- Monitor changes in the directory structure, add notes regarding significant patterns or potential issues as they arise.