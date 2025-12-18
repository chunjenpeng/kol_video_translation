# Contributing to KOL Video Translation

Thank you for your interest in contributing to KOL Video Translation! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, versions, etc.)
- Screenshots if applicable

### Suggesting Features

Feature requests are welcome! Please create an issue with:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (if you have ideas)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** from `develop`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow the code style guidelines below
   - Add tests for new features
   - Update documentation as needed
4. **Commit your changes**
   - Use clear, descriptive commit messages
   - Follow conventional commits format: `type(scope): message`
5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request**
   - Describe what changes you made and why
   - Reference any related issues

## Code Style Guidelines

### Go (Backend)

- Follow standard Go formatting (`gofmt`)
- Use meaningful variable names
- Add comments for exported functions and types
- Keep functions small and focused
- Handle errors appropriately

```go
// Good
func processVideo(url string) (*Video, error) {
    if url == "" {
        return nil, fmt.Errorf("url cannot be empty")
    }
    // ...
}

// Bad
func pv(u string) (*Video, error) {
    // ...
}
```

### Python (Service)

- Follow PEP 8 style guide
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused on single responsibility
- Use meaningful variable names

```python
# Good
def transcribe_audio(audio_path: str, language: str) -> List[Dict]:
    """Transcribe audio file to text segments.
    
    Args:
        audio_path: Path to the audio file
        language: Language code for transcription
        
    Returns:
        List of transcription segments with timestamps
    """
    # ...

# Bad
def ta(ap, l):
    # ...
```

### JavaScript/React (Frontend)

- Use ES6+ features
- Follow Airbnb JavaScript Style Guide
- Use functional components with hooks
- Add PropTypes or TypeScript types
- Keep components small and reusable

```javascript
// Good
function VideoForm({ languages, onSubmit }) {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  // ...
}

// Bad
function VideoForm(props) {
  var url = '';
  // ...
}
```

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/chunjenpeng/kol_video_translation.git
   cd kol_video_translation
   ```

2. **Install dependencies**
   ```bash
   make setup-all
   ```

3. **Create environment files**
   ```bash
   cp backend/.env.example backend/.env
   cp python_service/.env.example python_service/.env
   cp frontend/.env.example frontend/.env
   ```

### Running Tests

```bash
# Run all tests
./test_integration.sh

# Run specific component tests
cd backend && go test ./...
cd python_service && pytest
cd frontend && npm test
```

### Running the Application

```bash
# Using Docker
make build
make run

# Or manually
make dev-backend    # Terminal 1
make dev-python     # Terminal 2
make dev-frontend   # Terminal 3
```

## Project Structure

Understanding the project structure helps in making targeted contributions:

```
kol_video_translation/
├── backend/           # Go API server
│   ├── handlers/     # HTTP request handlers
│   ├── middleware/   # Middleware (CORS, auth, etc.)
│   ├── models/       # Data models
│   └── services/     # Business logic
├── python_service/   # Python video processing
│   └── services/     # Processing modules
├── frontend/         # React web application
│   └── src/
│       └── components/  # React components
└── examples/         # Usage examples
```

## Testing Guidelines

- Write tests for new features
- Ensure existing tests pass
- Test edge cases and error conditions
- Add integration tests for new endpoints
- Update test documentation

### Test Categories

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows

## Documentation Guidelines

- Update README.md for significant changes
- Update API.md for API changes
- Update SETUP.md for setup process changes
- Add inline comments for complex logic
- Include examples for new features

## Commit Message Guidelines

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

**Examples:**
```
feat(backend): add rate limiting middleware

Implement rate limiting to prevent API abuse.
Uses token bucket algorithm with configurable limits.

Closes #123
```

```
fix(python): handle missing audio streams

Some videos don't have separate audio streams.
Fall back to extracting audio from video stream.

Fixes #456
```

## Code Review Process

1. All PRs require at least one approval
2. CI must pass (build, tests, linting)
3. Address reviewer feedback
4. Squash commits before merging (if requested)

## Getting Help

- Check existing documentation
- Search existing issues
- Ask in GitHub Discussions
- Join our community chat (if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- CHANGELOG.md
- README.md (for significant contributions)

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the `question` label
- Contact the maintainers
- Check the documentation

Thank you for contributing to KOL Video Translation! 🎉
